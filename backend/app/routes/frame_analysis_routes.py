from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import json
import time
from app.services.face_detect import detect_faces
from app.services.smile_detect import detect_smile
from app.services.age_predict import predict_age
from app.services.gender_detect import detect_gender
from app.services.smile_analytics import compute_smile_strength, classify_smile_level
from app.services.quality_analysis import measure_blur
from app.services.guidance_engine import generate_guidance

router = APIRouter()

# Cache for age/gender predictions (they don't change frequently)
face_cache = {}
cache_duration = 2.0  # Cache for 2 seconds

@router.websocket("/ws/analyze")
async def websocket_frame_analysis(websocket: WebSocket):
    """
    WebSocket endpoint for real-time frame analysis.
    Receives base64 encoded frames from browser webcam.
    Returns detection results without performing capture.
    Optimized for low latency.
    """
    await websocket.accept()
    print("✓ WebSocket connection established")
    
    frame_count = 0
    last_process_time = time.time()
    
    try:
        while True:
            # Receive base64 encoded frame from frontend
            data = await websocket.receive_text()
            frame_count += 1
            
            try:
                start_time = time.time()
                
                # Parse JSON message
                message = json.loads(data)
                frame_data = message.get("frame")
                
                if not frame_data:
                    await websocket.send_json({
                        "error": "No frame data received"
                    })
                    continue
                
                # Decode base64 frame
                if "," in frame_data:
                    frame_data = frame_data.split(",")[1]
                
                frame_bytes = base64.b64decode(frame_data)
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    await websocket.send_json({
                        "error": "Failed to decode frame"
                    })
                    continue
                
                # Resize frame for faster processing (reduce to 50% size)
                height, width = frame.shape[:2]
                frame_small = cv2.resize(frame, (width // 2, height // 2))
                
                # Run face detection on smaller frame
                faces = detect_faces(frame_small)
                
                # Scale face coordinates back to original size
                for face in faces:
                    x, y, w, h = face["bbox"]
                    face["bbox"] = (x * 2, y * 2, w * 2, h * 2)
                
                face_results = []
                all_smiling = False
                smile_counters = {}
                current_time = time.time()
                
                if len(faces) > 0:
                    all_smiling = True
                    
                    for face in faces:
                        face_id = face["id"]
                        x, y, w, h = face["bbox"]
                        
                        # Extract face from original frame for better quality
                        face_bgr = frame[y:y+h, x:x+w]
                        face_gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
                        
                        # ALWAYS detect smile (this is critical for real-time feedback)
                        smile_detected = detect_smile(face_gray)
                        smile_counters[face_id] = 1 if smile_detected else 0
                        
                        if not smile_detected:
                            all_smiling = False
                        
                        # Check cache for age/gender (update every 2 seconds)
                        cache_key = f"face_{face_id}"
                        if cache_key in face_cache:
                            cached_data = face_cache[cache_key]
                            if current_time - cached_data["timestamp"] < cache_duration:
                                # Use cached values
                                age_range = cached_data["age_range"]
                                gender = cached_data["gender"]
                                smile_strength = cached_data["smile_strength"]
                                smile_level = cached_data["smile_level"]
                            else:
                                # Cache expired, recompute
                                age_range, _ = predict_age(face_bgr)
                                gender = detect_gender(face_bgr)
                                smile_strength = compute_smile_strength(face_bgr)
                                smile_level = classify_smile_level(smile_strength)
                                
                                face_cache[cache_key] = {
                                    "age_range": age_range,
                                    "gender": gender,
                                    "smile_strength": smile_strength,
                                    "smile_level": smile_level,
                                    "timestamp": current_time
                                }
                        else:
                            # First time seeing this face
                            age_range, _ = predict_age(face_bgr)
                            gender = detect_gender(face_bgr)
                            smile_strength = compute_smile_strength(face_bgr)
                            smile_level = classify_smile_level(smile_strength)
                            
                            face_cache[cache_key] = {
                                "age_range": age_range,
                                "gender": gender,
                                "smile_strength": smile_strength,
                                "smile_level": smile_level,
                                "timestamp": current_time
                            }
                        
                        face_results.append({
                            "face_id": face_id,
                            "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                            "age_range": age_range,
                            "gender": gender,
                            "smile_detected": smile_detected,
                            "smile_strength": float(smile_strength),
                            "smile_level": smile_level
                        })
                
                # Generate guidance message (use smaller frame for speed)
                blur_score = measure_blur(frame_small)
                guidance = generate_guidance(frame_small, faces, blur_score, smile_counters)
                
                # Clean up old cache entries (older than 5 seconds)
                face_cache_keys = list(face_cache.keys())
                for key in face_cache_keys:
                    if current_time - face_cache[key]["timestamp"] > 5.0:
                        del face_cache[key]
                
                processing_time = (time.time() - start_time) * 1000  # Convert to ms
                
                if frame_count % 10 == 0:
                    print(f"✓ Frame {frame_count}: {len(faces)} face(s), all_smiling={all_smiling}, processing={processing_time:.1f}ms")
                
                # Send results back to frontend
                await websocket.send_json({
                    "faces": face_results,
                    "all_smiling": all_smiling,
                    "face_count": len(faces),
                    "guidance": guidance,
                    "processing_time_ms": round(processing_time, 1)
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                print(f"Frame analysis error: {e}")
                import traceback
                traceback.print_exc()
                await websocket.send_json({
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        print(f"✓ WebSocket connection closed (processed {frame_count} frames)")
        face_cache.clear()
    except Exception as e:
        print(f"WebSocket error: {e}")
        face_cache.clear()

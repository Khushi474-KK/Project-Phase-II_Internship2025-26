import cv2
import time
import os
from app.services.face_detect import detect_faces
from app.services.smile_detect import detect_smile
from app.services.age_predict import predict_age
from app.services.gender_detect import detect_gender
from app.services.quality_analysis import measure_blur
from app.services.caption_engine import generate_caption
from app.services.guidance_engine import generate_guidance
from app.services.smile_analytics import compute_smile_strength, classify_smile_level
# New portrait intelligence imports
from app.services.emotion_engine import compute_emotional_state
from app.services.mood_recommendation_engine import get_recommendation
from app.services.portrait_analytics_engine import analyze_portrait, generate_score_explanation
from app.services.session_ranking_engine import get_session_engine


# Preserve original constants
FPS = 10
FRAME_DELAY = 1 / FPS
SMILE_THRESHOLD = 7
AGE_UPDATE_INTERVAL = 2


def capture_photo(user_id: int = None, db_session = None, login_session_id: str = None, user = None):
    """
    Capture photo using live camera feed with face detection.
    Preserves original Flask logic exactly.
    Saves to user-based storage structure.
    
    Args:
        user_id: Authenticated user ID for storage organization
        db_session: Database session for filtering liked songs
        login_session_id: Login session ID (e.g., "session_1", "session_2")
        user: User object for accessing preferences (preferred_market, preferred_music_language)
    
    Returns:
        tuple: (raw_frame, face_metadata_list, quality_score, caption, image_path)
               or (None, None, None, None, None) if capture failed
    """
    video_stream = cv2.VideoCapture(0)

    smile_counter = {}
    age_cache = {}
    gender_cache = {}
    smile_strength_cache = {}
    last_age_update = {}

    cv2.namedWindow("Smart Camera", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Smart Camera", cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow("Smart Camera", 900, 650)
    cv2.moveWindow("Smart Camera", 300, 120)

    while True:
        start_time = time.time()

        frame_available, frame = video_stream.read()
        if not frame_available:
            break

        raw_frame = frame.copy()
        faces = detect_faces(frame)

        if len(faces) == 0:
            smile_counter.clear()
            age_cache.clear()
            gender_cache.clear()
            smile_strength_cache.clear()
            last_age_update.clear()

            # Generate guidance even when no faces detected
            blur_score = measure_blur(frame)
            guidance = generate_guidance(frame, faces, blur_score, smile_counter)
            
            # Display guidance hint at bottom center
            if guidance:
                frame_height, frame_width = frame.shape[:2]
                text_size = cv2.getTextSize(guidance, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = (frame_width - text_size[0]) // 2
                text_y = frame_height - 30
                
                # Draw background rectangle for better visibility
                cv2.rectangle(
                    frame,
                    (text_x - 10, text_y - text_size[1] - 10),
                    (text_x + text_size[0] + 10, text_y + 10),
                    (0, 0, 0),
                    -1
                )
                
                # Draw guidance text
                cv2.putText(
                    frame,
                    guidance,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

            cv2.imshow("Smart Camera", frame)

        else:
            all_smiling = True
            active_face_ids = set()

            for face in faces:
                face_id = face["id"]
                active_face_ids.add(face_id)

                x, y, w, h = face["bbox"]
                face_gray = face["gray_face"]
                face_bgr = frame[y:y+h, x:x+w]

                if face_id not in smile_counter:
                    smile_counter[face_id] = 0
                    age_cache[face_id] = "Detecting..."
                    gender_cache[face_id] = "Detecting..."
                    smile_strength_cache[face_id] = 0
                    last_age_update[face_id] = 0

                smile_detected = detect_smile(face_gray)

                if smile_detected:
                    smile_counter[face_id] += 1
                else:
                    smile_counter[face_id] = 0

                if smile_counter[face_id] < SMILE_THRESHOLD:
                    all_smiling = False

                current_time = time.time()

                if current_time - last_age_update[face_id] >= AGE_UPDATE_INTERVAL:
                    age_range, _ = predict_age(face_bgr)
                    age_cache[face_id] = age_range
                    gender = detect_gender(face_bgr)
                    gender_cache[face_id] = gender
                    # Compute smile strength
                    smile_strength = compute_smile_strength(face_bgr)
                    smile_strength_cache[face_id] = smile_strength
                    last_age_update[face_id] = current_time

                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Display overlay with ID, Smile, Age, Gender, SmileScore
                smile_score = smile_strength_cache.get(face_id, 0)
                overlay_text = f"ID:{face_id} Smile:{smile_counter[face_id]} Age:{age_cache[face_id]} SmileScore:{int(smile_score)}"
                cv2.putText(
                    frame,
                    overlay_text,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

            # Generate and display guidance hint
            blur_score = measure_blur(frame)
            guidance = generate_guidance(frame, faces, blur_score, smile_counter)
            
            if guidance:
                frame_height, frame_width = frame.shape[:2]
                text_size = cv2.getTextSize(guidance, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = (frame_width - text_size[0]) // 2
                text_y = frame_height - 30
                
                # Draw background rectangle for better visibility
                cv2.rectangle(
                    frame,
                    (text_x - 10, text_y - text_size[1] - 10),
                    (text_x + text_size[0] + 10, text_y + 10),
                    (0, 0, 0),
                    -1
                )
                
                # Draw guidance text
                cv2.putText(
                    frame,
                    guidance,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )
            
            if all_smiling:
                video_stream.release()
                cv2.destroyAllWindows()

                # Use login_session_id for storage folder (e.g., "session_1", "session_2")
                # Fallback to timestamp if not provided (shouldn't happen with auth)
                if login_session_id:
                    storage_session_id = login_session_id
                else:
                    storage_session_id = f"session_{int(time.time() * 1000)}"
                
                # Save raw frame WITHOUT annotations
                # Use backend/storage/images structure
                backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                # Create user-based storage path inside backend
                if user_id:
                    storage_dir = os.path.join(backend_root, "storage", "images", str(user_id), storage_session_id)
                else:
                    # Fallback for unauthenticated (shouldn't happen with auth required)
                    storage_dir = os.path.join(backend_root, "storage", "images", "guest", storage_session_id)
                
                os.makedirs(storage_dir, exist_ok=True)
                
                # Generate timestamp-based filename using current time
                from datetime import datetime
                timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{timestamp_str}.jpg"
                image_path = os.path.join(storage_dir, filename)
                
                # Store relative path for database (relative to backend root)
                relative_path = os.path.relpath(image_path, backend_root)
                
                cv2.imwrite(image_path, raw_frame)
                
                print(f"✓ Image saved: {relative_path}")

                # Perform post-capture analysis
                faces_final = detect_faces(raw_frame)
                face_metadata_list = []
                
                for face in faces_final:
                    face_id = face["id"]
                    x, y, w, h = face["bbox"]
                    face_bgr = raw_frame[y:y+h, x:x+w]
                    face_gray = face["gray_face"]
                    
                    # Get final age and gender
                    age_range, _ = predict_age(face_bgr)
                    gender = detect_gender(face_bgr)
                    smile_detected = detect_smile(face_gray)
                    
                    # BUG FIX: Always compute smile strength and level
                    # Ensure these fields are NEVER missing from response
                    try:
                        smile_strength = compute_smile_strength(face_bgr)
                    except Exception:
                        smile_strength = 0.0
                    
                    # Ensure smile_level is always computed
                    smile_level = classify_smile_level(smile_strength)
                    
                    # Ensure all required fields are present
                    face_metadata_list.append({
                        "face_id": face_id,
                        "age_range": age_range,
                        "gender": gender,
                        "smile_detected": smile_detected,
                        "smile_strength": float(smile_strength),  # Ensure float type
                        "smile_level": str(smile_level)  # Ensure string type
                    })
                
                # Measure quality
                quality_score = measure_blur(raw_frame)
                
                # NEW: Portrait Intelligence Analytics
                portrait_analytics = None
                emotional_state = None
                recommendation = None
                session_id = None
                is_best_in_session = False
                
                # Generate enhanced caption with face count and smile analytics
                if face_metadata_list:
                    first_face = face_metadata_list[0]
                    face_count = len(face_metadata_list)
                    
                    # Use computed smile strength and level
                    smile_strength_score = first_face["smile_strength"]
                    smile_level = first_face["smile_level"]
                    smile_probability = smile_strength_score / 100.0  # Convert to 0-1
                    
                    # NEW: Compute emotional state
                    try:
                        emotional_state = compute_emotional_state(
                            smile_probability=smile_probability,
                            smile_growth_rate=0.0,  # Can be enhanced with timeline tracking
                            smile_timeline=None
                        )
                    except Exception as e:
                        print(f"Emotional state computation failed: {e}")
                        emotional_state = "neutral"
                    
                    # NEW: Get mood recommendation (with user's preferred market and language)
                    try:
                        # Get user preferences
                        market = user.preferred_market if user and user.preferred_market else "US"
                        language = user.preferred_music_language if user and user.preferred_music_language else None
                        
                        recommendation = get_recommendation(
                            emotional_state, 
                            market=market,
                            user_id=user_id,
                            db_session=db_session,
                            language=language,
                            smile_score=smile_strength_score,
                            user=user,
                        )
                    except Exception as e:
                        print(f"Recommendation generation failed: {e}")
                        recommendation = None
                    
                    # NEW: Compute portrait analytics
                    try:
                        # Get first face bounding box
                        first_face_obj = faces_final[0]
                        face_bbox = first_face_obj["bbox"]
                        
                        portrait_analytics = analyze_portrait(
                            image=raw_frame,
                            face_bbox=face_bbox,
                            smile_probability=smile_probability
                        )
                        
                        # Add explanations
                        portrait_analytics["explanations"] = generate_score_explanation(portrait_analytics)
                        
                    except Exception as e:
                        print(f"Portrait analytics computation failed: {e}")
                        portrait_analytics = {
                            "lighting": 50.0,
                            "sharpness": 50.0,
                            "alignment": 50.0,
                            "smile_score": smile_probability * 100,
                            "final_score": 50.0,
                            "explanations": []
                        }
                    
                    # NEW: Add to session ranking
                    try:
                        session_engine = get_session_engine()
                        
                        # Determine age category
                        age_lower = int(first_face["age_range"].strip("()").split("-")[0])
                        if age_lower <= 12:
                            age_category = "child"
                        elif age_lower <= 25:
                            age_category = "young_adult"
                        else:
                            age_category = "adult"
                        
                        photo_metadata = session_engine.add_photo(
                            smile_probability=smile_probability,
                            lighting_score=portrait_analytics["lighting"],
                            sharpness_score=portrait_analytics["sharpness"],
                            alignment_score=portrait_analytics["alignment"],
                            final_score=portrait_analytics["final_score"],
                            age_category=age_category,
                            image_path=image_path,
                            emotional_state=emotional_state
                        )
                        
                        session_id = photo_metadata.session_id
                        is_best_in_session = photo_metadata.is_best_in_session
                        
                    except Exception as e:
                        print(f"Session ranking failed: {e}")
                    
                    # Generate caption directly (deterministic engine)
                    caption = generate_caption(
                        first_face["age_range"],
                        first_face["smile_detected"],
                        quality_score,
                        face_count,
                        smile_level,
                        smile_strength_score
                    )
                    
                    # Image organization removed - analytics stored in database only
                else:
                    caption = "Photo captured successfully!"

                # Return extended metadata (backward compatible)
                return (
                    raw_frame,
                    face_metadata_list,
                    quality_score,
                    caption,
                    relative_path,  # Use relative path for database storage
                    emotional_state,
                    recommendation,
                    portrait_analytics,
                    session_id if 'session_id' in locals() else storage_session_id,  # Use session_engine's ID if available
                    is_best_in_session,
                    user_id,  # Add user_id for database insertion
                    storage_session_id  # Add storage session_id for database
                )

            cv2.imshow("Smart Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        elapsed = time.time() - start_time
        sleep_time = FRAME_DELAY - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

    video_stream.release()
    cv2.destroyAllWindows()

    return None, None, None, None, None, None, None, None, None, None


def capture_photo_from_frame(frame, user_id: int = None, db_session = None, login_session_id: str = None, user = None):
    """
    Capture photo from a provided frame (browser webcam).
    Performs the same analytics pipeline as capture_photo but without cv2.VideoCapture.
    
    Args:
        frame: numpy array (BGR image from decoded base64)
        user_id: Authenticated user ID for storage organization
        db_session: Database session for filtering liked songs
        login_session_id: Login session ID (e.g., "session_1", "session_2")
        user: User object for accessing preferences (preferred_market, preferred_music_language)
    
    Returns:
        tuple: (raw_frame, face_metadata_list, quality_score, caption, image_path, ...)
               or (None, None, None, None, None, ...) if capture failed
    """
    if frame is None:
        return None, None, None, None, None, None, None, None, None, None, None, None
    
    raw_frame = frame.copy()
    
    # Use login_session_id for storage folder
    if login_session_id:
        storage_session_id = login_session_id
    else:
        storage_session_id = f"session_{int(time.time() * 1000)}"
    
    # Save raw frame WITHOUT annotations
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create user-based storage path
    if user_id:
        storage_dir = os.path.join(backend_root, "storage", "images", str(user_id), storage_session_id)
    else:
        storage_dir = os.path.join(backend_root, "storage", "images", "guest", storage_session_id)
    
    os.makedirs(storage_dir, exist_ok=True)
    
    # Generate timestamp-based filename
    from datetime import datetime
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp_str}.jpg"
    image_path = os.path.join(storage_dir, filename)
    
    # Store relative path for database
    relative_path = os.path.relpath(image_path, backend_root)
    
    cv2.imwrite(image_path, raw_frame)
    
    print(f"✓ Image saved: {relative_path}")
    
    # Perform post-capture analysis
    faces_final = detect_faces(raw_frame)
    face_metadata_list = []
    
    for face in faces_final:
        face_id = face["id"]
        x, y, w, h = face["bbox"]
        face_bgr = raw_frame[y:y+h, x:x+w]
        face_gray = face["gray_face"]
        
        # Get final age and gender
        age_range, _ = predict_age(face_bgr)
        gender = detect_gender(face_bgr)
        smile_detected = detect_smile(face_gray)
        
        # Compute smile strength and level using DeepFace
        try:
            smile_strength = compute_smile_strength(face_bgr)
            print(f"✓ Face {face_id}: Smile strength = {smile_strength:.1f}%")
        except Exception as e:
            print(f"⚠ Face {face_id}: Smile strength computation failed: {e}")
            smile_strength = 0.0
        
        smile_level = classify_smile_level(smile_strength)
        
        face_metadata_list.append({
            "face_id": face_id,
            "age_range": age_range,
            "gender": gender,
            "smile_detected": smile_detected,
            "smile_strength": float(smile_strength),
            "smile_level": str(smile_level)
        })
    
    # Measure quality
    quality_score = measure_blur(raw_frame)
    
    # Portrait Intelligence Analytics
    portrait_analytics = None
    emotional_state = None
    recommendation = None
    session_id = None
    is_best_in_session = False
    
    # Generate enhanced caption with face count and smile analytics
    if face_metadata_list:
        first_face = face_metadata_list[0]
        face_count = len(face_metadata_list)
        
        smile_strength_score = first_face["smile_strength"]
        smile_level = first_face["smile_level"]
        smile_probability = smile_strength_score / 100.0
        
        # Compute emotional state based ONLY on smile strength (not progression)
        # For uploaded/captured images, we don't have timeline data
        try:
            # Simple emotion mapping based on smile strength
            if smile_probability >= 0.75:
                emotional_state = "joyful"
            elif smile_probability >= 0.50:
                emotional_state = "happy"
            elif smile_probability >= 0.30:
                emotional_state = "content"
            else:
                emotional_state = "neutral"
            
            print(f"✓ Emotional state (from smile strength {smile_probability*100:.1f}%): {emotional_state}")
        except Exception as e:
            print(f"Emotional state computation failed: {e}")
            emotional_state = "neutral"
        
        # Get mood recommendation
        try:
            market = user.preferred_market if user and user.preferred_market else "US"
            language = user.preferred_music_language if user and user.preferred_music_language else None
            
            recommendation = get_recommendation(
                emotional_state, 
                market=market,
                user_id=user_id,
                db_session=db_session,
                language=language,
                smile_score=smile_strength_score,
                user=user,
            )
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            recommendation = None
        
        # Compute portrait analytics
        try:
            first_face_obj = faces_final[0]
            face_bbox = first_face_obj["bbox"]
            
            portrait_analytics = analyze_portrait(
                image=raw_frame,
                face_bbox=face_bbox,
                smile_probability=smile_probability
            )
            
            portrait_analytics["explanations"] = generate_score_explanation(portrait_analytics)
            
        except Exception as e:
            print(f"Portrait analytics computation failed: {e}")
            portrait_analytics = {
                "lighting": 50.0,
                "sharpness": 50.0,
                "alignment": 50.0,
                "smile_score": smile_probability * 100,
                "final_score": 50.0,
                "explanations": []
            }
        
        # Add to session ranking
        try:
            session_engine = get_session_engine()
            
            age_lower = int(first_face["age_range"].strip("()").split("-")[0])
            if age_lower <= 12:
                age_category = "child"
            elif age_lower <= 25:
                age_category = "young_adult"
            else:
                age_category = "adult"
            
            photo_metadata = session_engine.add_photo(
                smile_probability=smile_probability,
                lighting_score=portrait_analytics["lighting"],
                sharpness_score=portrait_analytics["sharpness"],
                alignment_score=portrait_analytics["alignment"],
                final_score=portrait_analytics["final_score"],
                age_category=age_category,
                image_path=image_path,
                emotional_state=emotional_state
            )
            
            session_id = photo_metadata.session_id
            is_best_in_session = photo_metadata.is_best_in_session
            
        except Exception as e:
            print(f"Session ranking failed: {e}")
        
        # Generate caption
        caption = generate_caption(
            first_face["age_range"],
            first_face["smile_detected"],
            quality_score,
            face_count,
            smile_level,
            smile_strength_score
        )
    else:
        caption = "Photo captured successfully!"
    
    return (
        raw_frame,
        face_metadata_list,
        quality_score,
        caption,
        relative_path,
        emotional_state,
        recommendation,
        portrait_analytics,
        session_id if 'session_id' in locals() else storage_session_id,
        is_best_in_session,
        user_id,
        storage_session_id
    )

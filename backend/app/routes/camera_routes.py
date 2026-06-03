from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.photo import Photo
from app.schemas.detection_schema import (
    CaptureResponse,
    FaceDetection,
    PortraitAnalytics,
    MusicRecommendation,
    MusicTrack
)
from app.services.capture_service import capture_photo
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CaptureRequest(BaseModel):
    client_timestamp: Optional[str] = None
    client_timezone: Optional[str] = None
    frame: Optional[str] = None  # Base64 encoded frame from browser
    source: Optional[str] = "camera"  # "camera" or "upload"

class PhotoResponse(BaseModel):
    id: int
    user_id: int
    session_id: str  # Changed to string (UUID)
    file_path: str
    age_category: str | None
    gender: str | None
    smile_score: float | None
    lighting_score: float | None
    sharpness_score: float | None
    alignment_score: float | None
    final_score: float | None
    is_best_in_session: bool
    source: Optional[str] = "camera"
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/user", response_model=List[PhotoResponse])
def get_user_photos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all photos for the current user.
    Returns photos ordered by created_at descending (newest first).
    """
    photos = db.query(Photo).filter(
        Photo.user_id == current_user.id
    ).order_by(Photo.created_at.desc()).all()
    
    return [
        PhotoResponse(
            id=photo.id,
            user_id=photo.user_id,
            session_id=photo.session_id,
            file_path=photo.file_path,
            age_category=photo.age_category,
            gender=photo.gender,
            smile_score=photo.smile_score,
            lighting_score=photo.lighting_score,
            sharpness_score=photo.sharpness_score,
            alignment_score=photo.alignment_score,
            final_score=photo.final_score,
            is_best_in_session=photo.is_best_in_session,
            source=photo.source or "camera",
            created_at=photo.created_at.isoformat() + "Z"
        )
        for photo in photos
    ]


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a photo by ID.
    Only the owner can delete their photos.
    """
    import os
    
    # Find the photo
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete physical file
    try:
        # Convert web path to file system path
        # /images/5/abc/file.jpg -> backend/storage/images/5/abc/file.jpg
        file_path = photo.file_path.replace("/images/", "")
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(backend_root, "storage", "images", file_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"✓ Deleted file: {full_path}")
        else:
            print(f"⚠ File not found: {full_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
        # Continue to delete database record even if file deletion fails
    
    # Delete database record
    db.delete(photo)
    db.commit()
    
    print(f"✓ Deleted photo record: ID={photo_id}")
    
    return {"message": "Photo deleted successfully", "photo_id": photo_id}

@router.post("/capture", response_model=CaptureResponse)
def capture(
    request: CaptureRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Capture photo using camera with face detection and portrait intelligence.
    Protected route - requires JWT authentication.
    Saves to user-based storage and creates database record.
    
    Args:
        request: Contains client_timestamp, client_timezone, and optional frame (base64)
    
    Returns:
        CaptureResponse with image_path, faces metadata, caption,
        and portrait intelligence features (emotional_state, music_recommendation, analytics)
    """
    import cv2
    import numpy as np
    import base64
    from app.services.capture_service import capture_photo_from_frame
    
    # Get user's login session ID
    login_session_id = current_user.login_session_id
    if not login_session_id:
        import uuid
        login_session_id = str(uuid.uuid4())
        current_user.login_session_id = login_session_id
        db.commit()
    
    # Check if frame is provided (browser webcam mode)
    if request.frame:
        # Decode base64 frame
        try:
            frame_data = request.frame
            if "," in frame_data:
                frame_data = frame_data.split(",")[1]
            
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise HTTPException(status_code=400, detail="Failed to decode frame")
            
            # Use new capture function with provided frame
            result = capture_photo_from_frame(
                frame=frame,
                user_id=current_user.id,
                db_session=db,
                login_session_id=login_session_id,
                user=current_user
            )
        except Exception as e:
            print(f"Frame decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to process frame: {str(e)}")
    else:
        # Fallback to original OpenCV capture (for backward compatibility)
        result = capture_photo(
            user_id=current_user.id, 
            db_session=db,
            login_session_id=login_session_id,
            user=current_user
        )
    
    # Unpack extended response (backward compatible)
    if len(result) == 12:
        (raw_frame, face_metadata_list, quality_score, caption, image_path,
         emotional_state, recommendation, portrait_analytics, session_id, is_best_in_session,
         user_id, storage_session_id) = result
    elif len(result) == 10:
        (raw_frame, face_metadata_list, quality_score, caption, image_path,
         emotional_state, recommendation, portrait_analytics, session_id, is_best_in_session) = result
        user_id = current_user.id
        storage_session_id = session_id
    else:
        # Fallback for old response format
        raw_frame, face_metadata_list, quality_score, caption, image_path = result[:5]
        emotional_state = None
        recommendation = None
        portrait_analytics = None
        session_id = None
        is_best_in_session = False
        user_id = current_user.id
        storage_session_id = None
    
    if raw_frame is None:
        raise HTTPException(status_code=400, detail="Failed to capture photo")
    
    # Insert photo record into database
    try:
        # Determine age category and gender from first face
        age_category = None
        gender = None
        if face_metadata_list:
            first_face = face_metadata_list[0]
            age_lower = int(first_face["age_range"].strip("()").split("-")[0])
            if age_lower <= 12:
                age_category = "child"
            elif age_lower <= 25:
                age_category = "young_adult"
            else:
                age_category = "adult"
            
            # Store gender for filtering
            gender = first_face.get("gender", "Unknown")
        
        # Use user's login_session_id instead of timestamp-based session
        login_session_id = current_user.login_session_id
        if not login_session_id:
            # Generate one if somehow missing
            import uuid
            login_session_id = str(uuid.uuid4())
            current_user.login_session_id = login_session_id
            db.commit()
        
        # Parse client timestamp if provided
        created_at = None
        if request.client_timestamp:
            try:
                created_at = datetime.fromisoformat(request.client_timestamp.replace('Z', '+00:00'))
                print(f"✓ Using client timestamp: {created_at} (Timezone: {request.client_timezone})")
            except Exception as e:
                print(f"Failed to parse client timestamp: {e}, using server time")
                created_at = datetime.utcnow()
        else:
            created_at = datetime.utcnow()
        
        # Create photo record
        # Convert file path to web-accessible URL format
        # image_path from capture_service is like: storage\images\123\456\2026-03-09_20-15-34.jpg
        # We need to convert it to: /images/123/456/2026-03-09_20-15-34.jpg
        web_path = image_path.replace("\\", "/")  # Normalize separators
        if web_path.startswith("storage/images/"):
            web_path = "/" + web_path.replace("storage/images/", "images/")
        elif not web_path.startswith("/images/"):
            # Fallback: extract part after storage/images/
            parts = web_path.split("storage/images/")
            if len(parts) > 1:
                web_path = "/images/" + parts[1]
        
        print(f"✓ Storing web path: {web_path}")
        
        # Compute quality score
        from app.services.best_image_selector import compute_quality_score
        
        photo = Photo(
            user_id=user_id,
            session_id=login_session_id,  # Use login session ID
            file_path=web_path,  # Store web-accessible path
            age_category=age_category,
            gender=gender,
            smile_score=portrait_analytics.get("smile_score") if portrait_analytics else None,
            lighting_score=portrait_analytics.get("lighting") if portrait_analytics else None,
            sharpness_score=portrait_analytics.get("sharpness") if portrait_analytics else None,
            alignment_score=portrait_analytics.get("alignment") if portrait_analytics else None,
            final_score=portrait_analytics.get("final_score") if portrait_analytics else None,
            quality_score=None,  # Will be computed below
            is_best_in_session=False,  # Will be updated by best_image_selector
            source=request.source or "camera",  # Store source: "camera" or "upload"
            created_at=created_at  # Use client timestamp
        )
        
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        # Compute quality score for this photo
        from app.services.best_image_selector import compute_quality_score, update_best_images_for_session
        photo.quality_score = compute_quality_score(photo)
        db.commit()
        
        # Update best images for this session
        update_best_images_for_session(login_session_id, user_id, db)
        
        # Refresh to get updated is_best_in_session flag
        db.refresh(photo)
        is_best_in_session = photo.is_best_in_session
        
        print(f"✓ Photo record created: ID={photo.id}, User={user_id}, LoginSession={login_session_id}, Path={web_path}")
        print(f"  Quality Score: {photo.quality_score:.1f}, Best: {is_best_in_session}")
        
    except Exception as e:
        print(f"Failed to create photo record: {e}")
        db.rollback()
        # Continue anyway - don't fail the capture
    
    # Convert face metadata to schema format
    faces = [
        FaceDetection(
            face_id=face["face_id"],
            age_range=face["age_range"],
            gender=face["gender"],
            smile_detected=face["smile_detected"],
            smile_strength=face["smile_strength"],
            smile_level=face["smile_level"]
        )
        for face in face_metadata_list
    ]
    
    # Convert music recommendation to schema format
    music_recommendation = None
    if recommendation:
        tracks_data = recommendation.get("tracks", [])
        
        # Only create recommendation if tracks exist
        if tracks_data:
            music_tracks = []
            for track in tracks_data:
                # Skip tracks with no title (completely empty)
                if not track.get("title"):
                    continue

                music_tracks.append(
                    MusicTrack(
                        title=track.get("title", "Unknown"),
                        artist=track.get("artist", "Unknown Artist"),
                        video_id=track.get("video_id"),
                        embed_url=track.get("embed_url"),
                        watch_url=track.get("watch_url"),
                        spotify_url=track.get("spotify_url"),
                        track_id=track.get("track_id"),
                        preview_url=track.get("preview_url"),
                        popularity=track.get("popularity", 0),
                    )
                )
            
            # Only create recommendation if we have valid tracks
            if music_tracks:
                music_recommendation = MusicRecommendation(
                    message=recommendation.get("message", ""),
                    tracks=music_tracks,
                    state=recommendation.get("state", "neutral")
                )
    
    # Convert analytics to schema format
    analytics = None
    if portrait_analytics:
        analytics = PortraitAnalytics(
            lighting=portrait_analytics.get("lighting", 50.0),
            sharpness=portrait_analytics.get("sharpness", 50.0),
            alignment=portrait_analytics.get("alignment", 50.0),
            smile_score=portrait_analytics.get("smile_score", 50.0),
            final_score=portrait_analytics.get("final_score", 50.0),
            explanations=portrait_analytics.get("explanations", [])
        )
    
    # Convert file path to web-accessible URL
    # image_path from capture_service is like: storage\images\5\abc\2026-03-09_20-15-34.jpg (Windows)
    # or: storage/images/5/abc/2026-03-09_20-15-34.jpg (Unix)
    # Convert to: /images/5/abc/2026-03-09_20-15-34.jpg
    web_image_path = image_path.replace("\\", "/")  # Normalize path separators
    if web_image_path.startswith("storage/images/"):
        web_image_path = "/" + web_image_path.replace("storage/images/", "images/")
    elif not web_image_path.startswith("/images/"):
        # Fallback: try to extract the part after storage/images/
        parts = web_image_path.split("storage/images/")
        if len(parts) > 1:
            web_image_path = "/images/" + parts[1]
    
    print(f"✓ Image path conversion: {image_path} -> {web_image_path}")
    
    return CaptureResponse(
        image_path=web_image_path,
        faces=faces,
        caption=caption,
        emotional_state=emotional_state,
        music_recommendation=music_recommendation,
        analytics=analytics,
        session_id=session_id,
        is_best_in_session=is_best_in_session
    )

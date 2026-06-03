"""
Best Image Selection Service

Implements logic to select the best image per session based on:
- Age group
- Gender
- Quality score

Only ONE best image per (session, age_group, gender) combination.
"""
from sqlalchemy.orm import Session
from app.models.photo import Photo
from typing import List, Dict


def compute_quality_score(photo: Photo) -> float:
    """
    Compute quality score for a photo.
    
    Formula:
    quality_score = 0.30 * smile_score + 0.20 * alignment_score + 
                    0.20 * lighting_score + 0.20 * sharpness_score + 
                    0.10 * final_score
    
    Args:
        photo: Photo object
        
    Returns:
        float: Quality score (0-100)
    """
    components = []
    weights = []
    
    if photo.smile_score is not None:
        components.append(photo.smile_score)
        weights.append(0.3)
    
    if photo.alignment_score is not None:
        components.append(photo.alignment_score)
        weights.append(0.2)
    
    if photo.lighting_score is not None:
        components.append(photo.lighting_score)
        weights.append(0.2)
    
    if photo.sharpness_score is not None:
        components.append(photo.sharpness_score)
        weights.append(0.2)
    
    if photo.final_score is not None:
        components.append(photo.final_score)
        weights.append(0.1)
    
    if not components:
        return 50.0  # Default score
    
    # Weighted average
    total_weight = sum(weights)
    weighted_sum = sum(c * w for c, w in zip(components, weights))
    
    return weighted_sum / total_weight if total_weight > 0 else 50.0


def update_best_images_for_session(session_id: str, user_id: int, db: Session):
    """
    Update best image flags for a specific session.
    
    Logic:
    1. Get all photos in the session
    2. Group by age_category (child, young_adult, adult)
    3. For each age group, select the photo with highest quality_score
    4. Mark only those photos as is_best_in_session = True
    
    Args:
        session_id: Session identifier (e.g., "session_1 Mar 10, 2026")
        user_id: User ID
        db: Database session
    """
    # Get all photos in this session
    photos = db.query(Photo).filter(
        Photo.session_id == session_id,
        Photo.user_id == user_id
    ).all()
    
    if not photos:
        return
    
    print(f"\n{'='*60}")
    print(f"Updating best images for session: {session_id}")
    print(f"Total photos in session: {len(photos)}")
    
    # First, reset all is_best flags in this session
    for photo in photos:
        photo.is_best_in_session = False
    
    # Group photos by age_category only (not gender)
    groups: Dict[str, List[Photo]] = {}
    
    for photo in photos:
        # Compute and store quality score
        quality_score = compute_quality_score(photo)
        photo.quality_score = quality_score
        
        # Group key: age_category only
        age_cat = photo.age_category or "unknown"
        
        if age_cat not in groups:
            groups[age_cat] = []
        groups[age_cat].append(photo)
    
    print(f"Found {len(groups)} unique age groups")
    
    # For each group, select the best photo
    best_photos = []
    
    for age_cat, group_photos in groups.items():
        # Sort by quality_score descending
        group_photos.sort(key=lambda p: p.quality_score or 0, reverse=True)
        
        # Select the best one
        best_photo = group_photos[0]
        best_photo.is_best_in_session = True
        best_photos.append(best_photo)
        
        print(f"  Age Group ({age_cat}): Best photo ID={best_photo.id}, Quality={best_photo.quality_score:.1f}")
    
    # Commit changes
    db.commit()
    
    print(f"✓ Marked {len(best_photos)} photos as best in session")
    print(f"{'='*60}\n")


def update_all_best_images(user_id: int, db: Session):
    """
    Update best image flags for all sessions of a user.
    
    Args:
        user_id: User ID
        db: Database session
    """
    # Get all unique sessions for this user
    sessions = db.query(Photo.session_id).filter(
        Photo.user_id == user_id
    ).distinct().all()
    
    print(f"\nUpdating best images for user {user_id}")
    print(f"Total sessions: {len(sessions)}")
    
    for (session_id,) in sessions:
        update_best_images_for_session(session_id, user_id, db)
    
    print(f"✓ All sessions updated for user {user_id}\n")

"""
Authentication routes - Firebase only.
No login/register endpoints - all auth handled by Firebase on frontend.
Backend only provides user profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserResponse, ProfileUpdate

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile.
    Requires Firebase ID token in Authorization header.
    """
    return current_user

@router.post("/login", response_model=UserResponse)
def login(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Login endpoint - generates a new session ID for the user.
    Called by frontend after Firebase authentication.
    Requires Firebase ID token in Authorization header.
    
    This creates a new session for the user's login.
    All photos captured during this session will be grouped together.
    """
    from app.models.photo import Photo
    from datetime import date
    
    today = date.today()
    today_str = today.strftime("%b %d, %Y")  # e.g., "Mar 10, 2026"
    
    # Get all sessions for this user today
    existing_sessions = db.query(Photo.session_id).filter(
        Photo.user_id == current_user.id
    ).distinct().all()
    
    # Count sessions from today
    today_session_count = 0
    for (session_id,) in existing_sessions:
        if session_id and today_str in session_id:
            today_session_count += 1
    
    # Next session number for today
    next_session_num = today_session_count + 1
    current_user.login_session_id = f"session_{next_session_num} {today_str}"
    
    db.commit()
    db.refresh(current_user)
    
    print(f"✓ User logged in - Session ID: {current_user.login_session_id}")
    
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information.
    Requires Firebase ID token in Authorization header.
    """
    # Update fields if provided
    if profile_data.phone_number is not None:
        current_user.phone_number = profile_data.phone_number.strip() if profile_data.phone_number.strip() else None
    
    if profile_data.country is not None:
        current_user.country = profile_data.country.strip() if profile_data.country.strip() else None
    
    if profile_data.preferred_market is not None:
        current_user.preferred_market = profile_data.preferred_market
    
    if profile_data.preferred_music_language is not None:
        current_user.preferred_music_language = profile_data.preferred_music_language.strip() if profile_data.preferred_music_language.strip() else None

    if profile_data.favorite_genres is not None:
        current_user.favorite_genres = profile_data.favorite_genres.strip() if profile_data.favorite_genres.strip() else None

    if profile_data.favorite_artists is not None:
        current_user.favorite_artists = profile_data.favorite_artists.strip() if profile_data.favorite_artists.strip() else None
    
    # Commit changes
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/status")
def auth_status():
    """
    Check authentication system status.
    Public endpoint - no authentication required.
    """
    return {
        "status": "active",
        "auth_provider": "Firebase",
        "message": "Authentication handled by Firebase. Send Firebase ID token in Authorization header."
    }

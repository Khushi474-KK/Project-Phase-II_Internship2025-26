from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.liked_song import LikedSong
from app.models.disliked_song import DislikedSong
from app.schemas.liked_song_schema import LikedSongCreate, LikedSongResponse
from pydantic import BaseModel

router = APIRouter()

class DislikedSongCreate(BaseModel):
    song_id: str
    artist: str
    track_name: str
    mood: str = "neutral"

class DislikedSongResponse(BaseModel):
    id: int
    user_id: int
    song_id: str
    track_name: str
    artist: str
    mood: str
    
    class Config:
        from_attributes = True

@router.post("/like", response_model=LikedSongResponse)
def like_song(
    song_data: LikedSongCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a song and store user preference.
    """
    # Check if already liked
    existing = db.query(LikedSong).filter(
        LikedSong.user_id == current_user.id,
        LikedSong.song_id == song_data.song_id
    ).first()
    
    if existing:
        # Unlike (remove from database)
        db.delete(existing)
        db.commit()
        raise HTTPException(status_code=200, detail="Song unliked")
    
    # Create new liked song
    liked_song = LikedSong(
        user_id=current_user.id,
        song_id=song_data.song_id,
        artist=song_data.artist,
        track_name=song_data.track_name,
        mood=song_data.mood
    )
    
    db.add(liked_song)
    db.commit()
    db.refresh(liked_song)
    
    return liked_song

@router.get("/liked", response_model=list[LikedSongResponse])
def get_liked_songs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all liked songs for the current user.
    """
    liked_songs = db.query(LikedSong).filter(
        LikedSong.user_id == current_user.id
    ).all()
    
    return liked_songs

@router.get("/is-liked/{song_id}")
def is_song_liked(
    song_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a song is liked by the current user.
    """
    liked = db.query(LikedSong).filter(
        LikedSong.user_id == current_user.id,
        LikedSong.song_id == song_id
    ).first()
    
    return {"is_liked": liked is not None}

@router.post("/dislike", response_model=DislikedSongResponse)
def dislike_song(
    song_data: DislikedSongCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dislike a song and store user preference.
    Disliked songs will be filtered out from future recommendations.
    """
    # Check if already disliked
    existing = db.query(DislikedSong).filter(
        DislikedSong.user_id == current_user.id,
        DislikedSong.song_id == song_data.song_id
    ).first()
    
    if existing:
        # Un-dislike (remove from database)
        db.delete(existing)
        db.commit()
        raise HTTPException(status_code=200, detail="Song un-disliked")
    
    # Create new disliked song
    disliked_song = DislikedSong(
        user_id=current_user.id,
        song_id=song_data.song_id,
        artist=song_data.artist,
        track_name=song_data.track_name,
        mood=song_data.mood
    )
    
    db.add(disliked_song)
    db.commit()
    db.refresh(disliked_song)
    
    return disliked_song

@router.get("/disliked", response_model=list[DislikedSongResponse])
def get_disliked_songs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all disliked songs for the current user.
    """
    disliked_songs = db.query(DislikedSong).filter(
        DislikedSong.user_id == current_user.id
    ).all()
    
    return disliked_songs

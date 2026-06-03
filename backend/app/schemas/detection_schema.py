from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class FaceDetection(BaseModel):
    face_id: int
    age_range: str
    gender: str
    smile_detected: bool
    smile_strength: float
    smile_level: str

class PortraitAnalytics(BaseModel):
    """Portrait analytics with multi-factor scoring."""
    lighting: float
    sharpness: float
    alignment: float
    smile_score: float
    final_score: float
    explanations: List[str]

class MusicTrack(BaseModel):
    """Individual music track recommendation."""
    title: str
    artist: str
    video_id: Optional[str] = None       # YouTube video ID (None if no API key)
    embed_url: Optional[str] = None      # YouTube embed URL
    watch_url: Optional[str] = None      # YouTube watch/search URL for fallback link
    spotify_url: Optional[str] = None    # kept for backward compat
    track_id: Optional[str] = None       # kept for backward compat
    preview_url: Optional[str] = None
    popularity: int = 0

class MusicRecommendation(BaseModel):
    """Music recommendation with multiple tracks and contextual message."""
    message: str
    tracks: List[MusicTrack]
    state: str

class CaptureResponse(BaseModel):
    """Extended capture response with portrait intelligence."""
    image_path: str
    faces: List[FaceDetection]
    caption: str
    # New portrait intelligence fields (optional for backward compatibility)
    emotional_state: Optional[str] = None
    music_recommendation: Optional[MusicRecommendation] = None
    analytics: Optional[PortraitAnalytics] = None
    session_id: Optional[int] = None
    is_best_in_session: Optional[bool] = False

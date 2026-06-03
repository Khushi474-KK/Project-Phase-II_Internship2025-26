from pydantic import BaseModel
from datetime import datetime

class LikedSongCreate(BaseModel):
    song_id: str
    artist: str
    track_name: str
    mood: str

class LikedSongResponse(BaseModel):
    id: int
    user_id: int
    song_id: str
    artist: str
    track_name: str
    mood: str
    timestamp: datetime

    class Config:
        from_attributes = True

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class DislikedSong(Base):
    __tablename__ = "disliked_songs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    song_id = Column(String, nullable=False, index=True)  # Spotify track ID
    track_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    mood = Column(String, nullable=True)  # Emotional state when disliked
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="disliked_songs")

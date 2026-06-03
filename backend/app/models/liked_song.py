from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class LikedSong(Base):
    __tablename__ = "liked_songs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    song_id = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    track_name = Column(String, nullable=False)
    mood = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="liked_songs")

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Always NULL for Firebase auth users
    auth_provider = Column(String, nullable=True, default="firebase")  # Always "firebase"
    firebase_uid = Column(String, unique=True, nullable=True, index=True)  # Firebase UID (primary identifier)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)  # Track last login time
    login_session_id = Column(String, nullable=True)  # Current login session ID
    
    # Extended fields (backward compatible - nullable)
    phone_number = Column(String, nullable=True, default=None)
    country = Column(String, nullable=True, default=None)
    preferred_market = Column(String, nullable=True, default="US")
    preferred_music_language = Column(String, nullable=True, default=None)
    favorite_genres = Column(String, nullable=True, default=None)   # comma-separated, e.g. "pop,indie,lofi"
    favorite_artists = Column(String, nullable=True, default=None)  # comma-separated
    
    # Relationships
    photos = relationship("Photo", back_populates="user")
    liked_songs = relationship("LikedSong", back_populates="user")
    disliked_songs = relationship("DislikedSong", back_populates="user")

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)  # Login session ID (UUID string)
    file_path = Column(String, nullable=False)
    age_category = Column(String, nullable=True)
    gender = Column(String, nullable=True)  # Add gender field for filtering
    smile_score = Column(Float, nullable=True)
    lighting_score = Column(Float, nullable=True)
    sharpness_score = Column(Float, nullable=True)
    alignment_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)  # Computed quality score for ranking
    is_best_in_session = Column(Boolean, default=False)
    source = Column(String, nullable=True, default="camera")  # "camera" or "upload"
    created_at = Column(DateTime, nullable=False)  # Client device timestamp
    
    # Relationship
    user = relationship("User", back_populates="photos")

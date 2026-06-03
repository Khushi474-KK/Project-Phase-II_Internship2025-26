"""
Session Ranking Engine
Manages photo sessions and rankings
Maintains in-memory session store alongside existing age-based grouping
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PhotoMetadata:
    """Photo metadata for session tracking."""
    id: str
    session_id: int
    timestamp: float
    smile_probability: float
    lighting_score: float
    sharpness_score: float
    alignment_score: float
    final_score: float
    age_category: str
    image_path: str
    is_best_in_session: bool = False
    emotional_state: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "smile_probability": self.smile_probability,
            "lighting_score": self.lighting_score,
            "sharpness_score": self.sharpness_score,
            "alignment_score": self.alignment_score,
            "final_score": self.final_score,
            "age_category": self.age_category,
            "image_path": self.image_path,
            "is_best_in_session": self.is_best_in_session,
            "emotional_state": self.emotional_state
        }


class SessionRankingEngine:
    """
    Session-based photo ranking engine.
    Maintains in-memory store of photos grouped by session.
    """
    
    def __init__(self):
        """Initialize session ranking engine."""
        self.session_store: Dict[int, List[PhotoMetadata]] = {}
        self.current_session_id: Optional[int] = None
    
    def start_session(self) -> int:
        """
        Start a new photo session.
        
        Returns:
            int: New session ID
        """
        self.current_session_id = int(time.time() * 1000)  # Millisecond timestamp
        self.session_store[self.current_session_id] = []
        return self.current_session_id
    
    def add_photo(
        self,
        smile_probability: float,
        lighting_score: float,
        sharpness_score: float,
        alignment_score: float,
        final_score: float,
        age_category: str,
        image_path: str,
        emotional_state: Optional[str] = None
    ) -> PhotoMetadata:
        """
        Add photo to current session.
        
        Args:
            smile_probability: Smile probability (0-1)
            lighting_score: Lighting score (0-100)
            sharpness_score: Sharpness score (0-100)
            alignment_score: Alignment score (0-100)
            final_score: Final portrait score (0-100)
            age_category: Age category
            image_path: Path to saved image
            emotional_state: Emotional state classification
            
        Returns:
            PhotoMetadata: Photo metadata object
        """
        # Ensure session exists
        if self.current_session_id is None:
            self.start_session()
        
        # Create photo metadata
        photo = PhotoMetadata(
            id=f"photo_{int(time.time() * 1000)}_{len(self.session_store[self.current_session_id])}",
            session_id=self.current_session_id,
            timestamp=time.time(),
            smile_probability=smile_probability,
            lighting_score=lighting_score,
            sharpness_score=sharpness_score,
            alignment_score=alignment_score,
            final_score=final_score,
            age_category=age_category,
            image_path=image_path,
            emotional_state=emotional_state
        )
        
        # Add to session
        self.session_store[self.current_session_id].append(photo)
        
        # Update rankings
        self._update_session_rankings(self.current_session_id)
        
        return photo
    
    def _update_session_rankings(self, session_id: int):
        """
        Update rankings for a session.
        Marks the photo with highest final_score as best.
        
        Args:
            session_id: Session ID
        """
        if session_id not in self.session_store:
            return
        
        photos = self.session_store[session_id]
        
        if not photos:
            return
        
        # Reset all is_best_in_session flags
        for photo in photos:
            photo.is_best_in_session = False
        
        # Find photo with highest final_score
        best_photo = max(photos, key=lambda p: p.final_score)
        best_photo.is_best_in_session = True
    
    def get_ranked_photos(self, session_id: Optional[int] = None) -> List[PhotoMetadata]:
        """
        Get ranked photos for a session.
        
        Args:
            session_id: Session ID (uses current if None)
            
        Returns:
            List[PhotoMetadata]: Photos sorted by final_score descending
        """
        sid = session_id if session_id is not None else self.current_session_id
        
        if sid is None or sid not in self.session_store:
            return []
        
        photos = self.session_store[sid]
        return sorted(photos, key=lambda p: p.final_score, reverse=True)
    
    def get_best_photo(self, session_id: Optional[int] = None) -> Optional[PhotoMetadata]:
        """
        Get best photo in session.
        
        Args:
            session_id: Session ID (uses current if None)
            
        Returns:
            PhotoMetadata: Best photo or None
        """
        sid = session_id if session_id is not None else self.current_session_id
        
        if sid is None or sid not in self.session_store:
            return None
        
        photos = self.session_store[sid]
        
        for photo in photos:
            if photo.is_best_in_session:
                return photo
        
        return None
    
    def get_session_stats(self, session_id: Optional[int] = None) -> Dict:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session ID (uses current if None)
            
        Returns:
            dict: Session statistics
        """
        sid = session_id if session_id is not None else self.current_session_id
        
        if sid is None or sid not in self.session_store:
            return {
                "total_photos": 0,
                "avg_score": 0.0,
                "best_score": 0.0,
                "worst_score": 0.0
            }
        
        photos = self.session_store[sid]
        
        if not photos:
            return {
                "total_photos": 0,
                "avg_score": 0.0,
                "best_score": 0.0,
                "worst_score": 0.0
            }
        
        scores = [p.final_score for p in photos]
        
        return {
            "total_photos": len(photos),
            "avg_score": round(sum(scores) / len(scores), 2),
            "best_score": round(max(scores), 2),
            "worst_score": round(min(scores), 2)
        }
    
    def end_session(self):
        """End current session."""
        self.current_session_id = None
    
    def get_all_sessions(self) -> List[int]:
        """
        Get all session IDs.
        
        Returns:
            List[int]: List of session IDs
        """
        return list(self.session_store.keys())
    
    def clear_session(self, session_id: int):
        """
        Clear a specific session.
        
        Args:
            session_id: Session ID to clear
        """
        if session_id in self.session_store:
            del self.session_store[session_id]


# Global session ranking engine instance
_session_engine = None


def get_session_engine() -> SessionRankingEngine:
    """Get global session ranking engine instance."""
    global _session_engine
    if _session_engine is None:
        _session_engine = SessionRankingEngine()
    return _session_engine

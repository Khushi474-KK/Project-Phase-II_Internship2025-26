from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    phone_number: Optional[str] = None
    country: Optional[str] = None
    preferred_market: Optional[str] = "US"
    preferred_music_language: Optional[str] = None
    favorite_genres: Optional[str] = None
    favorite_artists: Optional[str] = None
    auth_provider: Optional[str] = "firebase"

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    phone_number: Optional[str] = None
    country: Optional[str] = None
    preferred_market: Optional[str] = None
    preferred_music_language: Optional[str] = None
    favorite_genres: Optional[str] = None    # comma-separated genres
    favorite_artists: Optional[str] = None  # comma-separated artists
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number length."""
        if v is not None and v.strip():
            v = v.strip()
            if len(v) > 20:
                raise ValueError('Phone number must be 20 characters or less')
            return v
        return None
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v: Optional[str]) -> Optional[str]:
        """Validate country length."""
        if v is not None and v.strip():
            v = v.strip()
            if len(v) > 50:
                raise ValueError('Country must be 50 characters or less')
            return v
        return None

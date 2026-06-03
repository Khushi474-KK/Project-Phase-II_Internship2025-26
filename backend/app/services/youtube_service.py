"""
YouTube Service
Searches YouTube Data API v3 for a track and returns a video_id + embed_url.

NOTE: The active recommendation pipeline (mood_recommendation_engine.py) now uses
direct emotion-based YouTube search instead of per-track lookups.
This module's search_track() is kept for potential future use (e.g. dataset pipeline).
"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_track(track_name: str, artist_name: str) -> Optional[Dict]:
    """
    Search YouTube for a track and return its video_id and embed_url.

    Query: "{track_name} {artist_name} official song"
    Falls back to "{track_name} {artist_name}" if no results.

    Returns:
        {
            "video_id":  str,
            "embed_url": str,   # https://www.youtube.com/embed/{video_id}
            "title":     str,
            "artist":    str,
        }
        or None if API key missing / no results.
    """
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        print("YouTube API key not configured")
        return None

    def _search(q: str) -> Optional[str]:
        try:
            resp = requests.get(
                YOUTUBE_SEARCH_URL,
                params={
                    "part":       "snippet",
                    "q":          q,
                    "type":       "video",
                    "maxResults": 1,
                    "key":        api_key,
                },
                timeout=8,
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    return items[0]["id"]["videoId"]
            else:
                print(f"YouTube search failed ({resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            print(f"YouTube search error: {e}")
        return None

    # Primary query
    video_id = _search(f"{track_name} {artist_name} official song")

    # Fallback — drop "official song"
    if not video_id:
        video_id = _search(f"{track_name} {artist_name}")

    # Last resort — track name only
    if not video_id:
        video_id = _search(track_name)

    if not video_id:
        print(f"YouTube: no result for '{track_name}' by '{artist_name}'")
        return None

    return {
        "video_id":  video_id,
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "title":     track_name,
        "artist":    artist_name,
    }

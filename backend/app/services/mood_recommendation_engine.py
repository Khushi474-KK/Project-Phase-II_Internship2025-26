"""
Mood Recommendation Engine
=========================

ACTIVE PIPELINE (YouTube-only):
  1. Detect emotion from analytics
  2. Get user's preferred music language
  3. Build a smart search query: "{emotion_phrase} {language} songs official audio"
  4. Search YouTube (videoCategoryId=10, maxResults=20)
  5. Remove playlist/compilation-style titles (regex patterns)
  6. Fetch video durations, keep only 2–8 minute videos
  7. Prefer titles that look like real songs (Artist - Title format)
  8. Shuffle remaining results
  9. Filter disliked/excluded video IDs
  10. Return top 5

OLD DATASET PIPELINE (kept for future use — NOT executed):
  See commented block below. Uses music.csv + audio feature filtering + YouTube ID resolution.
"""

import os
import re
import random
import urllib.parse
from typing import Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# OLD DATASET RECOMMENDATION SYSTEM (kept for future use — NOT executed)
# ─────────────────────────────────────────────────────────────────────────────
# from app.services.dataset_service import get_candidates, is_loaded
#
# def _get_dataset_candidates(emotional_state, user_genres, excluded_ids, market, target=5):
#     """
#     OLD FLOW:
#       candidates = get_candidates(emotional_state, user_genres=user_genres, top_n=30)
#       tracks = _resolve_tracks(candidates, excluded_ids, market=market, target_count=target)
#       if len(tracks) < 3:
#           extra = get_candidates(emotional_state, user_genres=None, top_n=50)
#           seen = {c["track_name"] for c in candidates}
#           extra = [c for c in extra if c["track_name"] not in seen]
#           tracks += _resolve_tracks(extra, excluded_ids, market=market, target_count=target - len(tracks))
#       return tracks
#     """
#     pass
#
# def _resolve_tracks(candidates, excluded_ids, market, target_count=5):
#     """
#     OLD FLOW:
#       For each dataset candidate, call search_track(track_name, artist_name).
#       Skip if video_id in excluded_ids.
#       Fall back to search-embed URL when no API key.
#       Stop once target_count results collected.
#     """
#     pass
#
# def _make_search_fallback(candidate):
#     """
#     OLD FLOW:
#       Build embed_url using YouTube search embed (no API key needed).
#       embed_url = f"https://www.youtube.com/embed?listType=search&list={query}"
#     """
#     pass
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# Emotion → smart search phrase mapping
# Avoids naive "happy songs" / "sad songs" queries
# ─────────────────────────────────────────────────────────────────────────────
_EMOTION_PHRASES = {
    "joyful":     "feel good upbeat",
    "happy":      "feel good cheerful",
    "content":    "relaxing chill",
    "cheerful":   "upbeat feel good",
    "positive":   "motivational uplifting",
    "neutral":    "trending popular",
    "recovering": "comeback motivational",
    "low_affect": "soothing gentle",
    "sad":        "emotional heartfelt",
    "calm":       "peaceful acoustic",
    "excited":    "energetic party",
}

_MESSAGES = {
    "joyful":     "You're glowing! Here's a soundtrack to match 🌟",
    "happy":      "Great energy! These tracks are made for moments like this 🎵",
    "content":    "Feeling good? Here's something to keep the flow going 🎶",
    "cheerful":   "Keep the vibe going! 🎧 Listen to these to enhance your mood.",
    "positive":   "Here are some tracks to lift your energy even higher 🎶",
    "neutral":    "A balanced mood deserves balanced beats 🎵",
    "low_affect": "Let these songs gently elevate your spirits 🎧",
    "recovering": "You're gaining momentum! These tracks match your comeback energy 🔥",
    "sad":        "Let the music carry you through 🎵",
    "calm":       "Breathe easy — here's something peaceful 🌿",
    "excited":    "Full energy! Let's go 🔥",
}

_VALID_STATES = {
    "low_affect", "cheerful", "recovering", "neutral", "positive",
    "joyful", "happy", "content", "sad", "calm", "excited",
}

DEFAULT_LANGUAGE = "english"

# ─────────────────────────────────────────────────────────────────────────────
# Playlist / compilation detection patterns
# Matches: "top 10", "top 20", "100 songs", "50 hits", "1 hour", "2 hours",
#          "playlist", "compilation", "mix"
# Does NOT block simple words like "best" alone.
# ─────────────────────────────────────────────────────────────────────────────
_PLAYLIST_PATTERNS = [
    re.compile(r"\btop\s*\d+\b",           re.IGNORECASE),  # top 10, top 20
    re.compile(r"\d+\s*(songs|hits|tracks)",re.IGNORECASE),  # 100 songs, 50 hits
    re.compile(r"\d+\s*(hour|hours)\b",    re.IGNORECASE),  # 1 hour, 2 hours
    re.compile(r"\bplaylist\b",            re.IGNORECASE),
    re.compile(r"\bcompilation\b",         re.IGNORECASE),
    re.compile(r"\bmix\b",                 re.IGNORECASE),
    re.compile(r"\bnonstop\b",             re.IGNORECASE),
    re.compile(r"\bjukebox\b",             re.IGNORECASE),
    re.compile(r"\bmashup\b",              re.IGNORECASE),
]

# Duration bounds in seconds
_MIN_DURATION_SEC = 2 * 60   # 2 minutes
_MAX_DURATION_SEC = 8 * 60   # 8 minutes


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_excluded_ids(user_id: int, db_session) -> set:
    """Return set of video IDs the user has liked or disliked."""
    try:
        from app.models.liked_song import LikedSong
        from app.models.disliked_song import DislikedSong
        liked    = db_session.query(LikedSong.song_id).filter(LikedSong.user_id == user_id).all()
        disliked = db_session.query(DislikedSong.song_id).filter(DislikedSong.user_id == user_id).all()
        return {r.song_id for r in liked} | {r.song_id for r in disliked}
    except Exception as e:
        print(f"Error loading excluded songs: {e}")
        return set()


def _get_disliked_ids(user_id: int, db_session) -> set:
    """Return ONLY disliked video IDs — these must never appear."""
    try:
        from app.models.disliked_song import DislikedSong
        disliked = db_session.query(DislikedSong.song_id).filter(DislikedSong.user_id == user_id).all()
        return {r.song_id for r in disliked}
    except Exception as e:
        print(f"Error loading disliked songs: {e}")
        return set()


def _build_query(emotional_state: str, language: str) -> str:
    """Build a smart YouTube search query from emotion + language."""
    phrase = _EMOTION_PHRASES.get(emotional_state, "trending popular")
    lang   = (language or DEFAULT_LANGUAGE).strip()
    return f"{phrase} {lang} songs official audio"


def _is_playlist_title(title: str) -> bool:
    """Return True if the title looks like a playlist/compilation, not a real song."""
    for pattern in _PLAYLIST_PATTERNS:
        if pattern.search(title):
            return True
    return False


def _looks_like_real_song(title: str) -> bool:
    """
    Return True if the title follows a typical song format.
    Titles containing ' - ', ' – ', or ' | ' are strong candidates.
    """
    return bool(re.search(r"[\-–|]", title))


def _parse_iso8601_duration(duration: str) -> int:
    """
    Parse ISO 8601 duration string (e.g. PT3M45S) into total seconds.
    Returns 0 if parsing fails.
    """
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duration or "",
        re.IGNORECASE,
    )
    if not match:
        return 0
    hours   = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _fetch_durations(video_ids: List[str], api_key: str) -> Dict[str, int]:
    """
    Batch-fetch video durations from YouTube Data API v3 (videos endpoint).
    Returns {video_id: duration_seconds}.
    """
    import requests

    if not video_ids or not api_key:
        return {}

    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part":  "contentDetails",
                "id":    ",".join(video_ids),
                "key":   api_key,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"YouTube videos endpoint failed ({resp.status_code})")
            return {}

        durations = {}
        for item in resp.json().get("items", []):
            vid_id   = item["id"]
            raw_dur  = item.get("contentDetails", {}).get("duration", "")
            durations[vid_id] = _parse_iso8601_duration(raw_dur)
        return durations

    except Exception as e:
        print(f"Duration fetch error: {e}")
        return {}


def _search_youtube_direct(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search YouTube Data API v3 with music category filter.
    Returns raw video dicts: {video_id, title, artist, embed_url, watch_url}.
    Falls back to empty list if no API key.
    """
    import requests

    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        print("YouTube API key not configured — cannot perform direct search")
        return []

    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part":            "snippet",
                "q":               query,
                "type":            "video",
                "videoCategoryId": "10",        # Music category only
                "maxResults":      max_results,  # Task 1: 20 results
                "key":             api_key,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"YouTube search failed ({resp.status_code}): {resp.text[:200]}")
            return []

        items = resp.json().get("items", [])
        results = []
        for item in items:
            vid_id  = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            if not vid_id:
                continue
            results.append({
                "video_id":  vid_id,
                "title":     snippet.get("title", "Unknown"),
                "artist":    snippet.get("channelTitle", "Unknown Artist"),
                "embed_url": f"https://www.youtube.com/embed/{vid_id}",
                "watch_url": f"https://www.youtube.com/watch?v={vid_id}",
            })
        return results

    except Exception as e:
        print(f"YouTube direct search error: {e}")
        return []


def _filter_and_rank(results: List[Dict], api_key: str) -> List[Dict]:
    """
    Apply quality filters to raw YouTube search results:
      1. Remove playlist/compilation titles
      2. Fetch durations and keep only 2–8 minute videos
      3. Sort: real-song-format titles first, then the rest
    Returns filtered + ranked list (may be shorter than input).
    """
    # Step 1 — remove playlist/compilation titles
    after_title_filter = [r for r in results if not _is_playlist_title(r["title"])]
    print(f"  After title filter: {len(after_title_filter)}/{len(results)} remain")

    if not after_title_filter:
        # All filtered out — skip duration check, return original minus hard blocks
        after_title_filter = results

    # Step 2 — fetch durations and filter by length
    video_ids = [r["video_id"] for r in after_title_filter if r.get("video_id")]
    durations = _fetch_durations(video_ids, api_key) if api_key else {}

    duration_filtered = []
    for r in after_title_filter:
        vid_id = r.get("video_id")
        if not vid_id:
            continue
        dur = durations.get(vid_id)
        if dur is None:
            # Duration unavailable — include with lower confidence
            duration_filtered.append((r, False))
            continue
        if _MIN_DURATION_SEC <= dur <= _MAX_DURATION_SEC:
            duration_filtered.append((r, True))
        else:
            print(f"  Skipping '{r['title']}' — duration {dur}s out of range")

    print(f"  After duration filter: {len(duration_filtered)}/{len(after_title_filter)} remain")

    # If duration filtering removed everything, fall back to title-filtered list
    if not duration_filtered:
        duration_filtered = [(r, False) for r in after_title_filter]

    # Step 3 — sort: confirmed duration + real-song format first
    def _rank_key(item):
        r, dur_ok = item
        song_format = _looks_like_real_song(r["title"])
        # Lower = better: (not dur_ok, not song_format)
        return (not dur_ok, not song_format)

    duration_filtered.sort(key=_rank_key)
    return [r for r, _ in duration_filtered]


def _make_fallback_tracks(emotional_state: str, language: str, count: int = 5) -> List[Dict]:
    """
    No API key fallback — return search-embed URL so the panel still renders.
    """
    phrase = _EMOTION_PHRASES.get(emotional_state, "trending popular")
    lang   = (language or DEFAULT_LANGUAGE).strip()
    query  = urllib.parse.quote_plus(f"{phrase} {lang} songs")
    embed  = f"https://www.youtube.com/embed?listType=search&list={query}"
    watch  = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(f'{phrase} {lang} songs')}"
    return [{
        "title":       f"{phrase.title()} {lang.title()} Music",
        "artist":      "YouTube",
        "video_id":    None,
        "embed_url":   embed,
        "watch_url":   watch,
        "spotify_url": None,
        "track_id":    None,
        "preview_url": None,
        "popularity":  0,
    }]


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def get_recommendation(
    emotional_state: str,
    market: str = "IN",
    user_id: Optional[int] = None,
    db_session=None,
    language: Optional[str] = None,
    smile_score: float = 50.0,
    user=None,
) -> Dict:
    """
    YouTube-only recommendation pipeline.

    Flow:
      emotion → smart query
      → YouTube search (music category, maxResults=20)
      → remove playlist/compilation titles
      → filter by duration (2–8 min)
      → prefer real-song-format titles
      → shuffle
      → filter disliked/excluded IDs
      → return top 5
    """
    if emotional_state not in _VALID_STATES:
        emotional_state = "neutral"

    # Resolve preferred language
    preferred_language = language
    if not preferred_language and user:
        preferred_language = getattr(user, "preferred_music_language", None)
    if not preferred_language:
        preferred_language = DEFAULT_LANGUAGE

    # Excluded IDs (liked + disliked — disliked must NEVER appear)
    excluded_ids: set = set()
    disliked_ids: set = set()
    if user_id and db_session:
        excluded_ids = _get_excluded_ids(user_id, db_session)
        disliked_ids = _get_disliked_ids(user_id, db_session)

    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()

    # Build search query
    query = _build_query(emotional_state, preferred_language)
    print(f"✓ YouTube query: '{query}'")

    # Search YouTube — 20 results for a larger filtering pool
    raw_results = _search_youtube_direct(query, max_results=20)

    if not raw_results:
        print("YouTube search returned no results — using fallback")
        return {
            "message": _MESSAGES.get(emotional_state, "Here are some tracks for you 🎵"),
            "tracks":  _make_fallback_tracks(emotional_state, preferred_language),
            "state":   emotional_state,
        }

    # Apply quality filters (playlist removal + duration check + ranking)
    filtered = _filter_and_rank(raw_results, api_key)

    # Shuffle for variety before applying like/dislike exclusions
    random.shuffle(filtered)

    # Hard exclude disliked; soft exclude liked (avoid repetition)
    clean = [
        r for r in filtered
        if r["video_id"] not in disliked_ids
        and r["video_id"] not in excluded_ids
    ]

    # If soft exclusion removed everything, fall back to only hard-excluding disliked
    if not clean:
        clean = [r for r in filtered if r["video_id"] not in disliked_ids]

    # If still empty (everything disliked), return gracefully
    if not clean:
        return {
            "message": _MESSAGES.get(emotional_state, "Here are some tracks for you 🎵"),
            "tracks":  [],
            "state":   emotional_state,
        }

    # Take top 5
    selected = clean[:5]

    tracks = [
        {
            "title":       r["title"],
            "artist":      r["artist"],
            "video_id":    r["video_id"],
            "embed_url":   r["embed_url"],
            "watch_url":   r["watch_url"],
            "spotify_url": None,
            "track_id":    None,
            "preview_url": None,
            "popularity":  0,
        }
        for r in selected
    ]

    return {
        "message": _MESSAGES.get(emotional_state, "Here are some tracks for you 🎵"),
        "tracks":  tracks,
        "state":   emotional_state,
    }


def get_mood_boost_message(emotional_state: str) -> str:
    return _MESSAGES.get(emotional_state, "Here's a recommendation for you!")

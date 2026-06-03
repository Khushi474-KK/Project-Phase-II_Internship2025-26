"""
Dataset Service
Loads music.csv once at startup and provides emotion-filtered track candidates.
Never reloads the CSV per request — dataset is cached in module-level memory.
"""

import os
import random
import pandas as pd
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Load dataset once at import time
# ---------------------------------------------------------------------------
_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "music.csv")

try:
    _df = pd.read_csv(_CSV_PATH)
    # Normalise column names
    _df.columns = [c.strip() for c in _df.columns]
    # Drop rows missing critical fields
    _df = _df.dropna(subset=["track_name", "artists", "valence", "energy", "popularity"])
    # Deduplicate by track_name + artists so we don't return the same song twice
    _df = _df.drop_duplicates(subset=["track_name", "artists"])
    print(f"✓ music.csv loaded: {len(_df)} unique tracks")
except Exception as e:
    _df = pd.DataFrame()
    print(f"⚠ Failed to load music.csv: {e}")


# ---------------------------------------------------------------------------
# Emotion → audio feature filter ranges
# ---------------------------------------------------------------------------
_EMOTION_FILTERS = {
    "joyful": dict(valence_min=0.75, energy_min=0.65, danceability_min=0.55),
    "happy":  dict(valence_min=0.60, energy_min=0.50, danceability_min=0.45),
    "content":dict(valence_min=0.45, energy_min=0.30),
    "neutral":dict(valence_min=0.35, valence_max=0.65, energy_min=0.30, energy_max=0.65),
    "cheerful":dict(valence_min=0.70, energy_min=0.60, danceability_min=0.55),
    "positive":dict(valence_min=0.55, energy_min=0.45),
    "recovering":dict(valence_min=0.50, energy_min=0.45, tempo_min=100),
    "low_affect":dict(valence_max=0.45, energy_max=0.45),
    "sad":    dict(valence_max=0.40, energy_max=0.40),
    "calm":   dict(energy_max=0.45, acousticness_min=0.40),
    "excited":dict(energy_min=0.75, tempo_min=110),
}

# Emotion → preferred genres (used to bias results when dataset is large)
_EMOTION_GENRES = {
    "joyful":    ["pop", "dance", "happy", "party"],
    "happy":     ["pop", "indie-pop", "soul", "funk"],
    "content":   ["indie", "chill", "acoustic", "folk"],
    "neutral":   ["indie", "chill", "alternative", "folk"],
    "cheerful":  ["pop", "dance", "disco", "funk"],
    "positive":  ["pop", "soul", "r-n-b", "indie-pop"],
    "recovering":["rock", "pop", "alternative", "indie"],
    "low_affect":["acoustic", "ambient", "sleep", "classical"],
    "sad":       ["acoustic", "blues", "classical", "ambient"],
    "calm":      ["acoustic", "ambient", "classical", "sleep"],
    "excited":   ["dance", "edm", "electronic", "party"],
}


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    mask = pd.Series([True] * len(df), index=df.index)
    for key, val in filters.items():
        col, direction = key.rsplit("_", 1)
        if col not in df.columns:
            continue
        if direction == "min":
            mask &= df[col] >= val
        elif direction == "max":
            mask &= df[col] <= val
    return df[mask]


def get_candidates(
    emotional_state: str,
    user_genres: Optional[List[str]] = None,
    excluded_track_names: Optional[set] = None,
    top_n: int = 20,
) -> List[Dict]:
    """
    Return up to `top_n` candidate tracks from the dataset for the given emotion.

    Priority:
      1. Apply audio feature filters for the emotion
      2. Bias toward user_genres (or emotion default genres) if available
      3. Sort by popularity descending
      4. Exclude already-seen track names
      5. Return a random sample of top_n from the top 100 results for variety
    """
    if _df.empty:
        return []

    filters = _EMOTION_FILTERS.get(emotional_state, _EMOTION_FILTERS["neutral"])
    filtered = _apply_filters(_df, filters)

    # If too few results, relax filters by dropping danceability/tempo constraints
    if len(filtered) < 10:
        relaxed = {k: v for k, v in filters.items()
                   if not k.startswith("danceability") and not k.startswith("tempo")}
        filtered = _apply_filters(_df, relaxed)

    # If still too few, use full dataset
    if len(filtered) < 5:
        filtered = _df.copy()

    # Bias toward preferred genres
    genres = user_genres or _EMOTION_GENRES.get(emotional_state, [])
    if genres and "track_genre" in filtered.columns:
        genre_mask = filtered["track_genre"].str.lower().isin([g.lower() for g in genres])
        genre_filtered = filtered[genre_mask]
        if len(genre_filtered) >= 5:
            filtered = genre_filtered

    # Exclude already-seen tracks
    if excluded_track_names:
        filtered = filtered[~filtered["track_name"].isin(excluded_track_names)]

    # Sort by popularity, take top 100, then random sample for variety
    top = filtered.sort_values("popularity", ascending=False).head(100)
    sample_size = min(top_n, len(top))
    sample = top.sample(n=sample_size) if sample_size > 0 else top

    results = []
    for _, row in sample.iterrows():
        results.append({
            "track_name": str(row["track_name"]),
            "artists":    str(row["artists"]),
            "album_name": str(row.get("album_name", "")),
            "popularity": int(row.get("popularity", 0)),
            "valence":    float(row.get("valence", 0)),
            "energy":     float(row.get("energy", 0)),
            "track_genre":str(row.get("track_genre", "")),
        })

    return results


def is_loaded() -> bool:
    return not _df.empty

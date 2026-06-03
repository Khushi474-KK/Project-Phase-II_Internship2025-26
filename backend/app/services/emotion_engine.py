"""
Emotional State Engine
Computes emotional state based on smile metrics without modifying detection logic
"""

from typing import Optional, List


def compute_emotional_state(
    smile_probability: float,
    smile_growth_rate: float = 0.0,
    smile_timeline: Optional[List[float]] = None
) -> str:
    """
    Compute emotional state based on smile metrics.
    
    Args:
        smile_probability: Current smile probability (0-1)
        smile_growth_rate: Rate of smile growth during capture
        smile_timeline: Optional list of smile probabilities over time
        
    Returns:
        str: Emotional state classification
             - "cheerful": Very happy, high smile probability
             - "positive": Generally positive mood
             - "recovering": Mood improving over time
             - "low_affect": Low emotional expression
             - "neutral": Balanced emotional state
    """
    # Base classification on current smile probability
    if smile_probability > 0.85:
        base_state = "cheerful"
    elif smile_probability >= 0.5 and smile_probability <= 0.85:
        base_state = "positive"
    elif smile_probability < 0.3:
        base_state = "low_affect"
    else:
        base_state = "neutral"
    
    # If timeline provided, analyze temporal patterns
    if smile_timeline and len(smile_timeline) > 0:
        # Calculate average smile
        avg_smile = sum(smile_timeline) / len(smile_timeline)
        
        # Calculate variance
        variance = sum((x - avg_smile) ** 2 for x in smile_timeline) / len(smile_timeline)
        
        # Calculate growth rate (last - first)
        growth_rate = smile_timeline[-1] - smile_timeline[0]
        
        # Check for recovering state
        if growth_rate > 0.2 and avg_smile < 0.6:
            return "recovering"
        
        # Refine cheerful classification
        if avg_smile > 0.8 and variance < 0.02:
            return "cheerful"
    
    return base_state


def get_emotional_state_description(state: str) -> str:
    """
    Get human-readable description of emotional state.
    
    Args:
        state: Emotional state
        
    Returns:
        str: Description
    """
    descriptions = {
        "cheerful": "Radiating joy and happiness",
        "positive": "Generally positive and content",
        "recovering": "Mood improving and brightening",
        "low_affect": "Subdued emotional expression",
        "neutral": "Balanced and calm"
    }
    
    return descriptions.get(state, "Neutral emotional state")


def compute_smile_timeline_metrics(smile_timeline: List[float]) -> dict:
    """
    Compute metrics from smile timeline.
    
    Args:
        smile_timeline: List of smile probabilities
        
    Returns:
        dict: Timeline metrics
    """
    if not smile_timeline or len(smile_timeline) == 0:
        return {
            "avg_smile": 0.0,
            "peak_smile": 0.0,
            "variance": 0.0,
            "growth_rate": 0.0,
            "timeline_length": 0
        }
    
    avg_smile = sum(smile_timeline) / len(smile_timeline)
    peak_smile = max(smile_timeline)
    variance = sum((x - avg_smile) ** 2 for x in smile_timeline) / len(smile_timeline)
    growth_rate = smile_timeline[-1] - smile_timeline[0]
    
    return {
        "avg_smile": round(avg_smile, 3),
        "peak_smile": round(peak_smile, 3),
        "variance": round(variance, 4),
        "growth_rate": round(growth_rate, 3),
        "timeline_length": len(smile_timeline)
    }

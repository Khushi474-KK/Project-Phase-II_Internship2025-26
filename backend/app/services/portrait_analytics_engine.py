"""
Portrait Analytics Engine
Multi-factor portrait quality analysis
Separate from existing quality_score logic - additive only
Enhanced with varied explanation vocabulary
"""

import cv2
import numpy as np
import random
from typing import Dict, Tuple, Optional


# ============================================================================
# EXPLANATION VOCABULARY POOLS
# Rich variation for analytics explanations
# ============================================================================

# SMILE EXPLANATIONS
SMILE_HIGH_EXPLANATIONS = [
    "Your bright expression greatly elevated the score.",
    "Excellent smile detection contributed significantly to the rating.",
    "That radiant smile boosted the overall quality substantially.",
    "Your joyful expression enhanced the capture tremendously.",
    "Strong smile presence added major value to the score.",
    "Your beaming smile was a key factor in the high rating.",
    "Exceptional smile detection drove the score upward.",
    "Your genuine smile made a significant positive impact.",
    "That brilliant expression contributed heavily to the result.",
    "Your cheerful demeanor elevated the quality considerably."
]

SMILE_MODERATE_EXPLANATIONS = [
    "Good smile presence enhanced the overall rating.",
    "Your pleasant expression contributed positively to the score.",
    "Smile detection added value to the final result.",
    "Your expression provided a nice boost to the rating.",
    "Moderate smile presence improved the overall quality.",
    "Your friendly demeanor enhanced the capture.",
    "Smile detection contributed favorably to the score.",
    "Your positive expression added to the final rating.",
    "Good facial expression improved the overall result.",
    "Your smile provided a solid contribution to the score."
]

SMILE_LOW_EXPLANATIONS = [
    "Limited smile detection reduced the overall score.",
    "Subtle expression resulted in a lower smile contribution.",
    "Minimal smile presence affected the rating moderately.",
    "Neutral expression limited the smile score impact.",
    "Restrained smile detection influenced the final result.",
    "Subdued expression reduced the smile component.",
    "Limited facial expression affected the overall rating.",
    "Neutral demeanor resulted in lower smile contribution.",
    "Minimal smile presence impacted the score.",
    "Subtle expression limited the smile rating factor."
]

# LIGHTING EXPLANATIONS
LIGHTING_HIGH_EXPLANATIONS = [
    "Superior lighting balance boosted the quality score.",
    "Excellent illumination enhanced the overall rating significantly.",
    "Optimal exposure conditions elevated the capture quality.",
    "Balanced exposure improved overall clarity substantially.",
    "Perfect lighting setup contributed to the high score.",
    "Ideal brightness levels enhanced the final rating.",
    "Well-balanced illumination boosted the quality considerably.",
    "Optimal light distribution improved the overall result.",
    "Excellent exposure balance elevated the score.",
    "Superior brightness control enhanced the capture quality."
]

LIGHTING_LOW_EXPLANATIONS = [
    "Suboptimal lighting conditions affected the rating.",
    "Challenging illumination reduced the overall score.",
    "Uneven exposure impacted the quality assessment.",
    "Limited lighting balance influenced the final rating.",
    "Difficult light conditions affected the score moderately.",
    "Inconsistent illumination reduced the overall quality.",
    "Subpar exposure conditions impacted the result.",
    "Challenging brightness levels affected the rating.",
    "Unbalanced lighting influenced the final score.",
    "Limited exposure control reduced the quality rating."
]

# SHARPNESS EXPLANATIONS
SHARPNESS_HIGH_EXPLANATIONS = [
    "Excellent image sharpness improved the final score.",
    "Crystal-clear detail enhanced the overall rating.",
    "Outstanding focus quality boosted the score significantly.",
    "Superb clarity contributed to the high rating.",
    "Exceptional sharpness elevated the capture quality.",
    "Perfect focus added substantial value to the score.",
    "Remarkable detail preservation improved the result.",
    "Excellent edge definition enhanced the overall quality.",
    "Superior sharpness contributed heavily to the rating.",
    "Outstanding clarity boosted the final score considerably."
]

SHARPNESS_LOW_EXPLANATIONS = [
    "Image blur or motion reduced sharpness score.",
    "Slight motion blur reduced sharpness impact.",
    "Limited clarity affected the overall rating.",
    "Soft focus influenced the sharpness component.",
    "Minor blur reduced the detail score.",
    "Reduced sharpness impacted the final rating.",
    "Slight defocus affected the clarity assessment.",
    "Motion artifacts reduced the sharpness contribution.",
    "Limited edge definition impacted the score.",
    "Soft detail affected the overall quality rating."
]

# ALIGNMENT EXPLANATIONS
ALIGNMENT_HIGH_EXPLANATIONS = [
    "Perfect face centering contributed to higher ranking.",
    "Ideal composition strengthened the overall score.",
    "Excellent framing enhanced the capture quality.",
    "Centered framing strengthened the composition.",
    "Optimal positioning boosted the final rating.",
    "Well-balanced composition improved the score.",
    "Perfect subject placement elevated the quality.",
    "Ideal centering contributed significantly to the rating.",
    "Excellent spatial balance enhanced the result.",
    "Optimal framing added value to the final score."
]

ALIGNMENT_LOW_EXPLANATIONS = [
    "Slight off-center alignment reduced the score.",
    "Asymmetric composition affected the rating moderately.",
    "Off-center positioning influenced the final result.",
    "Unbalanced framing reduced the composition score.",
    "Slight misalignment impacted the overall rating.",
    "Eccentric positioning affected the quality assessment.",
    "Off-center placement reduced the final score.",
    "Uneven composition influenced the rating.",
    "Asymmetric framing impacted the result.",
    "Slight positioning offset affected the score."
]


def compute_lighting_score(image: np.ndarray, face_bbox: Optional[Tuple[int, int, int, int]] = None) -> float:
    """
    Compute face-aware lighting score based on face illumination quality.
    Evaluates lighting primarily on the face region relative to background.
    
    Args:
        image: BGR image array
        face_bbox: Face bounding box (x, y, width, height) - optional
        
    Returns:
        float: Lighting score (0-100)
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # If no face bbox provided, fall back to global brightness
        if face_bbox is None:
            mean_brightness = np.mean(gray)
            brightness_score = 100 - abs(mean_brightness - 135)
            return max(0.0, min(100.0, brightness_score))
        
        x, y, w, h = face_bbox
        
        # Extract face region
        face_gray = gray[y:y+h, x:x+w]
        
        # Compute face brightness
        face_brightness = np.mean(face_gray)
        
        # Compute background brightness (excluding face region)
        background_mask = np.ones_like(gray, dtype=bool)
        background_mask[y:y+h, x:x+w] = False
        background_pixels = gray[background_mask]
        
        if len(background_pixels) > 0:
            background_brightness = np.mean(background_pixels)
        else:
            background_brightness = face_brightness
        
        # Compute face exposure score
        # Optimal face brightness range is approximately 90-140 in grayscale
        optimal_brightness = 110
        exposure_deviation = abs(face_brightness - optimal_brightness)
        exposure_score = max(0.0, 100.0 - exposure_deviation)
        
        # Compute background penalty
        # If background is significantly brighter than face, apply penalty
        brightness_diff = background_brightness - face_brightness
        background_penalty = max(0.0, brightness_diff * 0.5)
        
        # Compute face illumination uniformity
        # Split face vertically into left and right halves
        mid_w = w // 2
        left_face = face_gray[:, :mid_w]
        right_face = face_gray[:, mid_w:]
        
        left_brightness = np.mean(left_face)
        right_brightness = np.mean(right_face)
        
        # Penalty for uneven illumination across face
        uniformity_penalty = abs(left_brightness - right_brightness) * 0.3
        
        # Compute final lighting score
        lighting_score = exposure_score - background_penalty - uniformity_penalty
        
        # Clamp between 0 and 100
        lighting_score = max(0.0, min(100.0, lighting_score))
        
        return lighting_score
    
    except Exception as e:
        print(f"Error computing face-aware lighting score: {e}")
        return 50.0


def compute_sharpness_score(image: np.ndarray) -> float:
    """
    Compute sharpness score using Laplacian variance.
    
    Args:
        image: BGR image array
        
    Returns:
        float: Sharpness score (0-100)
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Compute Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize to 0-100 scale
        # Higher variance = sharper image
        # Typical range: 0-500 for variance
        score = min(100.0, (variance / 500.0) * 100.0)
        
        return max(0.0, min(100.0, score))
    
    except Exception as e:
        print(f"Error computing sharpness score: {e}")
        return 50.0


def compute_alignment_score(
    face_bbox: Tuple[int, int, int, int],
    frame_width: int,
    frame_height: int
) -> float:
    """
    Compute alignment score based on face center deviation from frame center.
    
    Args:
        face_bbox: Face bounding box (x, y, width, height)
        frame_width: Frame width
        frame_height: Frame height
        
    Returns:
        float: Alignment score (0-100)
    """
    try:
        x, y, w, h = face_bbox
        
        # Calculate face center
        face_center_x = x + w / 2
        face_center_y = y + h / 2
        
        # Calculate frame center
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2
        
        # Calculate deviation from center (normalized)
        deviation_x = abs(face_center_x - frame_center_x) / frame_width
        deviation_y = abs(face_center_y - frame_center_y) / frame_height
        
        # Combined deviation (weighted more on horizontal)
        total_deviation = (deviation_x * 0.6 + deviation_y * 0.4)
        
        # Score inversely proportional to deviation
        # Perfect center = 100, edges = lower score
        score = max(0.0, 100.0 - (total_deviation * 200.0))
        
        return max(0.0, min(100.0, score))
    
    except Exception as e:
        print(f"Error computing alignment score: {e}")
        return 50.0


def calculate_final_score(
    smile_probability: float,
    lighting_score: float,
    sharpness_score: float,
    alignment_score: float
) -> float:
    """
    Calculate final portrait score using weighted combination.
    
    Args:
        smile_probability: Smile probability (0-1)
        lighting_score: Lighting score (0-100)
        sharpness_score: Sharpness score (0-100)
        alignment_score: Alignment score (0-100)
        
    Returns:
        float: Final score (0-100)
    """
    # Convert smile probability to 0-100 scale
    smile_score = smile_probability * 100.0
    
    # Weighted combination
    final_score = (
        0.35 * smile_score +
        0.25 * lighting_score +
        0.20 * sharpness_score +
        0.20 * alignment_score
    )
    
    return max(0.0, min(100.0, final_score))


def analyze_portrait(
    image: np.ndarray,
    face_bbox: Tuple[int, int, int, int],
    smile_probability: float
) -> Dict:
    """
    Perform complete portrait analysis.
    
    Args:
        image: BGR image array
        face_bbox: Face bounding box (x, y, width, height)
        smile_probability: Smile probability (0-1)
        
    Returns:
        dict: Complete analytics
              {
                  "lighting": float,
                  "sharpness": float,
                  "alignment": float,
                  "smile_score": float,
                  "final_score": float
              }
    """
    try:
        frame_height, frame_width = image.shape[:2]
        
        # Compute individual scores (pass face_bbox to lighting)
        lighting_score = compute_lighting_score(image, face_bbox)
        sharpness_score = compute_sharpness_score(image)
        alignment_score = compute_alignment_score(face_bbox, frame_width, frame_height)
        
        # Calculate final score
        final_score = calculate_final_score(
            smile_probability,
            lighting_score,
            sharpness_score,
            alignment_score
        )
        
        return {
            "lighting": round(lighting_score, 2),
            "sharpness": round(sharpness_score, 2),
            "alignment": round(alignment_score, 2),
            "smile_score": round(smile_probability * 100, 2),
            "final_score": round(final_score, 2)
        }
    
    except Exception as e:
        print(f"Error analyzing portrait: {e}")
        return {
            "lighting": 50.0,
            "sharpness": 50.0,
            "alignment": 50.0,
            "smile_score": smile_probability * 100,
            "final_score": 50.0
        }


def generate_score_explanation(analytics: Dict) -> list:
    """
    Generate human-readable explanation for scores with rich vocabulary variation.
    Uses randomized selection from explanation pools for natural variety.
    
    Args:
        analytics: Analytics dictionary
        
    Returns:
        list: List of explanation strings (varied vocabulary)
    """
    explanations = []
    used_indices = set()  # Track used indices to avoid repetition
    
    # Helper function to get unique random choice
    def get_unique_choice(pool, category):
        available_indices = [i for i in range(len(pool)) if (category, i) not in used_indices]
        if not available_indices:
            # If all used, reset for this category
            available_indices = list(range(len(pool)))
        
        idx = random.choice(available_indices)
        used_indices.add((category, idx))
        return pool[idx]
    
    # Smile explanation
    smile_score = analytics.get("smile_score", 0)
    if smile_score >= 80:
        explanations.append(get_unique_choice(SMILE_HIGH_EXPLANATIONS, "smile_high"))
    elif smile_score >= 60:
        explanations.append(get_unique_choice(SMILE_MODERATE_EXPLANATIONS, "smile_mod"))
    elif smile_score < 40:
        explanations.append(get_unique_choice(SMILE_LOW_EXPLANATIONS, "smile_low"))
    
    # Lighting explanation
    lighting = analytics.get("lighting", 0)
    if lighting >= 80:
        explanations.append(get_unique_choice(LIGHTING_HIGH_EXPLANATIONS, "light_high"))
    elif lighting < 50:
        explanations.append(get_unique_choice(LIGHTING_LOW_EXPLANATIONS, "light_low"))
    
    # Sharpness explanation
    sharpness = analytics.get("sharpness", 0)
    if sharpness >= 75:
        explanations.append(get_unique_choice(SHARPNESS_HIGH_EXPLANATIONS, "sharp_high"))
    elif sharpness < 50:
        explanations.append(get_unique_choice(SHARPNESS_LOW_EXPLANATIONS, "sharp_low"))
    
    # Alignment explanation
    alignment = analytics.get("alignment", 0)
    if alignment >= 85:
        explanations.append(get_unique_choice(ALIGNMENT_HIGH_EXPLANATIONS, "align_high"))
    elif alignment < 60:
        explanations.append(get_unique_choice(ALIGNMENT_LOW_EXPLANATIONS, "align_low"))
    
    return explanations

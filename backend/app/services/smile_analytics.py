import cv2
from deepface import DeepFace

def compute_smile_strength(face_image):
    """
    Compute smile strength using DeepFace emotion analysis.
    Returns numeric smile strength score (0-100).
    
    Args:
        face_image: BGR image of face
        
    Returns:
        float: Smile strength score (0-100)
               Returns 0 if analysis fails
    """
    try:
        result = DeepFace.analyze(
            img_path=face_image,
            actions=["emotion"],
            enforce_detection=False
        )
        
        # Extract happy emotion probability
        happy_score = result[0]["emotion"]["happy"]
        
        # Return as 0-100 scale
        return float(happy_score)
    
    except Exception:
        return 0.0


def classify_smile_level(smile_strength):
    """
    Classify smile strength into deterministic levels.
    
    Args:
        smile_strength: Numeric smile strength (0-100)
        
    Returns:
        str: Smile level classification
             "Strong Smile" (> 75)
             "Moderate Smile" (40-75)
             "Subtle Smile" (< 40)
    """
    if smile_strength > 75:
        return "Strong Smile"
    elif smile_strength >= 40:
        return "Moderate Smile"
    else:
        return "Subtle Smile"

import cv2
from deepface import DeepFace

def detect_gender(face_image):
    """
    Detect gender using DeepFace.
    
    Args:
        face_image: BGR image of face
        
    Returns:
        str: "Man" or "Woman"
    """
    try:
        result = DeepFace.analyze(
            img_path=face_image,
            actions=["gender"],
            enforce_detection=False
        )
        
        gender = result[0]["dominant_gender"]
        return gender.capitalize()
    
    except Exception:
        return "Unknown"

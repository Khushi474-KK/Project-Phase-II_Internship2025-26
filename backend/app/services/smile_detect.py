import cv2
from deepface import DeepFace

def detect_smile(face_gray):
    face_bgr = cv2.cvtColor(face_gray, cv2.COLOR_GRAY2BGR)

    try:
        result = DeepFace.analyze(
            img_path=face_bgr,
            actions=["emotion"],
            enforce_detection=False
        )

        emotion = result[0]["dominant_emotion"]
        return emotion == "happy"

    except Exception:
        return False

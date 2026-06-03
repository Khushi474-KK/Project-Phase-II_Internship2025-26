import cv2
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "models")

AGE_PROTO = os.path.join(MODEL_DIR, "age_deploy.prototxt")
AGE_MODEL = os.path.join(MODEL_DIR, "age_net.caffemodel")

AGE_BUCKETS = [
    "(0-2)", "(4-6)", "(8-12)", "(15-20)",
    "(25-32)", "(38-43)", "(48-53)", "(60-100)"
]

if not os.path.exists(AGE_PROTO):
    raise FileNotFoundError(f"Missing: {AGE_PROTO}")

if not os.path.exists(AGE_MODEL):
    raise FileNotFoundError(f"Missing: {AGE_MODEL}")

age_net = cv2.dnn.readNetFromCaffe(AGE_PROTO, AGE_MODEL)

def predict_age(face_bgr):
    blob = cv2.dnn.blobFromImage(
        face_bgr,
        scalefactor=1.0,
        size=(227, 227),
        mean=(78.4263377603, 87.7689143744, 114.895847746),
        swapRB=False
    )

    age_net.setInput(blob)
    preds = age_net.forward()

    idx = preds[0].argmax()
    return AGE_BUCKETS[idx], float(preds[0][idx])

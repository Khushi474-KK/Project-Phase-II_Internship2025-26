import cv2

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

if face_detector.empty():
    exit()


def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    faces = sorted(faces, key=lambda x: x[0])

    output = []

    for face_id, (x, y, w, h) in enumerate(faces):
        output.append({
            "id": face_id,
            "bbox": (x, y, w, h),
            "gray_face": gray[y:y+h, x:x+w]
        })

    return output

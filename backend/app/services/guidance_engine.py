import cv2

def generate_guidance(frame, faces, blur_score, smile_counters):
    """
    Generate live camera coaching hints based on frame analysis.
    Returns ONLY one dominant guidance string per frame.
    
    Args:
        frame: Current camera frame (BGR)
        faces: List of detected faces with bbox info
        blur_score: Current frame blur score
        smile_counters: Dictionary of smile counters per face
        
    Returns:
        str: Single guidance hint or empty string if no guidance needed
    """
    frame_height, frame_width = frame.shape[:2]
    
    # Priority 1: Check blur (camera stability)
    if blur_score < 50:
        return "Hold camera steady"
    
    # Priority 2: Check if no faces detected
    if len(faces) == 0:
        return ""
    
    # Priority 3: Check face framing issues
    for face in faces:
        x, y, w, h = face["bbox"]
        
        # Check if face is partially outside frame
        if x < 10 or y < 10 or (x + w) > (frame_width - 10) or (y + h) > (frame_height - 10):
            return "Adjust framing"
        
        # Check if face is too small (less than 10% of frame width)
        if w < (frame_width * 0.1):
            return "Move closer"
    
    # Priority 4: Check for smiles
    all_smiling = True
    for face in faces:
        face_id = face["id"]
        if face_id in smile_counters and smile_counters[face_id] == 0:
            all_smiling = False
            break
    
    if not all_smiling:
        return "Say cheese 😄"
    
    # Priority 5: Check lighting (simple heuristic - mean brightness)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    
    if mean_brightness < 60:
        return "Try better lighting"
    
    # Priority 6: Check multiple faces alignment
    if len(faces) > 1:
        # Calculate center of mass for all faces
        centers = []
        for face in faces:
            x, y, w, h = face["bbox"]
            center_x = x + w // 2
            center_y = y + h // 2
            centers.append((center_x, center_y))
        
        # Check if faces are spread too far apart
        avg_x = sum(c[0] for c in centers) / len(centers)
        avg_y = sum(c[1] for c in centers) / len(centers)
        
        max_distance = 0
        for cx, cy in centers:
            distance = ((cx - avg_x) ** 2 + (cy - avg_y) ** 2) ** 0.5
            max_distance = max(max_distance, distance)
        
        # If faces are too spread out (more than 30% of frame width)
        if max_distance > (frame_width * 0.3):
            return "Center all faces"
    
    # No guidance needed
    return ""

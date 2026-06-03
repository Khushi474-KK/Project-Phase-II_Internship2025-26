import cv2

def measure_blur(image):
    """
    Measure image blur using Variance of Laplacian.
    
    Args:
        image: BGR image
        
    Returns:
        float: Blur score
            < 50: Poor quality
            50-150: Acceptable quality
            > 150: Good quality
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

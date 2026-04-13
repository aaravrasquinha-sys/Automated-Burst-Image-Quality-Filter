import cv2
import numpy as np

def calculate_sharpness(image):
    """
    Standardizes image size and calculates sharpness using Laplacian Variance.
    The Gaussian Blur prevents digital 'noise' from inflating the score.
    """
    # 1. Resize for consistent mathematical comparison (1000px wide)
    height, width = image.shape[:2]
    new_width = 1000
    new_height = int((new_width / width) * height)
    resized = cv2.resize(image, (new_width, new_height))

    # 2. Convert to Grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # 3. Apply Gaussian Blur to smooth out digital grain/noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # 4. Calculate Variance of Laplacian
    # Higher variance = sharper edges = better focus
    return cv2.Laplacian(blurred, cv2.CV_64F).var()
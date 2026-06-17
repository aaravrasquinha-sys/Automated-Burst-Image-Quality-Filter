"""
autoburstfilter/filters.py
--------------------------
Image quality scoring algorithms.

The sharpness pipeline mirrors what a professional photographer does by eye:
normalise scale → remove sensor noise → measure edge definition.
"""

import cv2
import numpy as np


def calculate_sharpness(image: np.ndarray) -> float:
    """
    Estimate perceived sharpness of a BGR image via Laplacian variance.

    Pipeline
    --------
    1. **Normalise** – resize to a 1000-px-wide standard so that images from
       different camera sensors (24 MP vs 45 MP) are scored on equal footing.
    2. **Denoise** – apply a mild Gaussian blur (3×3) to suppress high-frequency
       sensor noise that would otherwise inflate the Laplacian response.
    3. **Score** – compute the variance of the Laplacian.  A sharp image has
       strong, well-defined edges ⟹ high variance; a blurry one does not.

    Parameters
    ----------
    image : np.ndarray
        BGR image as returned by ``cv2.imread`` or ``rawpy`` post-processing.

    Returns
    -------
    float
        Sharpness score (higher ⟹ sharper).  Typical ranges:
        * > 1000 – tack-sharp
        * 500–1000 – acceptable
        * < 500  – noticeably blurry

    Examples
    --------
    >>> import cv2
    >>> from autoburstfilter.filters import calculate_sharpness
    >>> img = cv2.imread("photo.jpg")
    >>> score = calculate_sharpness(img)
    >>> print(f"Sharpness: {score:.1f}")
    """
    if image is None or image.size == 0:
        raise ValueError("Received an empty or None image.")

    height, width = image.shape[:2]
    if width == 0:
        raise ValueError("Image has zero width.")

    # --- 1. Normalise ---
    new_width = 1000
    new_height = int((new_width / width) * height)
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # --- 2. Denoise ---
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # --- 3. Score ---
    return float(cv2.Laplacian(blurred, cv2.CV_64F).var())

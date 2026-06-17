"""
autoburstfilter/loader.py
-------------------------
Unified image loading for JPEG, PNG, and professional RAW formats (CR2/CR3).

RAW files are decoded with ``rawpy`` using the camera's own white-balance
metadata so that the sharpness score reflects the real-world scene, not an
arbitrary in-software interpretation.
"""

import os

import cv2
import numpy as np
import rawpy

RAW_EXTENSIONS = frozenset({".cr2", ".cr3"})
SUPPORTED_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png"}) | RAW_EXTENSIONS


def load_bgr(filepath: str) -> np.ndarray | None:
    """
    Load *any* supported image file and return a BGR NumPy array.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the image.

    Returns
    -------
    np.ndarray or None
        BGR uint8 array on success, ``None`` if the file cannot be decoded.

    Raises
    ------
    ValueError
        If the file extension is not in ``SUPPORTED_EXTENSIONS``.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension '{ext}'. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    try:
        if ext in RAW_EXTENSIONS:
            return _load_raw(filepath)
        return _load_standard(filepath)
    except Exception:
        return None


def _load_raw(filepath: str) -> np.ndarray | None:
    """Decode a RAW (CR2/CR3) file via rawpy → BGR."""
    with rawpy.imread(filepath) as raw:
        rgb = raw.postprocess(use_camera_wb=True, bright=1.0)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _load_standard(filepath: str) -> np.ndarray | None:
    """Decode a JPEG/PNG via OpenCV."""
    img = cv2.imread(filepath)
    return img  # None if file missing or corrupt


def is_supported(filename: str) -> bool:
    """Return True if the filename has a supported image extension."""
    return os.path.splitext(filename)[1].lower() in SUPPORTED_EXTENSIONS

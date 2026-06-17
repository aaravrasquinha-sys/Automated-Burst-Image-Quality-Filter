"""
AutoBurstFilter
===============
Automated sharpness-based image culling for wildlife, sports, and action photography.

Quick start
-----------
>>> from autoburstfilter.ranker import rank_burst, export_champion
>>> results = rank_burst("data/input")
>>> dest = export_champion(results, "data/output")
>>> print(f"Champion exported to: {dest}")
"""

from .filters import calculate_sharpness
from .loader import load_bgr, is_supported
from .ranker import rank_burst, export_champion, ImageResult

__all__ = [
    "calculate_sharpness",
    "load_bgr",
    "is_supported",
    "rank_burst",
    "export_champion",
    "ImageResult",
]

__version__ = "1.0.0"
__author__ = "Aarav Rasquinha"

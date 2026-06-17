"""
autoburstfilter/ranker.py
-------------------------
Ranks a burst of images by sharpness and identifies the champion frame.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .filters import calculate_sharpness
from .loader import load_bgr, is_supported


@dataclass(order=True)
class ImageResult:
    """Holds the sharpness score and metadata for a single image."""

    score: float
    filename: str = field(compare=False)
    filepath: str = field(compare=False)


def rank_burst(
    input_dir: str,
    files: Sequence[str] | None = None,
) -> list[ImageResult]:
    """
    Score every supported image in *input_dir* and return results sorted
    from sharpest to blurriest.

    Parameters
    ----------
    input_dir : str
        Directory containing the burst images.
    files : sequence of str, optional
        Restrict scoring to this explicit list of filenames.  Defaults to
        every supported file found in *input_dir*.

    Returns
    -------
    list[ImageResult]
        Sorted descending by sharpness score (index 0 is the champion).
    """
    if files is None:
        files = [f for f in sorted(os.listdir(input_dir)) if is_supported(f)]

    results: list[ImageResult] = []

    for filename in files:
        filepath = os.path.join(input_dir, filename)
        bgr = load_bgr(filepath)
        if bgr is None:
            continue
        try:
            score = calculate_sharpness(bgr)
        except ValueError:
            continue
        results.append(ImageResult(score=score, filename=filename, filepath=filepath))

    results.sort(reverse=True)
    return results


def export_champion(results: list[ImageResult], output_dir: str) -> str | None:
    """
    Copy the top-ranked image to *output_dir*.

    Parameters
    ----------
    results : list[ImageResult]
        Sorted output from :func:`rank_burst`.
    output_dir : str
        Destination directory (created if absent).

    Returns
    -------
    str or None
        Destination path of the exported champion, or ``None`` if *results*
        is empty.
    """
    if not results:
        return None

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    champion = results[0]
    dest = os.path.join(output_dir, champion.filename)
    shutil.copy2(champion.filepath, dest)
    return dest

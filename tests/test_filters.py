"""
tests/test_filters.py
---------------------
Unit tests for the sharpness scoring pipeline.
"""

import numpy as np
import pytest

from autoburstfilter.filters import calculate_sharpness


def _solid(value: int = 128) -> np.ndarray:
    """Return a 200×200 solid-grey BGR image (blurry by definition)."""
    return np.full((200, 200, 3), value, dtype=np.uint8)


def _checkerboard(cell: int = 4) -> np.ndarray:
    """Return a 200×200 high-contrast checkerboard (sharp by definition)."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    for y in range(200):
        for x in range(200):
            if (x // cell + y // cell) % 2 == 0:
                img[y, x] = 255
    return img


class TestCalculateSharpness:
    def test_sharp_image_scores_higher_than_blurry(self):
        sharp_score = calculate_sharpness(_checkerboard())
        blurry_score = calculate_sharpness(_solid())
        assert sharp_score > blurry_score

    def test_returns_float(self):
        score = calculate_sharpness(_solid())
        assert isinstance(score, float)

    def test_solid_image_near_zero(self):
        score = calculate_sharpness(_solid())
        assert score < 10.0  # uniform image has almost no edges

    def test_raises_on_none(self):
        with pytest.raises((ValueError, AttributeError)):
            calculate_sharpness(None)  # type: ignore[arg-type]

    def test_raises_on_empty(self):
        with pytest.raises((ValueError, Exception)):
            calculate_sharpness(np.array([]))

    def test_non_square_image(self):
        """Landscape-ratio images should be handled correctly."""
        img = _checkerboard()[:100, :]  # 100×200
        score = calculate_sharpness(img)
        assert score > 0

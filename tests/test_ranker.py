"""
tests/test_ranker.py
--------------------
Integration tests for rank_burst and export_champion.
"""

import os
import shutil
import tempfile

import cv2
import numpy as np
import pytest

from autoburstfilter.ranker import rank_burst, export_champion


def _write_image(directory: str, filename: str, sharpness_level: str) -> str:
    """Write a synthetic JPEG to *directory* and return its path."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    if sharpness_level == "sharp":
        # checkerboard – lots of edges
        for y in range(200):
            for x in range(200):
                if (x // 4 + y // 4) % 2 == 0:
                    img[y, x] = 255
    elif sharpness_level == "medium":
        img[:, :] = 128
        img[50:150, 50:150] = 200
    # "blurry" stays as zeros

    path = os.path.join(directory, filename)
    cv2.imwrite(path, img)
    return path


class TestRankBurst:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_champion_is_sharpest(self):
        _write_image(self.tmp, "sharp.jpg", "sharp")
        _write_image(self.tmp, "blurry.jpg", "blurry")
        results = rank_burst(self.tmp)
        assert results[0].filename == "sharp.jpg"

    def test_returns_all_valid_images(self):
        for name, level in [("a.jpg", "sharp"), ("b.jpg", "medium"), ("c.jpg", "blurry")]:
            _write_image(self.tmp, name, level)
        results = rank_burst(self.tmp)
        assert len(results) == 3

    def test_empty_directory_returns_empty_list(self):
        results = rank_burst(self.tmp)
        assert results == []

    def test_scores_are_descending(self):
        for name, level in [("x.jpg", "sharp"), ("y.jpg", "medium"), ("z.jpg", "blurry")]:
            _write_image(self.tmp, name, level)
        results = rank_burst(self.tmp)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)


class TestExportChampion:
    def setup_method(self):
        self.src = tempfile.mkdtemp()
        self.dst = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.src, ignore_errors=True)
        shutil.rmtree(self.dst, ignore_errors=True)

    def test_exports_champion_file(self):
        _write_image(self.src, "best.jpg", "sharp")
        _write_image(self.src, "worst.jpg", "blurry")
        results = rank_burst(self.src)
        dest = export_champion(results, self.dst)
        assert dest is not None
        assert os.path.isfile(dest)
        assert os.path.basename(dest) == results[0].filename

    def test_empty_results_returns_none(self):
        dest = export_champion([], self.dst)
        assert dest is None

# Architecture & Algorithm Notes

This document expands on the design decisions behind AutoBurstFilter for
readers who want more depth than the README provides — useful context for
anyone reviewing this as a portfolio piece (e.g. graduate admissions, technical
interviews).

---

## 1. Why Laplacian Variance?

Focus/sharpness estimation is a classical problem in computational
photography and autofocus systems. Common approaches include:

| Method | Idea | Trade-off |
|---|---|---|
| **Laplacian Variance** (used here) | Second-derivative edge strength | Fast, simple, sensitive to noise if unfiltered |
| Tenengrad (Sobel gradient magnitude) | First-derivative edge strength | Similar cost, slightly more robust to noise |
| Frequency-domain (FFT high-frequency energy) | Sharp images have more high-frequency content | More expensive, harder to tune thresholds |
| Wavelet-based focus measures | Multi-scale edge analysis | Most robust, significantly more compute |

Laplacian variance was chosen because it is **O(n)** in pixel count, requires
no training data, and is well-validated in the autofocus and image-quality
literature for exactly this style of relative ranking task (comparing frames
*against each other*, not against an absolute sharpness standard).

## 2. Why Normalize to 1000px Width First?

The Laplacian's response scales with edge density, which itself scales with
resolution. A 45 MP RAW file and a 12 MP JPEG produce *systematically*
different variance ranges purely from pixel count, independent of true focus
quality. Resizing every image to the same width before scoring removes this
confound, so the comparison is about **focus**, not **sensor resolution**.

## 3. Why Gaussian Blur Before Scoring?

Digital sensor noise is itself high-frequency, and the Laplacian operator
responds to *any* high-frequency signal, not just meaningful edges. Without
denoising, a noisy-but-blurry frame can score deceptively high. A 3×3 Gaussian
kernel removes this noise floor while preserving genuine edge structure at the
scale that matters for human-perceived sharpness.

## 4. RAW Decoding Pipeline

RAW files (`.CR2`/`.CR3`) store unprocessed sensor data and must be
demosaiced before any standard image operation applies. `rawpy` (a Python
binding for LibRaw) is used with `use_camera_wb=True` so that white balance
matches what the camera itself recorded — keeping color-derived luminance
values consistent with how the photographer saw the scene through the
viewfinder, rather than an arbitrary auto-white-balance guess.

## 5. Module Boundaries

```
loader.py   →  Pure I/O: file → BGR ndarray. No scoring logic.
filters.py  →  Pure scoring: ndarray → float. No I/O.
ranker.py   →  Orchestration: walks a directory, calls loader + filters,
                sorts results, handles export side-effects.
cli.py      →  Thin argument-parsing wrapper around ranker.
gui_main.py →  Tkinter presentation layer; reuses the same scoring logic
                via a background worker thread to keep the UI responsive.
```

This separation means the scoring algorithm in `filters.py` can be unit
tested with synthetic NumPy arrays — no real image files, no filesystem,
no GUI — which is what `tests/test_filters.py` does.

## 6. Known Limitations (and the Roadmap Items That Address Them)

- **No subject awareness.** The current score is computed over the *entire*
  frame. A photo with a blurry subject but a sharp, high-contrast background
  (e.g., dense foliage) can outscore a correctly-focused shot. This motivates
  the planned **region-of-interest weighting**.
- **No temporal grouping.** Every image in the input folder is currently
  ranked against every other image, even if they're from unrelated bursts
  taken minutes apart. The planned **smart burst grouping** (by EXIF capture
  timestamp) will partition images into events before ranking, so a sharp
  frame from burst A never "steals" the win from burst B.
- **Single-threaded scoring path** (despite the threaded GUI worker) — fine
  for typical burst sizes (10–100 frames) but would benefit from
  multiprocessing for very large batch jobs (1000+ images).

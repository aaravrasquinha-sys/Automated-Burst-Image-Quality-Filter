# AutoBurstFilter

**Automated sharpness-based image culling for wildlife, sports, and action photography.**

[![CI](https://github.com/aarav-rasquinha/AutoBurstFilter/actions/workflows/ci.yml/badge.svg)](https://github.com/aarav-rasquinha/AutoBurstFilter/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Motivation

Modern mirrorless cameras fire at **20+ frames per second**, turning a single
three-second action sequence into 60 near-identical RAW files. Manually
reviewing thousands of images per session is time-consuming, error-prone, and
pulls photographers away from what they do best — being in the field.

AutoBurstFilter automates that triage step.  It reads every image in a folder
(JPEG, PNG, or professional Canon RAW), scores each frame's sharpness using
computer-vision metrics, and exports the single sharpest frame — the
**champion** — ready for post-processing.

---

## Key Features

| Feature | Detail |
|---------|--------|
| **RAW support** | Natively decodes Canon CR2 / CR3 via `rawpy` — no lossy intermediary |
| **Noise-robust scoring** | Gaussian pre-filtering removes sensor noise before Laplacian edge detection |
| **Scale-normalised** | All images resized to 1000 px wide before scoring — fair comparison across sensor sizes |
| **Desktop GUI** | Tkinter culling station with thumbnail grid, per-image scores, and one-click export |
| **CLI** | Headless batch mode for scripting and automation |
| **Extensible** | Clean module boundary between I/O, scoring, and ranking — easy to swap algorithms |

---

## How It Works

```
Input Folder (RAW / JPEG)
        │
        ▼
  ┌─────────────┐
  │  Load BGR   │  rawpy (CR2/CR3)  or  OpenCV (JPEG/PNG)
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────┐
  │  Normalise to 1000px│  equal footing across sensor sizes
  └──────┬──────────────┘
         │
         ▼
  ┌─────────────────────┐
  │  Gaussian Blur 3×3  │  suppress high-frequency sensor noise
  └──────┬──────────────┘
         │
         ▼
  ┌──────────────────────────┐
  │  Laplacian Variance Score│  high variance = sharp edges
  └──────┬───────────────────┘
         │
         ▼
  Rank all frames → Export Champion
```

**Laplacian Variance** measures the second spatial derivative of intensity.
Sharp images contain well-defined edges (high second derivative), yielding
high variance.  Blurry images smooth out those transitions, yielding low
variance.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/aarav-rasquinha/AutoBurstFilter.git
cd AutoBurstFilter

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install
pip install -e .
```

> **macOS note:** `rawpy` requires `libraw`.  Install via Homebrew:
> `brew install libraw` before `pip install rawpy`.

---

## Usage

### Command-line interface

```bash
# Rank all images in a folder and print the top 10
autoburstfilter --input data/input

# Export the champion to a specific output folder
autoburstfilter --input data/input --output data/output

# Score only specific files
autoburstfilter --input data/input --files IMG_001.CR3 IMG_002.CR3 IMG_003.CR3

# Show top 5
autoburstfilter --input data/input --top 5
```

Example output:

```
 Scanning: data/input

Rank   Score    Filename
--------------------------------------------------
#1    2341.8   IMG_0042.CR3
#2    1876.4   IMG_0041.CR3
#3     923.1   IMG_0043.CR3
#4     412.7   IMG_0040.CR3

 Champion exported → data/output/IMG_0042.CR3
```

### Desktop GUI

```bash
python -m autoburstfilter.gui_main
```

Place images in `data/input/`, launch the GUI, inspect thumbnail cards
with colour-coded sharpness scores, select your picks manually, and click
**EXPORT BEST** to copy the sharpest selected image to `data/output/`.

### Python API

```python
from autoburstfilter import rank_burst, export_champion

results = rank_burst("data/input")

for r in results:
    print(f"{r.filename:30s}  score={r.score:.1f}")

champion_path = export_champion(results, "data/output")
print(f"Champion: {champion_path}")
```

---

## Project Structure

```
AutoBurstFilter/
├── autoburstfilter/
│   ├── __init__.py       # Public API
│   ├── __main__.py       # python -m autoburstfilter
│   ├── filters.py        # Sharpness scoring algorithm
│   ├── loader.py         # Unified image loader (JPEG / PNG / CR2 / CR3)
│   ├── ranker.py         # Burst ranking and champion export
│   ├── cli.py            # Argument-parser entry point
│   └── gui_main.py       # Tkinter desktop GUI
├── tests/
│   ├── test_filters.py   # Unit tests for sharpness scoring
│   └── test_ranker.py    # Integration tests for ranking + export
├── data/
│   ├── input/            # Drop burst images here
│   └── output/           # Champions exported here
├── .github/workflows/
│   └── ci.yml            # GitHub Actions CI (Python 3.10 / 3.11 / 3.12)
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Roadmap

- [ ] **Smart burst grouping** — cluster frames by capture timestamp so that
  only related shots compete against each other (prevents a shot of distant
  sharp foliage beating a close-up subject).
- [ ] **Region-of-interest scoring** — weight sharpness within a user-defined
  subject bounding box, reducing false positives from high-contrast backgrounds.
- [ ] **Web application** — Flask/FastAPI backend with a browser-based GUI,
  removing the Tkinter dependency for cross-platform accessibility.
- [ ] **Batch reporting** — CSV/JSON export of all scores for post-session analysis.

---

## Acknowledgements

Developed as a course project for **CS F311 – Digital Image Processing** at BITS Pilani,
under the guidance of Dr. Tojo Mathew.

---

## License

[MIT](LICENSE)

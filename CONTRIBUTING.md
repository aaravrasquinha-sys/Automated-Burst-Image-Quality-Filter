# Contributing to AutoBurstFilter

Thanks for your interest in improving AutoBurstFilter! This is primarily a
solo academic project, but contributions, bug reports, and suggestions are
welcome.

## Getting Started

```bash
git clone https://github.com/aarav-rasquinha/AutoBurstFilter.git
cd AutoBurstFilter
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest   # confirm everything passes before making changes
```

## Development Guidelines

- **Keep modules single-purpose.** `loader.py` handles I/O, `filters.py`
  handles scoring math, `ranker.py` orchestrates. Don't mix concerns.
- **Add tests for new logic.** Pure functions (like anything in `filters.py`)
  should be testable with synthetic NumPy arrays — no real image files needed.
- **Type hints encouraged** for new public functions.
- **Docstrings follow NumPy style** (see existing modules for examples).

## Submitting Changes

1. Fork the repository and create a feature branch:
   `git checkout -b feature/your-feature-name`
2. Make your changes and ensure `pytest` passes.
3. Commit with a clear message describing the *why*, not just the *what*.
4. Open a pull request against `main`, describing your change and motivation.

## Reporting Bugs

Please open an issue including:
- Python version and OS
- Steps to reproduce
- Expected vs. actual behavior
- A sample image (if the bug is scoring-related) when possible

## Code of Conduct

Be respectful and constructive. This project is maintained as part of an
academic portfolio — feedback aimed at improving code quality and
correctness is especially appreciated.

"""
autoburstfilter/cli.py
----------------------
Command-line interface for headless / scripted usage.

Usage examples
--------------
# Rank all images and print scores:
    python -m autoburstfilter --input data/input

# Export champion to a custom output folder:
    python -m autoburstfilter --input data/input --output data/output

# Rank only specific files:
    python -m autoburstfilter --input data/input --files IMG_001.CR3 IMG_002.CR3
"""

import argparse
import sys

from .ranker import rank_burst, export_champion


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="autoburstfilter",
        description="Rank a burst of images by sharpness and export the champion.",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        metavar="DIR",
        help="Directory containing the burst images.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        metavar="DIR",
        help="Destination directory for the champion image (skipped if omitted).",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        help="Restrict scoring to these specific filenames (within --input).",
    )
    parser.add_argument(
        "--top", "-n",
        type=int,
        default=10,
        metavar="N",
        help="Print the top N results (default: 10).",
    )

    args = parser.parse_args(argv)

    print(f"\n🔍  Scanning: {args.input}")
    results = rank_burst(args.input, files=args.files)

    if not results:
        print("❌  No scorable images found.")
        return 1

    print(f"\n{'Rank':<6} {'Score':>10}   Filename")
    print("-" * 50)
    for rank, r in enumerate(results[: args.top], start=1):
        marker = "🏆 " if rank == 1 else f"#{rank:<2}"
        print(f"{marker}  {r.score:>10.1f}   {r.filename}")

    if args.output:
        dest = export_champion(results, args.output)
        print(f"\n✅  Champion exported → {dest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

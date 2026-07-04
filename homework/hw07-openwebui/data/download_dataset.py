#!/usr/bin/env python3
"""Download the Netflix Kaggle dataset into data/netflix_titles.csv."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
DATASET = "shivamb/netflix-shows"


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(DATA_DIR),
        "--unzip",
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    csv_path = DATA_DIR / "netflix_titles.csv"
    if not csv_path.exists():
        print("Expected netflix_titles.csv after unzip", file=sys.stderr)
        return 1
    print(f"Downloaded {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

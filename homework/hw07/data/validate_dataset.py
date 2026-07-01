"""Validate hw07 CVE CSV schema before KB upload."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from env_loader import load_hw07_env  # noqa: E402

TARGET = Path(__file__).resolve().parent / "cve.csv"
REQUIRED_COLUMNS = ("cve_id", "description", "cvss", "published", "keyword")
MIN_ROWS = 10


def main() -> int:
    if not TARGET.is_file():
        print(f"ERROR: dataset not found: {TARGET}", file=sys.stderr)
        print("Run: python data/download_dataset.py  (or data/fetch_nvd_csv.py as fallback)", file=sys.stderr)
        return 1

    with TARGET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            print("ERROR: CSV has no header row", file=sys.stderr)
            return 1
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            print(f"ERROR: missing columns: {', '.join(missing)}", file=sys.stderr)
            print(f"Found: {', '.join(reader.fieldnames)}", file=sys.stderr)
            return 1
        rows = list(reader)

    if len(rows) < MIN_ROWS:
        print(f"ERROR: expected at least {MIN_ROWS} data rows, got {len(rows)}", file=sys.stderr)
        return 1

    print(f"OK: {TARGET.name} — {len(rows)} rows, columns: {', '.join(REQUIRED_COLUMNS)}")
    print(f"Path: {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Download Kaggle CVE CSV for hw07 (idempotent)."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from env_loader import HW07_ROOT, load_hw07_env

# Preferred Kaggle dataset for submission.
DATASET = "satyabrata/nvd-vulnerabilities"
TARGET = Path(__file__).resolve().parent / "cve.csv"

COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "cve_id": ("cve_id", "cve", "id", "CVE ID", "cveId"),
    "description": ("description", "summary", "desc", "vulnerability_description"),
    "cvss": ("cvss", "cvss_score", "cvss_v3", "baseScore", "cvss3"),
    "published": ("published", "published_date", "publishedDate", "pub_date", "date"),
    "keyword": ("keyword", "keywords", "product", "vendor", "cpe", "affected_product"),
}


def _pick_column(fieldnames: list[str], aliases: tuple[str, ...]) -> str | None:
    lower_map = {name.lower(): name for name in fieldnames}
    for alias in aliases:
        if alias.lower() in lower_map:
            return lower_map[alias.lower()]
    return None


def normalize_csv(source: Path, destination: Path) -> None:
    """Map Kaggle/NVD CSV columns to hw07 required schema."""
    with source.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        mapping = {
            required: _pick_column(reader.fieldnames, aliases)
            for required, aliases in COLUMN_ALIASES.items()
        }
        missing = [key for key, col in mapping.items() if not col]
        if missing:
            raise ValueError(
                f"Cannot map columns {missing}; found: {', '.join(reader.fieldnames)}"
            )
        rows: list[dict[str, str]] = []
        for row in reader:
            out = {key: (row.get(mapping[key]) or "").strip() for key in mapping}
            if out["cve_id"]:
                if not out["keyword"]:
                    out["keyword"] = "unknown"
                rows.append(out)

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(COLUMN_ALIASES.keys()))
        writer.writeheader()
        writer.writerows(rows)


def _configure_kaggle_credentials() -> None:
    """Ensure Kaggle API credentials are available via env or token file."""
    username = os.environ.get("KAGGLE_USERNAME", "").strip()
    key = os.environ.get("KAGGLE_KEY", "").strip()
    if username and key:
        return

    token = os.environ.get("KAGGLE_API_TOKEN", "").strip()
    if token:
        os.environ["KAGGLE_API_TOKEN"] = token
        access_token_path = Path.home() / ".kaggle" / "access_token"
        access_token_path.parent.mkdir(parents=True, exist_ok=True)
        if not access_token_path.is_file():
            access_token_path.write_text(token, encoding="utf-8")
        return

    access_token = Path.home() / ".kaggle" / "access_token"
    if access_token.is_file():
        return

    print(
        "ERROR: Kaggle credentials missing. Set KAGGLE_API_TOKEN in repo root .env, "
        "KAGGLE_USERNAME + KAGGLE_KEY in homework/hw07/.env, or ~/.kaggle/access_token.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Kaggle CVE CSV for hw07.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if data/cve.csv already exists.",
    )
    args = parser.parse_args()
    load_hw07_env()

    if TARGET.is_file() and TARGET.stat().st_size > 0 and not args.force:
        print(f"SKIP: {TARGET} already exists ({TARGET.stat().st_size} bytes)")
        print("Use --force to re-download from Kaggle.")
        return 0

    _configure_kaggle_credentials()

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    tmp_dir = HW07_ROOT / "data" / ".kaggle_download"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {DATASET} ...")
    api.dataset_download_files(DATASET, path=str(tmp_dir), unzip=True, quiet=False)

    csv_files = sorted(tmp_dir.glob("*.csv"))
    if not csv_files:
        print(f"ERROR: No CSV found in {tmp_dir}", file=sys.stderr)
        return 1

    source = csv_files[0]
    if len(csv_files) > 1:
        print(f"NOTE: Multiple CSVs found; using {source.name}")

    try:
        normalize_csv(source, TARGET)
    except ValueError as exc:
        print(f"ERROR: column normalization failed: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote normalized {TARGET} ({TARGET.stat().st_size} bytes)")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

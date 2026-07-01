"""Download the Kaggle AI job-market CSV for hw07 (idempotent).

Primary dataset: "Global AI Job Market & Salary Trends 2025"
(kaggle.com/datasets/bismasajjad/global-ai-job-market-and-salary-trends-2025) —
~15k synthetic-but-clean AI job postings with title, salary, skills, location,
experience level, industry, remote ratio and posting date.

Credentials come from the repo root `.env` (KAGGLE_API_TOKEN, or
KAGGLE_USERNAME + KAGGLE_KEY). Never hardcode or commit tokens.

If the download fails, this script STOPS with manual instructions — it never
substitutes unrelated fallback data.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_DATASET = "bismasajjad/global-ai-job-market-and-salary-trends-2025"
HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent
TARGET = Path(__file__).resolve().parent / "ai_jobs.csv"

MANUAL_STEP = f"""
MANUAL FALLBACK (Kaggle download failed):
  1. Open https://www.kaggle.com/datasets/{DEFAULT_DATASET}
  2. Click "Download", unzip, and copy the CSV to:
       {TARGET}
  3. Re-run: python data/validate_dataset.py
Do NOT substitute an unrelated dataset — the KB must stay on the AI job-market topic.
"""


def _load_env() -> None:
    # Root .env is canonical (loaded first — wins); hw07/.env is optional local defaults.
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(HW07_ROOT / ".env")


def _configure_kaggle_credentials() -> None:
    """Ensure Kaggle API credentials are available via env or token file."""
    username = os.environ.get("KAGGLE_USERNAME", "").strip()
    key = os.environ.get("KAGGLE_KEY", "").strip()
    if username and key:
        return

    token = os.environ.get("KAGGLE_API_TOKEN", "").strip()
    if token:
        access_token_path = Path.home() / ".kaggle" / "access_token"
        access_token_path.parent.mkdir(parents=True, exist_ok=True)
        if not access_token_path.is_file():
            access_token_path.write_text(token, encoding="utf-8")
        return

    if (Path.home() / ".kaggle" / "access_token").is_file():
        return
    if (Path.home() / ".kaggle" / "kaggle.json").is_file():
        return

    print(
        "ERROR: Kaggle credentials missing. Set KAGGLE_API_TOKEN in the repo root .env "
        "(or KAGGLE_USERNAME + KAGGLE_KEY, or ~/.kaggle/kaggle.json).",
        file=sys.stderr,
    )
    print(MANUAL_STEP, file=sys.stderr)
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the hw07 AI jobs Kaggle CSV.")
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Kaggle dataset slug (owner/name). Must stay on the AI job-market topic.",
    )
    parser.add_argument("--force", action="store_true", help="Re-download even if CSV exists.")
    args = parser.parse_args()

    _load_env()

    if TARGET.is_file() and TARGET.stat().st_size > 0 and not args.force:
        print(f"SKIP: {TARGET} already exists ({TARGET.stat().st_size} bytes)")
        return 0

    _configure_kaggle_credentials()

    tmp_dir = HW07_ROOT / "data" / ".kaggle_download"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        print(f"Downloading {args.dataset} ...")
        api.dataset_download_files(args.dataset, path=str(tmp_dir), unzip=True, quiet=False)
    except Exception as exc:  # noqa: BLE001 — surface any Kaggle/network failure with manual step
        print(f"ERROR: Kaggle download failed: {exc}", file=sys.stderr)
        print(MANUAL_STEP, file=sys.stderr)
        return 1

    csv_files = sorted(tmp_dir.glob("**/*.csv"), key=lambda p: p.stat().st_size, reverse=True)
    if not csv_files:
        print(f"ERROR: No CSV found in {tmp_dir}", file=sys.stderr)
        print(MANUAL_STEP, file=sys.stderr)
        return 1

    source = csv_files[0]
    if len(csv_files) > 1:
        print(f"NOTE: Multiple CSVs found; using largest: {source.name}")

    shutil.copy2(source, TARGET)
    print(f"OK: wrote {TARGET} ({TARGET.stat().st_size} bytes)")
    print("Next: python data/validate_dataset.py")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

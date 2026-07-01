"""Download Kaggle CVE CSV for hw07 (idempotent)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

# NVD-style CVE records with CVSS scores — adjust if you pick a different dataset via MCP.
DATASET = "satyabrata/nvd-vulnerabilities"
TARGET = Path(__file__).resolve().parent / "cve.csv"
HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent


def _load_env() -> None:
    load_dotenv(HW07_ROOT / ".env")
    load_dotenv(REPO_ROOT / ".env")


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
    _load_env()

    if TARGET.is_file() and TARGET.stat().st_size > 0:
        print(f"SKIP: {TARGET} already exists ({TARGET.stat().st_size} bytes)")
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

    shutil.copy2(source, TARGET)
    print(f"OK: wrote {TARGET} ({TARGET.stat().st_size} bytes)")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

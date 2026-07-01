"""Verify hw07 environment variables are present (never prints secret values)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent

REQUIRED_FOR_KB = ("OWUI_API_KEY",)
OPTIONAL = ("RAPIDAPI_KEY", "RAPIDAPI_HOST", "OWUI_URL", "KAGGLE_API_TOKEN")


def main() -> int:
    load_dotenv(HW07_ROOT / ".env")
    load_dotenv(REPO_ROOT / ".env")

    missing = [name for name in REQUIRED_FOR_KB if not os.getenv(name, "").strip()]
    if missing:
        print("MISSING (required for KB upload):", ", ".join(missing))
        return 1

    print("OK: OWUI_API_KEY set")
    for name in OPTIONAL:
        status = "set" if os.getenv(name, "").strip() else "not set"
        print(f"  {name}: {status}")

    rapid_key = os.getenv("RAPIDAPI_KEY", "").strip()
    rapid_host = os.getenv("RAPIDAPI_HOST", "").strip()
    if rapid_key and not rapid_host:
        print("WARN: RAPIDAPI_KEY set but RAPIDAPI_HOST missing — tool server uses CVEDB fallback")
    elif rapid_host and not rapid_key:
        print("WARN: RAPIDAPI_HOST set but RAPIDAPI_KEY missing — tool server uses CVEDB fallback")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

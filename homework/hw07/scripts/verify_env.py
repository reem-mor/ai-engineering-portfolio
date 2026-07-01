"""Verify hw07 environment variables are present (never prints secret values)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from env_loader import load_hw07_env  # noqa: E402

OPTIONAL = ("RAPIDAPI_KEY", "RAPIDAPI_CVE_HOST", "OWUI_URL", "KAGGLE_API_TOKEN")


def main() -> int:
    load_hw07_env()

    api_key = os.getenv("OWUI_API_KEY", "").strip()
    email = os.getenv("OWUI_EMAIL", "").strip()
    password = os.getenv("OWUI_PASSWORD", "").strip()
    if not api_key and not (email and password):
        print("MISSING: set OWUI_API_KEY or both OWUI_EMAIL and OWUI_PASSWORD in repo root .env")
        return 1

    print("OK: Open WebUI auth configured")
    for name in OPTIONAL:
        status = "set" if os.getenv(name, "").strip() else "not set"
        print(f"  {name}: {status}")

    rapid_key = os.getenv("RAPIDAPI_KEY", "").strip()
    rapid_cve_host = os.getenv("RAPIDAPI_CVE_HOST", "").strip()
    if rapid_key and not rapid_cve_host:
        print("WARN: RAPIDAPI_KEY set but RAPIDAPI_CVE_HOST missing — tool server uses CVEDB fallback")
    elif rapid_cve_host and not rapid_key:
        print("WARN: RAPIDAPI_CVE_HOST set but RAPIDAPI_KEY missing — tool server uses CVEDB fallback")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

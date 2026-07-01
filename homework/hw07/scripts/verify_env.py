"""Verify hw07 environment variables are present (never prints secret values)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent
DEFAULT_RAPIDAPI_HOST = "jsearch.p.rapidapi.com"


def _is_set(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def _validate_rapidapi_host() -> tuple[bool, str]:
    host = os.environ.get("RAPIDAPI_HOST", DEFAULT_RAPIDAPI_HOST).strip() or DEFAULT_RAPIDAPI_HOST
    if host in {"rapidapi.com", "www.rapidapi.com"}:
        return False, host
    if not host.endswith(".rapidapi.com"):
        return False, host
    return True, host


def main() -> int:
    load_dotenv(HW07_ROOT / ".env")
    load_dotenv(REPO_ROOT / ".env")

    mock = os.environ.get("HW07_MOCK_RAPIDAPI", "").strip().lower() in {"1", "true", "yes"}
    rapidapi_ok = mock or _is_set("RAPIDAPI_KEY")
    host_ok, host = _validate_rapidapi_host()

    kaggle_ok = (
        (_is_set("KAGGLE_USERNAME") and _is_set("KAGGLE_KEY"))
        or _is_set("KAGGLE_API_TOKEN")
        or (Path.home() / ".kaggle" / "access_token").is_file()
        or (Path.home() / ".kaggle" / "kaggle.json").is_file()
    )

    print(f"RAPIDAPI_KEY or mock mode: {'OK' if rapidapi_ok else 'MISSING'}")
    print(f"RAPIDAPI_HOST:              {'OK' if host_ok else 'INVALID'} ({host})")
    print(f"Kaggle credentials:         {'OK' if kaggle_ok else 'MISSING'}")
    print(f"HW07_MOCK_RAPIDAPI:         {os.environ.get('HW07_MOCK_RAPIDAPI', '0')}")
    print(f"TOOLS_SERVER_PORT:          {os.environ.get('TOOLS_SERVER_PORT', '5005')}")

    if not rapidapi_ok:
        print("Set RAPIDAPI_KEY in .env or HW07_MOCK_RAPIDAPI=1 for offline tests.", file=sys.stderr)
        return 1
    if not host_ok:
        print(
            f"RAPIDAPI_HOST must be the JSearch API host (e.g. {DEFAULT_RAPIDAPI_HOST}), not {host!r}.",
            file=sys.stderr,
        )
        return 1
    if not kaggle_ok:
        print(
            "Set KAGGLE_USERNAME/KAGGLE_KEY or KAGGLE_API_TOKEN for dataset download.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

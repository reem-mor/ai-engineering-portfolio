"""Verify hw07 environment variables are present (never prints secret values)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent

REQUIRED = ("RAPIDAPI_KEY",)
OWUI_AUTH = ("OWUI_API_KEY", "OWUI_EMAIL")  # need API key OR email(+password)
OPTIONAL = (
    "RAPIDAPI_JOBS_HOST",
    "RAPIDAPI_JOBS_BASE_URL",
    "KAGGLE_API_TOKEN",
    "OWUI_URL",
    "OWUI_PASSWORD",
    "OWUI_KNOWLEDGE_ID",
    "OWUI_FILE_ID",
)


def _set(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def main() -> int:
    # Root .env is canonical (loaded first — wins); hw07/.env is optional defaults.
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(HW07_ROOT / ".env")

    exit_code = 0

    for name in REQUIRED:
        if _set(name):
            print(f"OK:   {name} set")
        else:
            print(f"MISS: {name} — required for live job search (repo root .env)")
            exit_code = 1

    if _set("OWUI_API_KEY") or (_set("OWUI_EMAIL") and _set("OWUI_PASSWORD")):
        print("OK:   Open WebUI auth set (OWUI_API_KEY or OWUI_EMAIL+OWUI_PASSWORD)")
    else:
        print("MISS: Open WebUI auth — set OWUI_API_KEY or OWUI_EMAIL+OWUI_PASSWORD")
        exit_code = 1

    if not _set("KAGGLE_API_TOKEN"):
        print("WARN: KAGGLE_API_TOKEN not set — dataset download will need manual step")

    for name in OPTIONAL:
        print(f"      {name}: {'set' if _set(name) else 'not set'}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

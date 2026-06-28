"""Shared paths and environment loading for lecture 10."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

LECTURE_ROOT = Path(__file__).resolve().parent
DATA_DIR = LECTURE_ROOT / "data"
REPO_ROOT = LECTURE_ROOT.parents[1]
TITANIC_CSV = REPO_ROOT / "homework" / "hw03" / "data" / "titanic.csv"


def load_lecture_env() -> None:
    load_dotenv(LECTURE_ROOT / ".env")


def require_openai_api_key() -> str:
    load_lecture_env()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return api_key

"""HW07 prompt helpers."""

from __future__ import annotations

from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent / "system_prompt.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

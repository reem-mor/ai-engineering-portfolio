"""HW07 prompt loading helpers."""

from __future__ import annotations

from pathlib import Path

_PROMPT_PATH = Path(__file__).resolve().parent / "system_prompt.md"
_IO_CONTRACT_MARKER = "## I/O contract"


def load_system_prompt(*, include_io_contract: bool = False) -> str:
    """Load the Open WebUI system prompt from system_prompt.md."""
    raw = _PROMPT_PATH.read_text(encoding="utf-8")
    if include_io_contract:
        return raw.strip()
    if _IO_CONTRACT_MARKER in raw:
        raw = raw.split(_IO_CONTRACT_MARKER, maxsplit=1)[0]
    return raw.strip()

#!/usr/bin/env python3
"""Launch the lecture-08 stdio MCP server (course-tools).

Resolves Python in order: lectures/08_mcp/.venv, repo root .venv, then PATH.
Install deps first: pip install -r lectures/08_mcp/requirements.txt
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "lectures" / "08_mcp" / "server" / "tools_server.py"

CANDIDATES = [
    ROOT / "lectures" / "08_mcp" / ".venv" / "Scripts" / "python.exe",
    ROOT / "lectures" / "08_mcp" / ".venv" / "bin" / "python",
    ROOT / ".venv" / "Scripts" / "python.exe",
    ROOT / ".venv" / "bin" / "python",
]


def resolve_python() -> Path:
    for candidate in CANDIDATES:
        if candidate.is_file():
            return candidate
    return Path(sys.executable)


def main() -> None:
    if not SERVER.is_file():
        print(f"Missing MCP server: {SERVER}", file=sys.stderr)
        sys.exit(1)
    python = resolve_python()
    os.chdir(ROOT / "lectures" / "08_mcp")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.execv(str(python), [str(python), str(SERVER)])


if __name__ == "__main__":
    main()

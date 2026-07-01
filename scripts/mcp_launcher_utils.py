#!/usr/bin/env python3
"""Shared helpers for MCP launcher scripts (venv re-exec + .env load without dotenv)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    return (start or Path(__file__)).resolve().parents[1]


def ensure_repo_venv() -> None:
    """Re-exec with repo .venv Python when Cursor invokes system python."""
    root = repo_root(Path(__file__))
    candidates = [
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
    ]
    current = Path(sys.executable).resolve()
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve() != current:
            os.execv(str(candidate), [str(candidate), *sys.argv])
            raise SystemExit("failed to re-exec with repo venv")


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ (does not override existing keys)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_repo_env(root: Path | None = None) -> None:
    base = root or repo_root(Path(__file__))
    load_env_file(base / ".env")
    load_env_file(base / "homework" / "hw07" / ".env")


def resolve_npx() -> str:
    import shutil

    for name in ("npx", "npx.cmd"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("npx not found on PATH — install Node.js 18+")


def launch_npx(args: list[str], env: dict[str, str] | None = None) -> None:
    """Run npx as MCP stdio server. On Windows, subprocess (npx.cmd); on Unix, exec."""
    import subprocess

    npx = resolve_npx()
    cmd = [npx, *args]
    run_env = env or os.environ.copy()
    if sys.platform == "win32":
        raise SystemExit(subprocess.call(cmd, env=run_env))
    os.execve(npx, cmd, run_env)

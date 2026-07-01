#!/usr/bin/env python3
"""Sync MCP HTTP vars from repo .env to Windows user environment."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_launcher_utils import load_repo_env  # noqa: E402

SYNC_KEYS = ("RAPIDAPI_KEY", "RAPIDAPI_HOST", "KAGGLE_API_TOKEN")


def main() -> int:
    load_repo_env(ROOT)
    missing = [k for k in SYNC_KEYS if not os.getenv(k, "").strip()]
    if missing:
        print(f"ERROR: missing in .env: {', '.join(missing)}", file=sys.stderr)
        return 1

    if sys.platform != "win32":
        print("Export these from .env before starting Cursor:")
        for key in SYNC_KEYS:
            print(f"  export {key}=...")
        return 0

    import subprocess

    for key in SYNC_KEYS:
        value = os.environ[key].strip().replace("'", "''")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"[Environment]::SetEnvironmentVariable('{key}', '{value}', 'User')",
            ],
            check=True,
        )
        print(f"OK: set user env {key}")

    print("Restart Cursor so HTTP MCP (${env:...}) picks up the values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Launch RapidAPI MCP via mcp-remote stdio (required for tools to appear in Cursor)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_launcher_utils import ensure_repo_venv, launch_npx, load_repo_env  # noqa: E402

ensure_repo_venv()
load_repo_env(ROOT)


def main() -> None:
    api_key = os.getenv("RAPIDAPI_KEY", "").strip()
    api_host = os.getenv("RAPIDAPI_HOST", "").strip()
    if not api_key or not api_host:
        print(
            "ERROR: set RAPIDAPI_KEY and RAPIDAPI_HOST in repo .env before starting rapidapi MCP.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # Pin version that matches Cursor's mcp-remote client (see MCP server logs).
    launch_npx(
        [
            "-y",
            "mcp-remote@0.1.37",
            "https://mcp.rapidapi.com",
            "--header",
            f"x-api-host: {api_host}",
            "--header",
            f"x-api-key: {api_key}",
        ],
        env=os.environ.copy(),
    )


if __name__ == "__main__":
    main()

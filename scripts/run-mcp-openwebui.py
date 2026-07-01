#!/usr/bin/env python3
"""Launch Open WebUI MCP via openwebui-mcp-server stdio."""

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
    url = (
        os.getenv("OPENWEBUI_URL")
        or os.getenv("OWUI_URL")
        or "http://localhost:3000"
    ).strip()
    api_key = (os.getenv("OPENWEBUI_API_KEY") or os.getenv("OWUI_API_KEY") or "").strip()

    if not api_key:
        print(
            "ERROR: set OWUI_API_KEY (or OPENWEBUI_API_KEY) in repo .env before starting openwebui MCP.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    env = os.environ.copy()
    env["OPENWEBUI_URL"] = url.rstrip("/")
    env["OPENWEBUI_API_KEY"] = api_key

    launch_npx(["-y", "openwebui-mcp-server"], env=env)


if __name__ == "__main__":
    main()

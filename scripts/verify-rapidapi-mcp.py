#!/usr/bin/env python3
"""Verify RapidAPI MCP exposes tools for the configured RAPIDAPI_HOST (no secrets printed)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_launcher_utils import load_repo_env  # noqa: E402


def main() -> int:
    load_repo_env(ROOT)
    host = os.getenv("RAPIDAPI_HOST", "").strip()
    key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not host or not key:
        print("ERROR: RAPIDAPI_HOST and RAPIDAPI_KEY required in .env", file=sys.stderr)
        return 1

    headers = {
        "x-api-host": host,
        "x-api-key": key,
        "Content-Type": "application/json",
    }
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "verify", "version": "1.0"},
        },
    }
    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    with httpx.Client(timeout=30.0) as client:
        r1 = client.post("https://mcp.rapidapi.com", headers=headers, json=init)
        r1.raise_for_status()
        r2 = client.post("https://mcp.rapidapi.com", headers=headers, json=tools_req)
        r2.raise_for_status()

    tools = r2.json().get("result", {}).get("tools", [])
    print(f"OK: {host} exposes {len(tools)} MCP tool(s):")
    for tool in tools:
        print(f"  - {tool.get('name')}")
    print("\nNote: RapidAPI MCP has tools only — no prompts or resources (by design).")
    print("Cursor must use stdio via scripts/run-mcp-rapidapi.py, not HTTP type.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

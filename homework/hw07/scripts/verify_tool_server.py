#!/usr/bin/env python3
"""Verify hw07 tool server health and live job search (no secrets printed)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

HW07 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07))
from env_loader import load_hw07_env  # noqa: E402

load_hw07_env()

BASE = os.getenv("TOOLS_SERVER_URL", "http://localhost:5005").rstrip("/")


def main() -> int:
    try:
        health = httpx.get(f"{BASE}/health", timeout=15)
        health.raise_for_status()
        body = health.json()
        print(f"health: status={body.get('status')} source={body.get('source')}")
        print(f"  rapidapi_configured={body.get('rapidapi_configured')}")

        search = httpx.get(
            f"{BASE}/jobs/search",
            params={"query": "ai engineer", "location": "Israel"},
            timeout=45,
        )
        sr = search.json()
        print(
            f"search_jobs: status={search.status_code} count={sr.get('count')} "
            f"error={sr.get('error')}"
        )

        missing = httpx.get(f"{BASE}/jobs/search", timeout=15)
        print(f"missing_query: status={missing.status_code} (expect 422)")

        skills = httpx.get(f"{BASE}/jobs/skills", params={"skill": "Python"}, timeout=45)
        print(f"search_jobs_by_skill: status={skills.status_code}")

        openapi = httpx.get(f"{BASE}/openapi.json", timeout=15)
        openapi.raise_for_status()
        spec = openapi.json()
        op = spec.get("paths", {}).get("/jobs/search", {}).get("get", {})
        print(
            f"openapi: operation_id={op.get('operationId')} "
            f"title={spec.get('info', {}).get('title')}"
        )
    except httpx.HTTPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if missing.status_code != 422:
        print("ERROR: missing query should return 422", file=sys.stderr)
        return 1
    if op.get("operationId") != "search_jobs":
        print("ERROR: operation_id must be search_jobs for Open WebUI", file=sys.stderr)
        return 1
    if body.get("rapidapi_configured"):
        if search.status_code != 200 or sr.get("error"):
            print("ERROR: RAPIDAPI_KEY set but live search failed", file=sys.stderr)
            return 1
    elif search.status_code != 503:
        print("ERROR: without RAPIDAPI_KEY, search should return clean 503", file=sys.stderr)
        return 1

    print("OK: tool server verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify hw07 tool server health and live CVE lookup (no secrets printed)."""

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
TEST_CVE = "CVE-2021-44228"


def main() -> int:
    try:
        health = httpx.get(f"{BASE}/health", timeout=15)
        health.raise_for_status()
        body = health.json()
        print(f"health: status={body.get('status')} mode={body.get('mode')} source={body.get('source')}")
        print(f"  rapidapi_configured={body.get('rapidapi_configured')}")

        lookup = httpx.get(f"{BASE}/cve/{TEST_CVE}", timeout=30)
        lookup.raise_for_status()
        cve = lookup.json()
        print(f"lookup_cve({TEST_CVE}): source={cve.get('source')} cvss={cve.get('cvss')} epss={cve.get('epss')}")

        invalid = httpx.get(f"{BASE}/cve/not-a-cve", timeout=15)
        print(f"invalid_cve: status={invalid.status_code} (expect 422)")

        search = httpx.get(f"{BASE}/search", params={"keyword": "apache struts"}, timeout=30)
        search.raise_for_status()
        sr = search.json()
        print(f"search_cves: source={sr.get('source')} count={sr.get('count')}")

        openapi = httpx.get(f"{BASE}/openapi.json", timeout=15)
        openapi.raise_for_status()
        spec = openapi.json()
        paths = spec.get("paths", {})
        op = paths.get("/cve/{cve_id}", {}).get("get", {})
        print(f"openapi: operation_id={op.get('operationId')} title={spec.get('info', {}).get('title')}")
    except httpx.HTTPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if invalid.status_code != 422:
        print("ERROR: invalid CVE should return 422", file=sys.stderr)
        return 1
    if op.get("operationId") != "lookup_cve":
        print("ERROR: operation_id must be lookup_cve for Open WebUI", file=sys.stderr)
        return 1

    print("OK: tool server verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

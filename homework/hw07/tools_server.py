"""Open WebUI OpenAPI tool server for hw07 — live CVE lookups.

Primary source: RapidAPI CVE product (RAPIDAPI_KEY + RAPIDAPI_HOST in .env).
Fallback: Shodan CVEDB (https://cvedb.shodan.io) — free, no key.

Run:
    uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload

Register in Open WebUI (Admin > Settings > External Tools > OpenAPI):
    http://host.docker.internal:5005/openapi.json   # OWUI in Docker
    http://localhost:5005/openapi.json              # OWUI on host
"""

from __future__ import annotations

import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

TIMEOUT = float(os.getenv("TOOLS_HTTP_TIMEOUT", "15"))


def _rapidapi_config() -> tuple[str, str]:
    """Read RapidAPI credentials at call time (testable via env patching)."""
    return (
        os.getenv("RAPIDAPI_KEY", "").strip(),
        os.getenv("RAPIDAPI_HOST", "").strip(),
    )

CVE_ID_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

app = FastAPI(
    title="CVE Intelligence Tool Server",
    description="Live CVE / vulnerability lookups for the Open WebUI assistant.",
    version="1.0.0",
)


def validate_cve_id(raw: str) -> str:
    """Normalize and validate a CVE identifier."""
    cve_id = raw.strip().upper()
    if not cve_id:
        raise HTTPException(status_code=422, detail="CVE ID must not be empty.")
    if not CVE_ID_PATTERN.match(cve_id):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid CVE ID format: {raw!r}. Expected CVE-YYYY-NNNN.",
        )
    return cve_id


def normalize_cve(data: dict) -> dict:
    """Return a compact, model-friendly subset of CVE fields."""
    refs = data.get("references") or []
    if isinstance(refs, dict):
        refs = list(refs.values())
    return {
        "cve_id": data.get("cve_id") or data.get("id"),
        "summary": data.get("summary") or data.get("description"),
        "cvss": data.get("cvss") or data.get("cvss_v3") or data.get("cvss_v2"),
        "epss": data.get("epss"),
        "kev": data.get("kev"),
        "published": data.get("published_time") or data.get("published"),
        "references": list(refs)[:5],
        "source": data.get("_source", "unknown"),
    }


async def fetch_rapidapi(cve_id: str) -> dict | None:
    """Query the configured RapidAPI CVE product, or None if not configured."""
    api_key, api_host = _rapidapi_config()
    if not (api_key and api_host):
        return None
    url = f"https://{api_host}/cve/{cve_id}"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": api_host}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
        payload["_source"] = "rapidapi"
        return payload


async def fetch_cvedb(cve_id: str) -> dict:
    """Shodan CVEDB — free, no key, updated daily."""
    url = f"https://cvedb.shodan.io/cve/{cve_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()
        payload["_source"] = "cvedb"
        return payload


@app.get("/health")
def health() -> dict:
    """Liveness check; reports which upstream source is configured."""
    api_key, api_host = _rapidapi_config()
    return {
        "status": "ok",
        "source": "rapidapi" if api_host else "cvedb",
        "rapidapi_configured": bool(api_key and api_host),
    }


@app.get("/cve/{cve_id}", operation_id="lookup_cve")
async def lookup_cve(cve_id: str) -> dict:
    """Look up live details for a CVE ID (e.g. CVE-2021-44228).

    Returns CVSS, EPSS, KEV status, publication date, and references.
    Use for CURRENT risk questions; use the knowledge base for historical dataset queries.
    """
    normalized_id = validate_cve_id(cve_id)
    data: dict | None = None

    try:
        data = await fetch_rapidapi(normalized_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 404:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Upstream error for {normalized_id}.",
            ) from exc

    if data is None:
        try:
            data = await fetch_cvedb(normalized_id)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"CVE not found: {normalized_id}.",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="CVE lookup failed.") from exc

    return normalize_cve(data)

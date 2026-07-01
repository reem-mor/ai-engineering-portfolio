"""Open WebUI OpenAPI tool server for hw07 — live CVE lookups.

Primary source: RapidAPI CVE product (RAPIDAPI_KEY + RAPIDAPI_CVE_HOST in repo root .env).
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
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from env_loader import load_hw07_env

load_hw07_env()

TIMEOUT = float(os.getenv("TOOLS_HTTP_TIMEOUT", "15"))
SOURCE_RAPIDAPI = "rapidapi"
SOURCE_CVEDB_FALLBACK = "cvedb_fallback"

CVE_ID_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

app = FastAPI(
    title="CVE Intelligence Tool Server",
    description=(
        "Live CVE lookups for HW07. Use for current EPSS/KEV/CVSS questions. "
        "Use the Open WebUI knowledge base for historical dataset questions."
    ),
    version="1.1.0",
)


def _rapidapi_config() -> tuple[str, str]:
    """Read RapidAPI credentials at call time (testable via env patching)."""
    return (
        os.getenv("RAPIDAPI_KEY", "").strip(),
        (os.getenv("RAPIDAPI_CVE_HOST") or os.getenv("RAPIDAPI_HOST", "")).strip(),
    )


def _rapidapi_cve_compatible(api_host: str) -> bool:
    """True when the configured host is a CVE API (not JSearch / job APIs)."""
    host = api_host.lower()
    non_cve_markers = ("jsearch", "job-search", "jobs", "linkedin", "indeed")
    return not any(marker in host for marker in non_cve_markers)


def _rapidapi_configured() -> bool:
    api_key, api_host = _rapidapi_config()
    return bool(api_key and api_host and _rapidapi_cve_compatible(api_host))


def _should_fallback_from_rapidapi(exc: httpx.HTTPStatusError) -> bool:
    code = exc.response.status_code
    return code in {404, 429} or code >= 500


class HealthResponse(BaseModel):
    status: str = Field(..., description="Always 'ok' when the server is running.")
    source: str = Field(
        ...,
        description="Primary upstream: 'rapidapi' when configured, else 'cvedb_fallback'.",
    )
    mode: str = Field(
        ...,
        description="'live' when RapidAPI is configured; 'fallback' uses Shodan CVEDB only.",
    )
    rapidapi_configured: bool = Field(
        ...,
        description="True when CVE-compatible RapidAPI host and key are set.",
    )
    rapidapi_host: str | None = Field(
        None,
        description="Configured RapidAPI host (safe to display; no secrets).",
    )


class CveLookupResponse(BaseModel):
    cve_id: str = Field(..., description="CVE identifier, e.g. CVE-2021-44228.")
    summary: str | None = Field(None, description="Brief vulnerability description.")
    cvss: float | int | str | None = Field(
        None, description="CVSS base score from the live upstream."
    )
    epss: float | None = Field(
        None, description="Exploit Prediction Scoring System probability (0–1)."
    )
    kev: bool | None = Field(
        None, description="True if listed in CISA Known Exploited Vulnerabilities catalog."
    )
    published: str | None = Field(None, description="Publication date (ISO or upstream format).")
    references: list[str] = Field(
        default_factory=list,
        description="Up to 5 reference URLs.",
        max_length=5,
    )
    source: str = Field(
        ...,
        description="Upstream used: 'rapidapi' or 'cvedb_fallback'.",
    )


class CveSearchHit(BaseModel):
    cve_id: str
    summary: str | None = None
    cvss: float | int | str | None = None
    epss: float | None = None
    kev: bool | None = None


class CveSearchResponse(BaseModel):
    keyword: str
    count: int
    results: list[CveSearchHit]
    source: str = Field(..., description="'rapidapi' or 'cvedb_fallback'.")


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


def validate_keyword(raw: str) -> str:
    keyword = raw.strip()
    if not keyword:
        raise HTTPException(status_code=422, detail="keyword must not be empty.")
    if len(keyword) < 2:
        raise HTTPException(status_code=422, detail="keyword must be at least 2 characters.")
    if len(keyword) > 100:
        raise HTTPException(status_code=422, detail="keyword must be at most 100 characters.")
    return keyword


def normalize_cve(data: dict, source: str) -> CveLookupResponse:
    """Return a compact, model-friendly subset of CVE fields."""
    refs = data.get("references") or []
    if isinstance(refs, dict):
        refs = list(refs.values())
    return CveLookupResponse(
        cve_id=data.get("cve_id") or data.get("id") or "",
        summary=data.get("summary") or data.get("description"),
        cvss=data.get("cvss") or data.get("cvss_v3") or data.get("cvss_v2"),
        epss=data.get("epss"),
        kev=data.get("kev"),
        published=data.get("published_time") or data.get("published"),
        references=[str(r) for r in list(refs)[:5]],
        source=source,
    )


def normalize_search_hit(item: dict) -> CveSearchHit:
    return CveSearchHit(
        cve_id=item.get("cve_id") or item.get("id") or "",
        summary=item.get("summary") or item.get("description"),
        cvss=item.get("cvss") or item.get("cvss_v3") or item.get("cvss_v2"),
        epss=item.get("epss"),
        kev=item.get("kev"),
    )


async def fetch_rapidapi_cve(cve_id: str) -> dict | None:
    """Query RapidAPI CVE product; None if not configured."""
    api_key, api_host = _rapidapi_config()
    if not (api_key and api_host and _rapidapi_cve_compatible(api_host)):
        return None
    url = f"https://{api_host}/cve/{cve_id}"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_cvedb_cve(cve_id: str) -> dict:
    url = f"https://cvedb.shodan.io/cve/{cve_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()


async def fetch_rapidapi_search(keyword: str, limit: int = 10) -> list[dict] | None:
    api_key, api_host = _rapidapi_config()
    if not (api_key and api_host and _rapidapi_cve_compatible(api_host)):
        return None
    url = f"https://{api_host}/search"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers, params={"q": keyword, "limit": limit})
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            return payload
        return payload.get("results") or payload.get("items") or []


async def fetch_cvedb_search(keyword: str, limit: int = 10) -> list[dict]:
    product = keyword.split()[0] if keyword else keyword
    url = f"https://cvedb.shodan.io/cves?product={quote(product)}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("cves") or payload.get("results") or payload.get("items") or []
        return items[:limit]


async def lookup_with_fallback(cve_id: str) -> CveLookupResponse:
    if _rapidapi_configured():
        try:
            data = await fetch_rapidapi_cve(cve_id)
            if data is not None:
                return normalize_cve(data, SOURCE_RAPIDAPI)
        except httpx.HTTPStatusError as exc:
            if not _should_fallback_from_rapidapi(exc):
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Upstream error for {cve_id}.",
                ) from exc
        except httpx.HTTPError:
            pass  # fall through to CVEDB

    try:
        data = await fetch_cvedb_cve(cve_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"CVE not found: {cve_id}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="CVE lookup failed.") from exc

    return normalize_cve(data, SOURCE_CVEDB_FALLBACK)


async def search_with_fallback(keyword: str, limit: int = 10) -> CveSearchResponse:
    if _rapidapi_configured():
        try:
            items = await fetch_rapidapi_search(keyword, limit=limit)
            if items is not None:
                hits = [normalize_search_hit(item) for item in items[:limit]]
                return CveSearchResponse(
                    keyword=keyword,
                    count=len(hits),
                    results=hits,
                    source=SOURCE_RAPIDAPI,
                )
        except httpx.HTTPStatusError as exc:
            if not _should_fallback_from_rapidapi(exc):
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail="Upstream search error.",
                ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="CVE search failed.") from exc

    try:
        items = await fetch_cvedb_search(keyword, limit=limit)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"No results for keyword: {keyword!r}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="CVE search failed.") from exc

    hits = [normalize_search_hit(item) for item in items]
    return CveSearchResponse(
        keyword=keyword,
        count=len(hits),
        results=hits,
        source=SOURCE_CVEDB_FALLBACK,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check; reports which upstream source is configured."""
    _, api_host = _rapidapi_config()
    configured = _rapidapi_configured()
    return HealthResponse(
        status="ok",
        source=SOURCE_RAPIDAPI if configured else SOURCE_CVEDB_FALLBACK,
        mode="live" if configured else "fallback",
        rapidapi_configured=configured,
        rapidapi_host=api_host or None,
    )


@app.get(
    "/cve/{cve_id}",
    operation_id="lookup_cve",
    response_model=CveLookupResponse,
    responses={
        422: {"description": "Invalid or empty CVE ID format."},
        404: {"description": "CVE not found in upstream sources."},
        502: {"description": "Upstream connection failure."},
    },
)
async def lookup_cve(cve_id: str) -> CveLookupResponse:
    """Look up live details for a CVE ID (e.g. CVE-2021-44228)."""
    normalized_id = validate_cve_id(cve_id)
    return await lookup_with_fallback(normalized_id)


@app.get(
    "/search",
    operation_id="search_cves",
    response_model=CveSearchResponse,
    responses={
        422: {"description": "Invalid or empty keyword."},
        404: {"description": "No results found."},
        502: {"description": "Upstream connection failure."},
    },
)
async def search_cves(
    keyword: str = Query(..., description="Product or vulnerability keyword, e.g. apache struts"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return."),
) -> CveSearchResponse:
    """Search live CVE records by keyword (product/vendor)."""
    normalized = validate_keyword(keyword)
    return await search_with_fallback(normalized, limit=limit)

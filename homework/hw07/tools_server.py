"""Open WebUI OpenAPI tool server for hw07 — live AI job-market search.

Upstream: a job-search API on RapidAPI (JSearch by default).
Secrets/config come from the repo root `.env` (see env_loader):
    RAPIDAPI_KEY            — RapidAPI key (never printed, never committed)
    RAPIDAPI_JOBS_HOST      — e.g. jsearch.p.rapidapi.com
    RAPIDAPI_JOBS_BASE_URL  — optional; defaults to https://<RAPIDAPI_JOBS_HOST>

Run:
    uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload

Register in Open WebUI (Admin > Settings > External Tools > OpenAPI):
    http://host.docker.internal:5005/openapi.json   # OWUI in Docker
    http://tool-server:5005/openapi.json            # OWUI + tool server via compose
    http://localhost:5005/openapi.json              # OWUI on host
"""

from __future__ import annotations

import json
import os

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from env_loader import load_hw07_env

load_hw07_env()

TIMEOUT = float(os.getenv("TOOLS_HTTP_TIMEOUT", "15"))
DEFAULT_JOBS_HOST = "jsearch.p.rapidapi.com"
MAX_QUERY_LEN = 200
MAX_RESULTS = 10

app = FastAPI(
    title="AI Job Market Live Search Tool Server",
    description=(
        "Live AI / ML / DevOps / SRE / software job search for the Open WebUI "
        "assistant, backed by a RapidAPI job-search provider (JSearch)."
    ),
    version="2.0.0",
)


def _rapidapi_config() -> tuple[str, str, str]:
    """Read RapidAPI credentials at call time (testable via env patching)."""
    key = os.getenv("RAPIDAPI_KEY", "").strip()
    host = os.getenv("RAPIDAPI_JOBS_HOST", "").strip() or DEFAULT_JOBS_HOST
    base_url = os.getenv("RAPIDAPI_JOBS_BASE_URL", "").strip() or f"https://{host}"
    return key, host, base_url.rstrip("/")


def _payload(
    query: str,
    results: list[dict],
    source: str,
    error: str | None = None,
    status_code: int = 200,
) -> JSONResponse:
    """Uniform response envelope: source / query / count / results / error."""
    body: dict = {
        "source": source,
        "query": query,
        "count": len(results),
        "results": results,
    }
    if error:
        body["error"] = error
    return JSONResponse(status_code=status_code, content=body)


def _validate_term(value: str, name: str, max_len: int = MAX_QUERY_LEN) -> str | None:
    """Return an error message if the term is unusable, else None."""
    if not value or not value.strip():
        return f"Parameter '{name}' must not be empty."
    if len(value) > max_len:
        return f"Parameter '{name}' too long (max {max_len} characters)."
    return None


def normalize_job(raw: dict) -> dict:
    """Compact, model-friendly subset of a JSearch job record."""
    city = raw.get("job_city") or ""
    country = raw.get("job_country") or ""
    location = ", ".join(part for part in (city, country) if part)
    salary = None
    if raw.get("job_min_salary") or raw.get("job_max_salary"):
        salary = {
            "min": raw.get("job_min_salary"),
            "max": raw.get("job_max_salary"),
            "currency": raw.get("job_salary_currency"),
            "period": raw.get("job_salary_period"),
        }
    description = (raw.get("job_description") or "").strip()
    return {
        "title": raw.get("job_title"),
        "company": raw.get("employer_name"),
        "location": location or None,
        "remote": raw.get("job_is_remote"),
        "employment_type": raw.get("job_employment_type"),
        "posted_at": raw.get("job_posted_at_datetime_utc"),
        "salary": salary,
        "apply_link": raw.get("job_apply_link"),
        "description_snippet": description[:400] or None,
    }


async def fetch_jobs(search_query: str) -> list[dict]:
    """Call the RapidAPI job-search provider; raise httpx errors to the caller."""
    api_key, api_host, base_url = _rapidapi_config()
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": api_host}
    params = {"query": search_query, "page": "1", "num_pages": "1"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{base_url}/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data") or []
    return [normalize_job(job) for job in data[:MAX_RESULTS]]


async def _search(query: str, search_query: str, source_label: str) -> JSONResponse:
    """Shared upstream-call wrapper with clean, secret-free error handling."""
    api_key, _, _ = _rapidapi_config()
    if not api_key:
        return _payload(
            query,
            [],
            source_label,
            error=(
                "RAPIDAPI_KEY is not configured. Set it in the repo root .env "
                "(never hardcode or commit it)."
            ),
            status_code=503,
        )
    try:
        results = await fetch_jobs(search_query)
    except httpx.TimeoutException:
        return _payload(
            query,
            [],
            source_label,
            error=f"Upstream RapidAPI request timed out after {TIMEOUT:.0f}s.",
            status_code=504,
        )
    except httpx.HTTPStatusError as exc:
        return _payload(
            query,
            [],
            source_label,
            error=(
                f"Upstream RapidAPI error (HTTP {exc.response.status_code}). "
                "Check RAPIDAPI_JOBS_HOST and your RapidAPI subscription."
            ),
            status_code=502,
        )
    except httpx.HTTPError:
        return _payload(
            query,
            [],
            source_label,
            error="Could not reach the RapidAPI job-search provider (network error).",
            status_code=502,
        )
    return _payload(query, results, source_label)


@app.get("/health")
def health() -> dict:
    """Liveness check; reports upstream configuration without exposing secrets."""
    api_key, api_host, _ = _rapidapi_config()
    return {
        "status": "ok",
        "source": f"rapidapi:{api_host}",
        "rapidapi_configured": bool(api_key),
    }


@app.get("/jobs/search", operation_id="search_jobs")
async def search_jobs(
    query: str = Query("", description="Job search terms, e.g. 'AI engineer'."),
    location: str = Query("", description="Optional location, e.g. 'Israel' or 'Tel Aviv'."),
) -> JSONResponse:
    """Search current live job postings by role/keywords and optional location.

    Use for CURRENT market questions ("open AI Engineer jobs in Israel now");
    use the knowledge base for questions about the static Kaggle dataset.
    """
    error = _validate_term(query, "query")
    if error:
        return _payload(query, [], "rapidapi", error=error, status_code=422)
    location = location.strip()
    if location and len(location) > 100:
        return _payload(
            query, [], "rapidapi",
            error="Parameter 'location' too long (max 100 characters).",
            status_code=422,
        )
    search_query = f"{query.strip()} jobs in {location}" if location else f"{query.strip()} jobs"
    return await _search(query.strip(), search_query, "rapidapi")


@app.get("/jobs/company", operation_id="search_jobs_by_company")
async def search_jobs_by_company(
    company: str = Query("", description="Company name, e.g. 'Google'."),
) -> JSONResponse:
    """Search current live job postings at a specific company."""
    error = _validate_term(company, "company")
    if error:
        return _payload(company, [], "rapidapi", error=error, status_code=422)
    company = company.strip()
    response = await _search(company, f"jobs at {company}", "rapidapi")
    if response.status_code != 200:
        return response
    body = json.loads(bytes(response.body))
    needle = company.lower()
    # Prefer exact employer matches; keep the raw upstream list if none match.
    matched = [
        job for job in body["results"] if needle in (job.get("company") or "").lower()
    ]
    body["results"] = matched or body["results"]
    body["count"] = len(body["results"])
    return JSONResponse(status_code=200, content=body)


@app.get("/jobs/skills", operation_id="search_jobs_by_skill")
async def search_jobs_by_skill(
    skill: str = Query("", description="Skill keyword, e.g. 'Python' or 'Kubernetes'."),
) -> JSONResponse:
    """Search current live job postings that mention a specific skill."""
    error = _validate_term(skill, "skill")
    if error:
        return _payload(skill, [], "rapidapi", error=error, status_code=422)
    skill = skill.strip()
    return await _search(skill, f"{skill} jobs", "rapidapi")

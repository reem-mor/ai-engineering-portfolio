"""Tests for hw07 tools_server (mocked HTTP — no live RapidAPI required)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

import tools_server

SAMPLE_JOB = {
    "job_title": "AI Engineer",
    "employer_name": "Acme AI",
    "job_city": "Tel Aviv",
    "job_country": "IL",
    "job_is_remote": False,
    "job_employment_type": "FULLTIME",
    "job_posted_at_datetime_utc": "2026-06-20T00:00:00Z",
    "job_min_salary": 120000,
    "job_max_salary": 160000,
    "job_salary_currency": "USD",
    "job_salary_period": "YEAR",
    "job_apply_link": "https://example.com/apply",
    "job_description": "Build LLM pipelines with Python and Kubernetes.",
}

NORMALIZED_JOB = tools_server.normalize_job(SAMPLE_JOB)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client with NO RapidAPI key configured."""
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.delenv("RAPIDAPI_JOBS_HOST", raising=False)
    monkeypatch.delenv("RAPIDAPI_JOBS_BASE_URL", raising=False)
    return TestClient(tools_server.app)


@pytest.fixture
def configured_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client with a fake RapidAPI key + host configured."""
    monkeypatch.setenv("RAPIDAPI_KEY", "test-secret-key-do-not-leak")
    monkeypatch.setenv("RAPIDAPI_JOBS_HOST", "jsearch.p.rapidapi.com")
    monkeypatch.delenv("RAPIDAPI_JOBS_BASE_URL", raising=False)
    return TestClient(tools_server.app)


# --- /health ------------------------------------------------------------------


def test_health_unconfigured(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["source"] == "rapidapi:jsearch.p.rapidapi.com"
    assert body["rapidapi_configured"] is False


def test_health_configured_never_leaks_key(configured_client: TestClient) -> None:
    response = configured_client.get("/health")
    assert response.json()["rapidapi_configured"] is True
    assert "test-secret-key-do-not-leak" not in response.text


# --- input validation -----------------------------------------------------------


def test_search_missing_query(client: TestClient) -> None:
    response = client.get("/jobs/search")
    assert response.status_code == 422
    body = response.json()
    assert body["count"] == 0
    assert "query" in body["error"]


def test_search_query_too_long(client: TestClient) -> None:
    response = client.get("/jobs/search", params={"query": "x" * 201})
    assert response.status_code == 422
    assert "too long" in response.json()["error"]


def test_search_location_too_long(configured_client: TestClient) -> None:
    response = configured_client.get(
        "/jobs/search", params={"query": "ai engineer", "location": "x" * 101}
    )
    assert response.status_code == 422
    assert "location" in response.json()["error"]


def test_company_missing_param(client: TestClient) -> None:
    assert client.get("/jobs/company").status_code == 422


def test_skills_missing_param(client: TestClient) -> None:
    assert client.get("/jobs/skills").status_code == 422


# --- missing key / upstream failures --------------------------------------------


def test_search_missing_key_returns_503(client: TestClient) -> None:
    response = client.get("/jobs/search", params={"query": "ai engineer"})
    assert response.status_code == 503
    body = response.json()
    assert "RAPIDAPI_KEY" in body["error"]
    assert body["results"] == []


def test_search_upstream_timeout_returns_504(configured_client: TestClient) -> None:
    with patch(
        "tools_server.fetch_jobs",
        new=AsyncMock(side_effect=httpx.ConnectTimeout("slow upstream")),
    ):
        response = configured_client.get("/jobs/search", params={"query": "ai engineer"})
    assert response.status_code == 504
    assert "timed out" in response.json()["error"]


def test_search_upstream_http_error_returns_502(configured_client: TestClient) -> None:
    request = httpx.Request("GET", "https://jsearch.p.rapidapi.com/search")
    upstream = httpx.Response(429, request=request)
    with patch(
        "tools_server.fetch_jobs",
        new=AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "rate limited", request=request, response=upstream
            )
        ),
    ):
        response = configured_client.get("/jobs/search", params={"query": "ai engineer"})
    assert response.status_code == 502
    body = response.json()
    assert "429" in body["error"]
    assert "test-secret-key-do-not-leak" not in response.text


# --- success paths ----------------------------------------------------------------


def test_search_success_shape(configured_client: TestClient) -> None:
    with patch("tools_server.fetch_jobs", new=AsyncMock(return_value=[NORMALIZED_JOB])) as mock:
        response = configured_client.get(
            "/jobs/search", params={"query": "AI Engineer", "location": "Israel"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "rapidapi"
    assert body["query"] == "AI Engineer"
    assert body["count"] == 1
    assert body["results"][0]["company"] == "Acme AI"
    assert body["results"][0]["salary"]["max"] == 160000
    mock.assert_awaited_once_with("AI Engineer jobs in Israel")


def test_company_filters_by_employer(configured_client: TestClient) -> None:
    other = dict(NORMALIZED_JOB, company="Unrelated Corp")
    with patch(
        "tools_server.fetch_jobs", new=AsyncMock(return_value=[NORMALIZED_JOB, other])
    ):
        response = configured_client.get("/jobs/company", params={"company": "Acme"})
    body = response.json()
    assert response.status_code == 200
    assert body["count"] == 1
    assert body["results"][0]["company"] == "Acme AI"


def test_skills_success(configured_client: TestClient) -> None:
    with patch("tools_server.fetch_jobs", new=AsyncMock(return_value=[NORMALIZED_JOB])) as mock:
        response = configured_client.get("/jobs/skills", params={"skill": "Python"})
    assert response.status_code == 200
    assert response.json()["count"] == 1
    mock.assert_awaited_once_with("Python jobs")


# --- normalize_job -----------------------------------------------------------------


def test_normalize_job_fields() -> None:
    job = tools_server.normalize_job(SAMPLE_JOB)
    assert job["title"] == "AI Engineer"
    assert job["location"] == "Tel Aviv, IL"
    assert job["salary"]["currency"] == "USD"
    assert len(job["description_snippet"]) <= 400


def test_normalize_job_handles_missing_fields() -> None:
    job = tools_server.normalize_job({})
    assert job["title"] is None
    assert job["location"] is None
    assert job["salary"] is None
    assert job["description_snippet"] is None

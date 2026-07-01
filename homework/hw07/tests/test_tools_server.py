"""Tests for hw07 tools_server (mock JSearch — no live API required)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

import tools_server
from jsearch_client import JSearchClient, JSearchSettings, JSearchUpstreamError


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    tools_server.refresh_client(tools_server.app)
    return TestClient(tools_server.app)


@pytest.fixture
def live_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")
    monkeypatch.setenv("RAPIDAPI_KEY", "test-secret-key-do-not-leak")
    monkeypatch.setenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
    tools_server.refresh_client(tools_server.app)
    return TestClient(tools_server.app)


def test_health_returns_ok(mock_client: TestClient) -> None:
    response = mock_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mock"] is True
    assert body["jsearch_configured"] is True


def test_jobs_search_mock_shape(mock_client: TestClient) -> None:
    response = mock_client.post(
        "/jobs/search",
        json={"query": "AI engineer", "location": "Israel", "num_pages": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["source"] == "mock"
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1
    first = body["data"][0]
    assert "job_title" in first
    assert "employer_name" in first


def test_jobs_search_validation(mock_client: TestClient) -> None:
    response = mock_client.post("/jobs/search", json={"query": ""})
    assert response.status_code == 422


def test_jobs_search_default_location(mock_client: TestClient) -> None:
    response = mock_client.post("/jobs/search", json={"query": "AI engineer"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["data"], list)


def test_jobs_search_empty_results(live_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def _empty_search(self, query: str, location: str = "Israel", num_pages: int = 1) -> list:
        return []

    monkeypatch.setattr(JSearchClient, "search_jobs", _empty_search)
    tools_server.refresh_client(tools_server.app)
    client = TestClient(tools_server.app)

    response = client.post(
        "/jobs/search",
        json={"query": "nonexistent role xyz", "location": "Israel"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"] == []


def test_jobs_search_upstream_timeout(live_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def _timeout_search(self, query: str, location: str = "Israel", num_pages: int = 1) -> list:
        raise JSearchUpstreamError("JSearch request timed out")

    monkeypatch.setattr(JSearchClient, "search_jobs", _timeout_search)
    tools_server.refresh_client(tools_server.app)
    client = TestClient(tools_server.app)

    response = client.post(
        "/jobs/search",
        json={"query": "AI engineer", "location": "Israel"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert "timed out" in (body.get("error") or "").lower()
    assert "test-secret-key-do-not-leak" not in response.text


def test_no_secret_leakage_in_health_or_errors(
    live_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    secret = "test-secret-key-do-not-leak"

    def _fail_search(self, query: str, location: str = "Israel", num_pages: int = 1) -> list:
        raise JSearchUpstreamError("JSearch request failed: upstream rejected request")

    monkeypatch.setattr(JSearchClient, "search_jobs", _fail_search)
    tools_server.refresh_client(tools_server.app)
    client = TestClient(tools_server.app)

    health = client.get("/health")
    assert secret not in health.text

    search = client.post("/jobs/search", json={"query": "AI engineer", "location": "Israel"})
    assert secret not in search.text
    assert search.json()["ok"] is False


def test_jsearch_client_timeout_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")
    monkeypatch.setenv("RAPIDAPI_KEY", "fake-key")
    settings = JSearchSettings.from_env()
    client = JSearchClient(settings)

    mock_http = MagicMock()
    mock_http.get.side_effect = httpx.TimeoutException("timed out")
    client._http = mock_http

    with pytest.raises(JSearchUpstreamError, match="timed out"):
        client.search_jobs("AI engineer", "Israel")


@pytest.mark.live
def test_jobs_search_live() -> None:
    api_key = os.environ.get("RAPIDAPI_KEY", "").strip()
    if not api_key:
        pytest.skip("RAPIDAPI_KEY not set")

    os.environ["HW07_MOCK_RAPIDAPI"] = "0"
    tools_server.refresh_client(tools_server.app)
    client = TestClient(tools_server.app)

    response = client.post(
        "/jobs/search",
        json={"query": "software engineer", "location": "Israel", "num_pages": 1},
    )
    assert response.status_code == 200
    body = response.json()
    if not body["ok"]:
        error = body.get("error") or "unknown"
        if "404" in error or "does not exist" in error.lower():
            pytest.skip(
                "JSearch returned 404 — subscribe to JSearch on RapidAPI and use that app's key: "
                "https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
            )
        pytest.fail(f"JSearch upstream error: {error}")
    assert body["source"] == "jsearch"
    assert isinstance(body["data"], list)
    assert api_key not in response.text


def test_jsearch_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    monkeypatch.setenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")
    settings = JSearchSettings.from_env()
    assert settings.api_key == "test-key"
    assert settings.jsearch_configured is True

"""Tests for hw07 tools_server (mocked HTTP — no live API required)."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

import tools_server


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.delenv("RAPIDAPI_HOST", raising=False)
    monkeypatch.delenv("RAPIDAPI_CVE_HOST", raising=False)
    return TestClient(tools_server.app)


@pytest.fixture
def rapidapi_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-secret-key-do-not-leak")
    monkeypatch.setenv("RAPIDAPI_CVE_HOST", "cve-api.example.com")
    monkeypatch.delenv("RAPIDAPI_HOST", raising=False)
    return TestClient(tools_server.app)


def test_health_cvedb_mode(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["source"] == "cvedb_fallback"
    assert body["mode"] == "fallback"
    assert body["rapidapi_configured"] is False


def test_health_rapidapi_mode(rapidapi_client: TestClient) -> None:
    response = rapidapi_client.get("/health")
    body = response.json()
    assert body["source"] == "rapidapi"
    assert body["mode"] == "live"
    assert body["rapidapi_configured"] is True
    assert "test-secret-key-do-not-leak" not in response.text


def test_jsearch_host_not_used(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "key")
    monkeypatch.setenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
    monkeypatch.delenv("RAPIDAPI_CVE_HOST", raising=False)
    response = TestClient(tools_server.app).get("/health")
    assert response.json()["rapidapi_configured"] is False


def test_validate_cve_id_empty(client: TestClient) -> None:
    response = client.get("/cve/%20%20")
    assert response.status_code == 422


def test_validate_cve_id_invalid_format(client: TestClient) -> None:
    response = client.get("/cve/not-a-cve")
    assert response.status_code == 422
    assert "Invalid CVE ID format" in response.json()["detail"]


def test_validate_cve_id_normalizes_case(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "Log4Shell",
            "cvss": 10.0,
            "references": [],
        }
        response = client.get("/cve/cve-2021-44228")
    assert response.status_code == 200
    assert response.json()["cve_id"] == "CVE-2021-44228"


def test_lookup_cve_cvedb_success(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 RCE",
            "cvss": 10.0,
            "epss": 0.97,
            "kev": True,
            "published_time": "2021-12-10",
            "references": ["https://example.com/a", "https://example.com/b"],
        }
        response = client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    body = response.json()
    assert body["cve_id"] == "CVE-2021-44228"
    assert body["source"] == "cvedb_fallback"
    assert len(body["references"]) == 2


def test_normalize_truncates_references() -> None:
    data = {
        "cve_id": "CVE-2020-0001",
        "references": [f"https://ref{i}.example" for i in range(10)],
    }
    normalized = tools_server.normalize_cve(data, "cvedb_fallback")
    assert len(normalized.references) == 5


def test_normalize_alternate_field_names() -> None:
    data = {
        "id": "CVE-2019-0001",
        "description": "Test vuln",
        "cvss_v3": 7.5,
        "published": "2019-01-01",
    }
    normalized = tools_server.normalize_cve(data, "rapidapi")
    assert normalized.cve_id == "CVE-2019-0001"
    assert normalized.summary == "Test vuln"
    assert normalized.cvss == 7.5


def test_lookup_cve_not_found(client: TestClient) -> None:
    request = httpx.Request("GET", "https://cvedb.shodan.io/cve/CVE-2099-00001")
    response = httpx.Response(404, request=request)

    with patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = httpx.HTTPStatusError(
            "not found", request=request, response=response
        )
        result = client.get("/cve/CVE-2099-00001")

    assert result.status_code == 404


def test_lookup_cve_upstream_error(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = httpx.ConnectError("connection refused")
        result = client.get("/cve/CVE-2021-44228")

    assert result.status_code == 502


def test_rapidapi_404_falls_back_to_cvedb(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    not_found = httpx.Response(404, request=request)

    with (
        patch("tools_server.fetch_rapidapi_cve", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "not found", request=request, response=not_found
        )
        mock_cvedb.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "fallback",
        }
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "cvedb_fallback"
    mock_cvedb.assert_awaited_once()


def test_rapidapi_429_falls_back_to_cvedb(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    rate_limited = httpx.Response(429, request=request)

    with (
        patch("tools_server.fetch_rapidapi_cve", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "rate limited", request=request, response=rate_limited
        )
        mock_cvedb.return_value = {"cve_id": "CVE-2021-44228", "summary": "fallback"}
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "cvedb_fallback"


def test_rapidapi_500_falls_back_to_cvedb(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    server_error = httpx.Response(500, request=request)

    with (
        patch("tools_server.fetch_rapidapi_cve", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "server error", request=request, response=server_error
        )
        mock_cvedb.return_value = {"cve_id": "CVE-2021-44228", "summary": "fallback"}
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "cvedb_fallback"


def test_rapidapi_success_skips_cvedb(rapidapi_client: TestClient) -> None:
    with (
        patch("tools_server.fetch_rapidapi_cve", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb_cve", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "from rapidapi",
        }
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "rapidapi"
    mock_cvedb.assert_not_called()


def test_rapidapi_403_does_not_fallback(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    forbidden = httpx.Response(403, request=request)

    with patch("tools_server.fetch_rapidapi_cve", new_callable=AsyncMock) as mock_rapid:
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "forbidden", request=request, response=forbidden
        )
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 403
    assert "test-secret-key-do-not-leak" not in response.text


def test_search_empty_keyword(client: TestClient) -> None:
    response = client.get("/search", params={"keyword": "  "})
    assert response.status_code == 422


def test_search_success_cvedb(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {"cve_id": "CVE-2006-1546", "summary": "Apache Struts", "cvss": 7.5},
        ]
        response = client.get("/search", params={"keyword": "apache struts"})

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["source"] == "cvedb_fallback"
    assert body["results"][0]["cve_id"] == "CVE-2006-1546"


def test_search_openapi_operation_id(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    op = spec["paths"]["/search"]["get"]
    assert op["operationId"] == "search_cves"


def test_lookup_openapi_operation_id(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    op = spec["paths"]["/cve/{cve_id}"]["get"]
    assert op["operationId"] == "lookup_cve"


@pytest.mark.live
def test_lookup_cve_live_cvedb() -> None:
    """Optional live test against Shodan CVEDB (no API key)."""
    if os.getenv("HW07_SKIP_LIVE", "").strip() == "1":
        pytest.skip("HW07_SKIP_LIVE=1")

    client = TestClient(tools_server.app)
    response = client.get("/cve/CVE-2021-44228")
    assert response.status_code == 200
    body = response.json()
    assert body["cve_id"] == "CVE-2021-44228"
    assert body.get("summary") or body.get("cvss") is not None
    assert body["source"] in {"rapidapi", "cvedb_fallback"}

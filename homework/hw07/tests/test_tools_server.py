"""Tests for hw07 tools_server (mocked HTTP — no live API required)."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

import tools_server


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.delenv("RAPIDAPI_HOST", raising=False)
    return TestClient(tools_server.app)


@pytest.fixture
def rapidapi_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-secret-key-do-not-leak")
    monkeypatch.setenv("RAPIDAPI_HOST", "cve-api.example.com")
    return TestClient(tools_server.app)


def test_health_cvedb_mode(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["source"] == "cvedb"
    assert body["rapidapi_configured"] is False


def test_health_rapidapi_mode(rapidapi_client: TestClient) -> None:
    response = rapidapi_client.get("/health")
    body = response.json()
    assert body["source"] == "rapidapi"
    assert body["rapidapi_configured"] is True
    assert "test-secret-key-do-not-leak" not in response.text


def test_validate_cve_id_empty(client: TestClient) -> None:
    response = client.get("/cve/%20%20")
    assert response.status_code == 422


def test_validate_cve_id_invalid_format(client: TestClient) -> None:
    response = client.get("/cve/not-a-cve")
    assert response.status_code == 422
    assert "Invalid CVE ID format" in response.json()["detail"]


def test_validate_cve_id_normalizes_case(client: TestClient) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cve_id": "CVE-2021-44228",
        "summary": "Log4Shell",
        "cvss": 10.0,
        "references": [],
    }
    mock_response.raise_for_status = MagicMock()

    with patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "Log4Shell",
            "cvss": 10.0,
            "references": [],
            "_source": "cvedb",
        }
        response = client.get("/cve/cve-2021-44228")
    assert response.status_code == 200
    assert response.json()["cve_id"] == "CVE-2021-44228"


def test_lookup_cve_cvedb_success(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 RCE",
            "cvss": 10.0,
            "epss": 0.97,
            "kev": True,
            "published_time": "2021-12-10",
            "references": ["https://example.com/a", "https://example.com/b"],
            "_source": "cvedb",
        }
        response = client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    body = response.json()
    assert body["cve_id"] == "CVE-2021-44228"
    assert body["summary"] == "Apache Log4j2 RCE"
    assert body["cvss"] == 10.0
    assert body["source"] == "cvedb"
    assert len(body["references"]) == 2


def test_normalize_truncates_references() -> None:
    data = {
        "cve_id": "CVE-2020-0001",
        "references": [f"https://ref{i}.example" for i in range(10)],
        "_source": "cvedb",
    }
    normalized = tools_server.normalize_cve(data)
    assert len(normalized["references"]) == 5


def test_normalize_alternate_field_names() -> None:
    data = {
        "id": "CVE-2019-0001",
        "description": "Test vuln",
        "cvss_v3": 7.5,
        "published": "2019-01-01",
        "_source": "rapidapi",
    }
    normalized = tools_server.normalize_cve(data)
    assert normalized["cve_id"] == "CVE-2019-0001"
    assert normalized["summary"] == "Test vuln"
    assert normalized["cvss"] == 7.5


def test_lookup_cve_not_found(client: TestClient) -> None:
    request = httpx.Request("GET", "https://cvedb.shodan.io/cve/CVE-2099-00001")
    response = httpx.Response(404, request=request)

    with patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = httpx.HTTPStatusError(
            "not found", request=request, response=response
        )
        result = client.get("/cve/CVE-2099-00001")

    assert result.status_code == 404


def test_lookup_cve_upstream_error(client: TestClient) -> None:
    with patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = httpx.ConnectError("connection refused")
        result = client.get("/cve/CVE-2021-44228")

    assert result.status_code == 502


def test_rapidapi_404_falls_back_to_cvedb(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    not_found = httpx.Response(404, request=request)

    with (
        patch("tools_server.fetch_rapidapi", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "not found", request=request, response=not_found
        )
        mock_cvedb.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "fallback",
            "_source": "cvedb",
        }
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "cvedb"
    mock_cvedb.assert_awaited_once()


def test_rapidapi_success_skips_cvedb(rapidapi_client: TestClient) -> None:
    with (
        patch("tools_server.fetch_rapidapi", new_callable=AsyncMock) as mock_rapid,
        patch("tools_server.fetch_cvedb", new_callable=AsyncMock) as mock_cvedb,
    ):
        mock_rapid.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "from rapidapi",
            "_source": "rapidapi",
        }
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 200
    assert response.json()["source"] == "rapidapi"
    mock_cvedb.assert_not_called()


def test_no_secret_leakage_on_upstream_error(rapidapi_client: TestClient) -> None:
    request = httpx.Request("GET", "https://cve-api.example.com/cve/CVE-2021-44228")
    error_response = httpx.Response(500, request=request)

    with patch("tools_server.fetch_rapidapi", new_callable=AsyncMock) as mock_rapid:
        mock_rapid.side_effect = httpx.HTTPStatusError(
            "server error", request=request, response=error_response
        )
        response = rapidapi_client.get("/cve/CVE-2021-44228")

    assert response.status_code == 500
    assert "test-secret-key-do-not-leak" not in response.text


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

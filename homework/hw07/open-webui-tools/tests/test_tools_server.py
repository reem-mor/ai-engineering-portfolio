"""Unit and integration tests for hw07 Open WebUI tool server."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from rapidapi_client import RapidApiClient, RapidApiSettings, is_mock_mode
from tools_server import app, refresh_client

TOOL_POST_PATHS = {
    "/tools/search_title",
    "/tools/country_info",
    "/tools/streaming_status",
}


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        refresh_client(app)
        yield test_client


@pytest.fixture(autouse=True)
def disable_mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")
    refresh_client(app)


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["rapidapi_configured"] in {"true", "false"}
    assert body["mock_mode"] == "false"
    assert body["tools_ready"] in {"true", "false"}


def test_health_reports_mock_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    refresh_client(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["mock_mode"] == "true"
    assert body["tools_ready"] == "true"


def test_openapi_has_three_tool_operations(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    post_ops = [
        (path, method)
        for path, methods in spec["paths"].items()
        for method in methods
        if method == "post" and path in TOOL_POST_PATHS
    ]
    assert len(post_ops) == 3


def test_openapi_operation_summaries_present(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    for path in TOOL_POST_PATHS:
        post = spec["paths"][path]["post"]
        assert post.get("operationId") in {
            "search_title",
            "country_info",
            "streaming_status",
        }
        assert post.get("summary")
        assert post.get("description")


def test_search_title_empty_rejected(client: TestClient) -> None:
    response = client.post("/tools/search_title", json={"title": ""})
    assert response.status_code == 422


def test_country_info_missing_key_returns_structured_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    refresh_client(app)
    response = client.post("/tools/country_info", json={"country_name": "Brazil"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert "RAPIDAPI_KEY" in (body["error"] or "")


def test_mock_mode_country_info(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    refresh_client(app)
    response = client.post("/tools/country_info", json={"country_name": "Brazil"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["source"] == "mock"
    assert body["data"]["capital"] == "Brasília"


def test_mock_mode_streaming_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    refresh_client(app)
    response = client.post(
        "/tools/streaming_status",
        json={"title": "Stranger Things", "country_code": "US"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["source"] == "mock"
    assert body["data"]["result"][0]["country"] == "US"


def test_search_title_mocked_success(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    refresh_client(app)

    def fake_search(self: RapidApiClient, title: str) -> dict[str, Any]:
        assert title == "Squid Game"
        return {"results": [{"title": "Squid Game", "year": 2021}]}

    monkeypatch.setattr(RapidApiClient, "search_title", fake_search)
    response = client.post("/tools/search_title", json={"title": "Squid Game"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["results"][0]["title"] == "Squid Game"


def test_streaming_status_invalid_country_code(client: TestClient) -> None:
    response = client.post(
        "/tools/streaming_status",
        json={"title": "Stranger Things", "country_code": "USA"},
    )
    assert response.status_code == 422


def test_country_info_mocked_http_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    refresh_client(app)

    def fake_request(
        self: RapidApiClient,
        *,
        host: str,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        request = httpx.Request(method, f"https://{host}{path}")
        response = httpx.Response(404, request=request, text="not found")
        raise httpx.HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr(RapidApiClient, "_request", fake_request)
    response = client.post("/tools/country_info", json={"country_name": "Atlantis"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert "External API error" in (body["error"] or "")


def test_rapidapi_settings_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")
    settings = RapidApiSettings.from_env()
    with pytest.raises(Exception, match="RAPIDAPI_KEY"):
        settings.require_live_credentials()


def test_rapidapi_settings_allows_missing_key_in_mock_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    settings = RapidApiSettings.from_env()
    assert settings.api_key == ""
    assert settings.tools_ready is True
    assert is_mock_mode() is True


def test_rapidapi_client_with_mock_transport() -> None:
    settings = RapidApiSettings(
        api_key="test-key",
        omdb_host="example.test",
        countries_host="example.test",
        streaming_host="example.test",
        mock_mode=False,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3.1/name/brazil"
        assert request.headers.get("X-RapidAPI-Host") == "example.test"
        return httpx.Response(
            200,
            json=[{"name": {"common": "Brazil"}, "capital": ["Brasília"], "region": "Americas"}],
        )

    transport = httpx.MockTransport(handler)
    with RapidApiClient(settings, transport=transport) as client:
        result = client.country_info("Brazil")
    assert result["name"] == "Brazil"
    assert result["capital"] == "Brasília"


def test_normalize_country_payload_from_list() -> None:
    settings = RapidApiSettings(
        api_key="test-key",
        omdb_host="example.test",
        countries_host="example.test",
        streaming_host="example.test",
        mock_mode=False,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "name": {"common": "Brazil", "official": "Federative Republic of Brazil"},
                    "capital": ["Brasília"],
                    "region": "Americas",
                    "population": 212559417,
                }
            ],
        )

    transport = httpx.MockTransport(handler)
    with RapidApiClient(settings, transport=transport) as client:
        result = client.country_info("Brazil")
    assert result["name"] == "Brazil"
    assert result["capital"] == "Brasília"
    assert result["region"] == "Americas"

"""Unit and integration tests for hw07 Open WebUI tool server."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from rapidapi_client import RapidApiClient, RapidApiSettings, is_mock_mode
from tools_server import app

TOOL_POST_PATHS = {
    "/tools/search_title",
    "/tools/country_info",
    "/tools/streaming_status",
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def disable_mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "0")


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["rapidapi_configured"] in {"true", "false"}
    assert body["mock_mode"] in {"true", "false"}


def test_health_reports_mock_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mock_mode"] == "true"


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
    response = client.post("/tools/country_info", json={"country_name": "Brazil"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert "RAPIDAPI_KEY" in (body["error"] or "")


def test_mock_mode_country_info(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    response = client.post("/tools/country_info", json={"country_name": "Brazil"})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["source"] == "mock"
    assert body["data"]["capital"] == "Brasília"


def test_search_title_mocked_success(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")

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
    with pytest.raises(Exception, match="RAPIDAPI_KEY"):
        RapidApiSettings.from_env()


def test_rapidapi_settings_allows_missing_key_in_mock_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.setenv("HW07_MOCK_RAPIDAPI", "1")
    settings = RapidApiSettings.from_env()
    assert settings.api_key == "mock"
    assert is_mock_mode() is True


def test_rapidapi_client_with_mock_transport() -> None:
    settings = RapidApiSettings(
        api_key="test-key",
        omdb_host="example.test",
        countries_host="example.test",
        streaming_host="example.test",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        payload = {"path": request.url.path, "host": request.headers.get("X-RapidAPI-Host")}
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    client = RapidApiClient(settings, transport=transport)
    result = client.country_info("Brazil")
    assert result["path"] == "/name/brazil"
    assert result["host"] == "example.test"

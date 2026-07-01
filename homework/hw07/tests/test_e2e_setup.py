"""E2E setup tests — run before screenshot capture."""

from __future__ import annotations

import httpx
import pytest

from e2e.fixtures import KB_COLLECTION_NAME, TOOL_ID
from e2e.open_webui_client import OpenWebUIClient


@pytest.fixture
def api_client() -> OpenWebUIClient:
    client = OpenWebUIClient()
    client.sign_in()
    yield client
    client.close()


def test_open_webui_health(api_client: OpenWebUIClient) -> None:
    response = httpx.get("http://localhost:3000/health", timeout=10.0)
    assert response.status_code == 200


def test_tool_server_health() -> None:
    response = httpx.get("http://127.0.0.1:5005/health", timeout=10.0)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ollama_llama_available(api_client: OpenWebUIClient) -> None:
    name = api_client.ensure_chat_model()
    assert name.startswith("llama3.2")


def test_knowledge_collection_exists(api_client: OpenWebUIClient) -> None:
    kb = api_client.ensure_knowledge_collection()
    assert kb["name"] == KB_COLLECTION_NAME


def test_tool_registered(api_client: OpenWebUIClient) -> None:
    tool = api_client.ensure_tool()
    assert tool.get("id") == TOOL_ID


def test_model_preset_native_tools(api_client: OpenWebUIClient) -> None:
    preset = api_client.ensure_model_preset()
    assert preset["params"]["function_calling"] == "native"
    assert TOOL_ID in preset["meta"]["toolIds"]
    system = preset.get("params", {}).get("system") or preset.get("meta", {}).get("system")
    assert system and "search_live_jobs" in system

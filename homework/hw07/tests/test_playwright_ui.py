"""Playwright UI validation — teacher HW checklist in Open WebUI."""

from __future__ import annotations

import re

import httpx
import pytest
from playwright.sync_api import Page, sync_playwright

from e2e.fixtures import (
    CHAT_MODEL,
    KB_COLLECTION_NAME,
    TOOL_NAME,
)
from e2e.open_webui_client import OpenWebUIClient
from e2e.open_webui_helpers import (
    ensure_authenticated,
    goto_path,
    inject_auth_token,
    open_model_settings,
    open_tool_editor,
)

OPEN_WEBUI_URL = "http://localhost:3000"
TOOL_SERVER_HEALTH = "http://127.0.0.1:5005/health"
CSV_NAME = "job_postings.csv"


def _stack_ready() -> bool:
    try:
        webui = httpx.get(f"{OPEN_WEBUI_URL}/health", timeout=8.0)
        tools = httpx.get(TOOL_SERVER_HEALTH, timeout=8.0)
        return webui.status_code == 200 and tools.status_code == 200 and tools.json().get("status") == "ok"
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="module")
def require_stack(api_client: OpenWebUIClient) -> OpenWebUIClient:
    """Ensure stack + tool server up; reuse API session for setup."""
    if not _stack_ready():
        pytest.skip("Start hw07 stack + tool server: docker compose up -d && .\\scripts\\start_tool_server.ps1 -MockRapidApi")
    api_client.ensure_tool()
    api_client.ensure_model_preset()
    return api_client


@pytest.fixture
def ui_page(require_stack: OpenWebUIClient) -> Page:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        inject_auth_token(page, require_stack.token or "")
        ensure_authenticated(page)
        yield page
        browser.close()


def test_playwright_signed_in_home(ui_page: Page) -> None:
    body = ui_page.locator("body").inner_text()
    assert "sign in" not in body.lower() or "hello" in body.lower()


def test_playwright_knowledge_base_csv(ui_page: Page, require_stack: OpenWebUIClient) -> None:
    kb = require_stack.ensure_knowledge_collection()
    goto_path(ui_page, f"/workspace/knowledge/{kb['id']}")
    assert ui_page.get_by_text(CSV_NAME, exact=False).first.is_visible(timeout=15_000)


def test_playwright_tool_registered(ui_page: Page) -> None:
    open_tool_editor(ui_page, TOOL_NAME)
    assert ui_page.get_by_text(re.compile(r"search_live_jobs", re.I)).first.is_visible(timeout=15_000)


def test_playwright_tool_calls_local_server(ui_page: Page) -> None:
    open_tool_editor(ui_page, TOOL_NAME)
    body = ui_page.locator("body").inner_text()
    assert "search_live_jobs" in body
    assert "host.docker.internal:5005" in body


def test_playwright_model_system_prompt_and_native_fc(
    ui_page: Page, require_stack: OpenWebUIClient
) -> None:
    preset = require_stack.ensure_model_preset()
    system = preset.get("params", {}).get("system") or preset.get("meta", {}).get("system") or ""
    assert "search_live_jobs" in system
    assert "ai-job-postings" in system

    open_model_settings(ui_page, CHAT_MODEL)
    body = ui_page.locator("body").inner_text()
    assert "System Prompt" in body
    assert preset["params"]["function_calling"] == "native"
    # Full prompt text is verified via API preset above; UI may keep textarea collapsed.

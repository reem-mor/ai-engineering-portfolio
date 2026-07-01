"""Playwright UI helpers for Open WebUI hw07 E2E."""

from __future__ import annotations

import os
import re
import time
from typing import Pattern

from playwright.sync_api import Page, expect

from e2e.fixtures import (
    CHAT_MODEL,
    OPEN_WEBUI_EMAIL,
    OPEN_WEBUI_PASSWORD,
    TOOL_NAME,
)

OPEN_WEBUI_URL = os.environ.get("OPEN_WEBUI_URL", "http://localhost:3000")


def dismiss_modals(page: Page) -> None:
    for pattern in (
        re.compile(r"okay, let's go!", re.I),
        re.compile(r"got it", re.I),
        re.compile(r"close toast", re.I),
    ):
        btn = page.get_by_role("button", name=pattern)
        try:
            if btn.first.is_visible(timeout=500):
                btn.first.click(timeout=2000)
                page.wait_for_timeout(400)
        except Exception:
            pass


def mask_sensitive_fields(page: Page) -> None:
    page.evaluate(
        """() => {
        document.querySelectorAll('input[type="password"], input[name*="key" i]').forEach(el => {
            if (el instanceof HTMLInputElement) { el.value = '***'; }
        });
    }"""
    )


def screenshot_page(page: Page, path: str, *, full_page: bool = False) -> None:
    page.set_viewport_size({"width": 1920, "height": 1080})
    mask_sensitive_fields(page)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)
    page.screenshot(path=path, full_page=full_page)


def screenshot_chat_exchange(page: Page, path: str) -> None:
    page.set_viewport_size({"width": 1920, "height": 1080})
    mask_sensitive_fields(page)
    page.wait_for_timeout(600)

    log_items = page.locator(
        '[aria-label="Chat Conversation"] listitem, [role="log"] listitem, [role="log"] > li'
    )
    count = log_items.count()
    if count >= 2:
        user_item = log_items.nth(count - 2)
        assistant_item = log_items.nth(count - 1)
        assistant_item.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        user_box = user_item.bounding_box()
        assistant_box = assistant_item.bounding_box()
        if user_box and assistant_box:
            x = max(0, min(user_box["x"], assistant_box["x"]) - 40)
            y = max(0, user_box["y"] - 24)
            width = min(1920 - x, max(user_box["width"], assistant_box["width"]) + 80)
            height = min(1080 - y, assistant_box["y"] + assistant_box["height"] - user_box["y"] + 48)
            page.screenshot(path=path, clip={"x": x, "y": y, "width": width, "height": height})
            return

    conversation = page.locator('[aria-label="Chat Conversation"]').first
    if conversation.is_visible():
        conversation.scroll_into_view_if_needed()
        conversation.screenshot(path=path)
        return

    screenshot_page(page, path)


def goto_path(page: Page, path: str) -> None:
    page.goto(f"{OPEN_WEBUI_URL}{path}", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    dismiss_modals(page)
    ensure_authenticated(page)


def ensure_authenticated(page: Page) -> None:
    sign_in = page.get_by_role("button", name=re.compile(r"^sign in$", re.I))
    try:
        if not sign_in.is_visible(timeout=1000):
            return
    except Exception:
        return

    email = os.environ.get("OPEN_WEBUI_EMAIL", OPEN_WEBUI_EMAIL)
    password = os.environ.get("OPEN_WEBUI_PASSWORD", OPEN_WEBUI_PASSWORD)
    page.get_by_placeholder(re.compile(r"email", re.I)).fill(email)
    page.get_by_placeholder(re.compile(r"password", re.I)).fill(password)
    sign_in.click()
    page.wait_for_load_state("networkidle")
    dismiss_modals(page)


def upload_csv_to_collection(page: Page, csv_path: str, collection_name: str, csv_name: str) -> None:
    goto_path(page, "/workspace/knowledge")
    page.get_by_text(collection_name, exact=False).first.click(timeout=30_000)
    page.wait_for_url(re.compile(r"/workspace/knowledge/[a-f0-9-]+", re.I), timeout=30_000)

    if page.get_by_text(csv_name, exact=False).first.is_visible(timeout=3000):
        return

    page.locator('input[type="file"]').first.set_input_files(csv_path)
    expect(page.get_by_text(csv_name, exact=False).first).to_be_visible(timeout=120_000)


def wait_for_knowledge_indexed(page: Page, csv_name: str, timeout_ms: int = 300_000) -> None:
    expect(page.get_by_text(re.compile(csv_name, re.I)).first).to_be_visible(timeout=120_000)
    deadline = time.time() + timeout_ms / 1000

    while time.time() < deadline:
        file_row = page.locator("button, div, li").filter(has_text=re.compile(csv_name, re.I)).first
        row_text = file_row.inner_text() if file_row.count() else ""
        has_size = re.search(r"(MB|KB|GB|bytes|B\b)", row_text, re.I)
        row_busy = re.search(r"uploading|processing|pending|spinner", row_text, re.I)

        if has_size and not row_busy:
            page.wait_for_timeout(15_000)
            return

        page.wait_for_timeout(5000)
        page.reload(wait_until="domcontentloaded")
        dismiss_modals(page)

    body = page.locator("body").inner_text()
    if re.search(rf"{re.escape(csv_name)}[\s\S]{{0,120}}(MB|KB|GB|bytes)", body, re.I):
        return
    raise TimeoutError(f"Knowledge indexing did not complete for {csv_name}")


def start_new_chat(page: Page) -> None:
    goto_path(page, "/")
    new_chat = page.get_by_role("link", name=re.compile(r"new chat", re.I)).or_(
        page.get_by_role("button", name=re.compile(r"new chat", re.I))
    )
    if new_chat.first.is_visible(timeout=3000):
        new_chat.first.click()
        page.wait_for_timeout(400)


def attach_knowledge_collection(page: Page, name: str) -> None:
    input_box = _chat_input(page)
    input_box.first.click()
    input_box.first.fill(f"#{name} ")


def select_chat_model(page: Page, model_name: str = CHAT_MODEL) -> None:
    selector = page.get_by_role("button", name=re.compile(r"select a model", re.I))
    if selector.is_visible(timeout=3000):
        selector.click()
        page.get_by_text(model_name, exact=False).first.click(timeout=30_000)
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        return

    model_btn = page.locator("button, div").filter(has_text=re.compile(r"llama3\.2|select a model", re.I)).first
    if model_btn.is_visible(timeout=3000):
        model_btn.click()
        page.get_by_text(model_name, exact=False).first.click(timeout=15_000)
        page.keyboard.press("Escape")


def _chat_input(page: Page):
    return (
        page.locator("#chat-input")
        .or_(page.locator('[contenteditable="true"]'))
        .or_(page.get_by_placeholder(re.compile(r"send a message|message|ask|chat", re.I)))
        .or_(page.locator("textarea").last)
    )


def send_chat_message(page: Page, message: str) -> None:
    input_box = _chat_input(page)
    input_box.first.click(timeout=30_000)
    input_box.first.fill("")
    input_box.first.fill(message)
    page.wait_for_timeout(300)

    voice = page.get_by_role("button", name=re.compile(r"voice input", re.I))
    if voice.is_visible(timeout=2000):
        toolbar = voice.locator("xpath=ancestor::div[1]")
        buttons = toolbar.locator("button")
        for i in range(buttons.count() - 1, -1, -1):
            btn = buttons.nth(i)
            label = (btn.get_attribute("aria-label") or "").lower()
            if "voice" in label:
                continue
            btn.click()
            page.wait_for_timeout(800)
            if not _message_still_in_composer(page, message):
                return

    page.keyboard.press("Enter")
    page.wait_for_timeout(500)
    if _message_still_in_composer(page, message):
        page.keyboard.press("Control+Enter")


def _message_still_in_composer(page: Page, message: str) -> bool:
    snippet = message[: min(24, len(message))]
    text = _chat_input(page).first.inner_text()
    return bool(snippet) and snippet in text


def _assistant_messages(page: Page) -> list[str]:
    items = page.locator(
        '[aria-label="Chat Conversation"] listitem, [role="log"] listitem, [role="log"] > li'
    )
    texts: list[str] = []
    for i in range(items.count()):
        text = items.nth(i).inner_text().strip()
        if text:
            texts.append(text)
    return texts


def _is_still_generating(page: Page) -> bool:
    try:
        if page.get_by_role("button", name=re.compile(r"stop|cancel", re.I)).first.is_visible(timeout=500):
            return True
    except Exception:
        pass

    assistant = page.locator(
        '[aria-label="Chat Conversation"] listitem:last-child, [role="log"] listitem:last-child'
    ).last
    if assistant.count() == 0:
        return False

    skeleton = assistant.locator('[class*="skeleton"], [class*="animate-pulse"]')
    if skeleton.count() > 0:
        return True

    text = assistant.inner_text().strip()
    if len(text) < 40:
        return True
    if re.search(r"^(thinking|generating|\.\.\.)", text, re.I):
        return True
    return False


def wait_for_assistant_reply(
    page: Page,
    hints: list[str | Pattern[str]],
    timeout_ms: int = 600_000,
) -> None:
    deadline = time.time() + timeout_ms / 1000
    compiled = [re.compile(h, re.I) if isinstance(h, str) else h for h in hints]

    while time.time() < deadline:
        if _is_still_generating(page):
            page.wait_for_timeout(3000)
            continue

        messages = _assistant_messages(page)
        if len(messages) < 2:
            page.wait_for_timeout(3000)
            continue

        assistant_text = messages[-1]
        if len(assistant_text) < 80:
            page.wait_for_timeout(3000)
            continue

        if any(p.search(assistant_text) for p in compiled):
            page.wait_for_timeout(1500)
            if not _is_still_generating(page):
                return

        page.wait_for_timeout(3000)

    raise TimeoutError(f"Assistant reply did not match hints within {timeout_ms}ms: {hints}")


def wait_for_tool_invocation(
    page: Page,
    hints: list[str | Pattern[str]],
    timeout_ms: int = 120_000,
) -> None:
    deadline = time.time() + timeout_ms / 1000
    compiled = [re.compile(h, re.I) if isinstance(h, str) else h for h in hints]

    while time.time() < deadline:
        body = page.locator("body").inner_text()
        if any(p.search(body) for p in compiled):
            return
        page.wait_for_timeout(2000)

    raise TimeoutError(f"Tool invocation UI did not appear: {hints}")


def enable_tool_in_chat(page: Page, tool_name: str = TOOL_NAME) -> None:
    integrations = page.get_by_role("button", name=re.compile(r"integrations|tools", re.I))
    if integrations.first.is_visible(timeout=3000):
        integrations.first.click()
        row = page.get_by_text(re.compile(tool_name, re.I)).first
        if row.is_visible(timeout=5000):
            row.click()
        page.keyboard.press("Escape")


def open_workspace_tools(page: Page) -> None:
    goto_path(page, "/workspace/tools")
    expect(page.get_by_text(re.compile(r"Tools|Create", re.I)).first).to_be_visible(timeout=30_000)


def open_tool_editor(page: Page, tool_name: str = TOOL_NAME) -> None:
    goto_path(page, "/workspace/tools")
    row = page.get_by_text(re.compile(tool_name, re.I)).first
    row.click(timeout=30_000)
    page.wait_for_timeout(1200)
    expect(page.get_by_text(re.compile(r"search_live_jobs", re.I)).first).to_be_visible(timeout=30_000)


def open_model_settings(page: Page, model_name: str = CHAT_MODEL) -> None:
    goto_path(page, "/admin/settings/models")
    page.get_by_text(model_name, exact=False).first.click(timeout=30_000)
    page.wait_for_timeout(1000)
    expect(page.get_by_text(re.compile(r"Function Calling|function calling|System", re.I)).first).to_be_visible(
        timeout=30_000
    )


def open_saved_chat(page: Page, chat_id: str, *, wait_for: str) -> None:
    goto_path(page, f"/c/{chat_id}")
    page.wait_for_timeout(2500)
    deadline = time.time() + 60
    while time.time() < deadline:
        if "Loading..." not in page.locator("body").inner_text():
            break
        page.wait_for_timeout(1000)
    pattern = re.compile(re.escape(wait_for[: min(28, len(wait_for))]), re.I)
    expect(page.get_by_text(pattern).first).to_be_visible(timeout=60_000)


def configure_model_native_tools(page: Page, model_name: str = CHAT_MODEL) -> None:
    goto_path(page, "/admin/settings/models")
    page.get_by_text(model_name, exact=False).first.click(timeout=30_000)
    page.wait_for_timeout(800)

    advanced = page.get_by_text(re.compile(r"Advanced Parameters|Advanced", re.I)).first
    if advanced.is_visible(timeout=5000):
        advanced.click()
        page.wait_for_timeout(500)

    fn_call = page.locator("select, button").filter(has_text=re.compile(r"Function Calling|function calling", re.I))
    if fn_call.first.is_visible(timeout=3000):
        fn_call.first.click()
        native = page.get_by_text(re.compile(r"^Native$|native", re.I)).first
        if native.is_visible(timeout=3000):
            native.click()

    save = page.get_by_role("button", name=re.compile(r"save|update", re.I))
    if save.first.is_visible(timeout=3000):
        save.first.click()
        page.wait_for_timeout(1000)

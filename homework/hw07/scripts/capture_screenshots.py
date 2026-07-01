#!/usr/bin/env python3
"""Capture HW07 submission screenshots (00-08) via Playwright."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

HW07 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07))

import owui_kb_setup  # noqa: E402
from env_loader import load_hw07_env  # noqa: E402

load_hw07_env()

SHOTS = HW07 / "screenshots"

OWUI_URL = os.getenv("OWUI_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("OWUI_EMAIL", "")
PASSWORD = os.getenv("OWUI_PASSWORD", "")
MODEL_ID = "cve-intelligence-assistant"
KB_NAME = "CVE Intelligence"


def resolve_kb_id() -> str:
    env_id = os.getenv("HW07_KB_ID", "").strip()
    if env_id:
        return env_id
    token = owui_kb_setup.signin_token(OWUI_URL, EMAIL, PASSWORD)
    return owui_kb_setup.resolve_kb_id(OWUI_URL, token, KB_NAME)


def login(page) -> None:
    if not EMAIL:
        raise RuntimeError("Set OWUI_EMAIL in homework/hw07/.env")
    page.goto(f"{OWUI_URL}/auth", wait_until="networkidle")
    if page.locator('input[type="email"], input[name="email"]').count():
        page.fill('input[type="email"], input[name="email"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)
        page.get_by_role("button", name="Sign in").click()
        deadline = time.time() + 60
        while time.time() < deadline:
            if "/auth" not in page.url:
                break
            if page.locator("#sidebar, nav, [data-testid='chat-input']").count():
                break
            page.wait_for_timeout(500)
        else:
            SHOTS.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(SHOTS / "login_failed.png"), full_page=True)
            raise RuntimeError(f"Login failed — current URL: {page.url}")
    page.wait_for_timeout(1500)


def shot(page, name: str, *, full_page: bool = True) -> None:
    path = SHOTS / name
    page.screenshot(path=str(path), full_page=full_page)
    print(f"[+] {path.name}")


def capture_tool_openapi(page) -> None:
    page.goto("http://localhost:5005/docs", wait_until="networkidle")
    shot(page, "00-tool-server-openapi.png")


def capture_kb(page, kb_id: str) -> None:
    page.goto(f"{OWUI_URL}/workspace/knowledge/{kb_id}", wait_until="networkidle")
    page.wait_for_timeout(2000)
    shot(page, "01-kb-upload.png")
    shot(page, "02-kb-indexed.png")


def capture_tool_registered(page) -> None:
    page.goto(f"{OWUI_URL}/admin/settings/tools", wait_until="networkidle")
    page.wait_for_timeout(2000)
    shot(page, "04-tool-registered.png")


def capture_model_settings(page) -> None:
    page.goto(f"{OWUI_URL}/workspace/models/edit?id={MODEL_ID}", wait_until="networkidle")
    page.wait_for_timeout(2000)
    shot(page, "06-model-system-prompt.png", full_page=True)


def chat_and_shot(page, prompt: str, filename: str, *, wait_s: int = 180) -> None:
    page.goto(f"{OWUI_URL}/?model={MODEL_ID}", wait_until="networkidle")
    page.wait_for_timeout(1500)
    textarea = page.locator("#chat-input, textarea").first
    textarea.fill(prompt)
    page.keyboard.press("Enter")
    deadline = time.time() + wait_s
    while time.time() < deadline:
        if page.locator("text=lookup_cve").count() and filename == "05-tool-function-io.png":
            break
        if page.locator(".prose, .markdown-prose").last.count():
            text = page.locator(".prose, .markdown-prose").last.inner_text()
            if len(text) > 80 and "Thinking" not in text[-20:]:
                break
        page.wait_for_timeout(3000)
    page.wait_for_timeout(2000)
    shot(page, filename, full_page=True)


def capture_docker(page) -> None:
    out = subprocess.run(
        ["docker", "compose", "ps"],
        cwd=HW07,
        capture_output=True,
        text=True,
        check=True,
    )
    html = f"""<!DOCTYPE html><html><head><style>
    body{{font-family:Consolas,monospace;background:#0d1117;color:#c9d1d9;padding:24px}}
    pre{{white-space:pre-wrap;font-size:14px;line-height:1.5}}
    h1{{font-size:18px;color:#58a6ff}}
    </style></head><body>
    <h1>docker compose ps — homework/hw07</h1>
    <pre>{out.stdout}</pre></body></html>"""
    tmp = SHOTS / "_docker.html"
    tmp.write_text(html, encoding="utf-8")
    page.goto(tmp.as_uri(), wait_until="load")
    shot(page, "08-docker-healthy.png", full_page=False)
    tmp.unlink(missing_ok=True)


def main() -> int:
    if not PASSWORD:
        print("Set OWUI_PASSWORD", file=sys.stderr)
        return 2
    if not EMAIL:
        print("Set OWUI_EMAIL", file=sys.stderr)
        return 2
    SHOTS.mkdir(parents=True, exist_ok=True)

    try:
        kb_id = resolve_kb_id()
        print(f"Using KB id: {kb_id}")
    except (RuntimeError, httpx.HTTPError) as exc:
        print(f"ERROR: cannot resolve KB id: {exc}", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        try:
            capture_tool_openapi(page)
            login(page)
            capture_kb(page, kb_id)
            capture_tool_registered(page)
            capture_model_settings(page)

            chat_and_shot(
                page,
                "Which CVEs in my dataset affected Apache Struts, and what were their CVSS scores?",
                "03-kb-answer.png",
                wait_s=300,
            )
            chat_and_shot(
                page,
                "What is the current EPSS score and KEV status for CVE-2021-44228? Use lookup_cve.",
                "05-tool-function-io.png",
                wait_s=300,
            )
            chat_and_shot(
                page,
                "What is the current EPSS score and KEV status for CVE-2021-44228?",
                "07-live-tool-answer.png",
                wait_s=300,
            )
            capture_docker(page)
        except (RuntimeError, PlaywrightTimeout) as exc:
            SHOTS.mkdir(parents=True, exist_ok=True)
            try:
                page.screenshot(path=str(SHOTS / "login_failed.png"), full_page=True)
            except Exception:
                pass
            print(f"ERROR: {exc}", file=sys.stderr)
            if hasattr(page, "url"):
                print(f"Current URL: {page.url}", file=sys.stderr)
            browser.close()
            return 1
        browser.close()

    print(f"\nDone — screenshots in {SHOTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

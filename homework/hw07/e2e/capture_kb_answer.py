"""Capture screenshot 03-kb-answer via API chat (faster than UI typing on 3B)."""

from __future__ import annotations

import sys
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent.parent
if str(HW07_ROOT) not in sys.path:
    sys.path.insert(0, str(HW07_ROOT))

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from e2e.capture_screenshots import CSV_PATH, SCREENSHOT_DIR, check_preconditions, setup_via_api
from e2e.open_webui_helpers import dismiss_modals, ensure_authenticated, open_saved_chat, screenshot_chat_exchange

OPEN_WEBUI_URL = "http://localhost:3000"


def main() -> int:
    load_dotenv(HW07_ROOT / ".env")
    load_dotenv(HW07_ROOT.parent.parent / ".env")
    check_preconditions()
    client = setup_via_api(CSV_PATH, skip_kb_upload=True)
    print("Running KB chat via API (may take several minutes on llama3.2:3b)...")
    _prompt, answer, chat_id = client.run_kb_chat_evidence()
    print(f"KB answer length: {len(answer)}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(OPEN_WEBUI_URL, wait_until="domcontentloaded")
        dismiss_modals(page)
        ensure_authenticated(page)
        open_saved_chat(page, chat_id, wait_for=answer[:40])
        page.wait_for_timeout(1500)
        screenshot_chat_exchange(page, str(SCREENSHOT_DIR / "03-kb-answer.png"))
        browser.close()

    client.close()
    print("Saved screenshots/03-kb-answer.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""One-off: UI KB upload + wait for indexing."""

from __future__ import annotations

import sys
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07_ROOT))

from playwright.sync_api import sync_playwright

from e2e.fixtures import KB_COLLECTION_NAME
from e2e.open_webui_client import OpenWebUIClient
from e2e.open_webui_helpers import (
    goto_path,
    upload_csv_to_collection,
    wait_for_knowledge_indexed,
)

CSV = HW07_ROOT / "data" / "job_postings.csv"


def main() -> int:
    client = OpenWebUIClient()
    client.sign_in()
    kb = client.ensure_knowledge_collection()
    print(f"kb id {kb['id']}", flush=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        goto_path(page, f"/workspace/knowledge/{kb['id']}")
        print("on kb page", flush=True)
        csv_name = CSV.name
        if not page.get_by_text(csv_name, exact=False).first.is_visible(timeout=3000):
            print("uploading csv...", flush=True)
            upload_csv_to_collection(page, str(CSV), KB_COLLECTION_NAME, csv_name)
        else:
            print("csv already visible", flush=True)
        print("waiting for index...", flush=True)
        wait_for_knowledge_indexed(page, csv_name, timeout_ms=2_400_000)
        print("INDEXED OK", flush=True)
        browser.close()

    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

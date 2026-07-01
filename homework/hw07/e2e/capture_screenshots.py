"""End-to-end Open WebUI setup + screenshot capture for hw07."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent.parent
if str(HW07_ROOT) not in sys.path:
    sys.path.insert(0, str(HW07_ROOT))

import httpx
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from e2e.fixtures import (
    CHAT_MODEL,
    KB_ANSWER_HINTS,
    KB_COLLECTION_NAME,
    PROMPT_KB_SKILLS,
    TOOL_NAME,
    OLLAMA_PULL_MODEL,
)
from e2e.open_webui_client import OpenWebUIClient
from e2e.open_webui_helpers import (
    dismiss_modals,
    ensure_authenticated,
    goto_path,
    attach_knowledge_collection,
    open_model_settings,
    open_saved_chat,
    open_tool_editor,
    open_workspace_tools,
    screenshot_chat_exchange,
    screenshot_page,
    select_chat_model,
    send_chat_message,
    start_new_chat,
    upload_csv_to_collection,
    wait_for_assistant_reply,
    wait_for_knowledge_indexed,
)

CSV_PATH = HW07_ROOT / "data" / "job_postings.csv"
SCREENSHOT_DIR = HW07_ROOT / "screenshots"
OPEN_WEBUI_URL = os.environ.get("OPEN_WEBUI_URL", "http://localhost:3000")
TOOL_SERVER_HEALTH = os.environ.get(
    "TOOL_SERVER_HEALTH", "http://127.0.0.1:5005/health"
)
MIN_CSV_BYTES = 50_000


class PipelineError(RuntimeError):
    pass


def _load_env() -> None:
    load_dotenv(HW07_ROOT / ".env")
    load_dotenv(HW07_ROOT.parent.parent / ".env")


def warmup_ollama() -> None:
    print(f"Warming up {OLLAMA_PULL_MODEL} in Ollama (first token may take 1-2 min)...")
    try:
        result = subprocess.run(
            ["docker", "exec", "hw07-ollama", "ollama", "run", OLLAMA_PULL_MODEL, "Reply with OK only."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        if result.returncode != 0:
            print(f"WARN: Ollama warmup stderr: {result.stderr[:500]}")
        else:
            print("Ollama warmup complete.")
    except subprocess.TimeoutExpired:
        print(f"WARN: Ollama warmup timed out after 300s — continuing (model may still respond slowly)")


def check_preconditions() -> str:
    if not CSV_PATH.is_file():
        raise PipelineError(
            f"Missing {CSV_PATH}. Run: python data/download_dataset.py"
        )
    if CSV_PATH.stat().st_size < MIN_CSV_BYTES:
        raise PipelineError(
            f"{CSV_PATH} looks like the dev fixture ({CSV_PATH.stat().st_size} bytes). "
            "Delete it and run: python data/download_dataset.py"
        )

    docker_ps = subprocess.run(
        ["docker", "compose", "ps"],
        cwd=HW07_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for name in ("hw07-ollama", "hw07-open-webui"):
        if name not in docker_ps:
            raise PipelineError(f"Container {name} not running")
    if "healthy" not in docker_ps.lower():
        raise PipelineError(f"Containers not healthy:\n{docker_ps}")

    webui = httpx.get(f"{OPEN_WEBUI_URL}/health", timeout=15.0)
    webui.raise_for_status()

    tools = httpx.get(TOOL_SERVER_HEALTH, timeout=15.0)
    tools.raise_for_status()
    body = tools.json()
    if body.get("status") != "ok":
        raise PipelineError(f"Tool server unhealthy: {body}")

    return docker_ps


def setup_via_api(
    csv_path: Path, *, refresh_kb: bool = False, skip_kb_upload: bool = False
) -> OpenWebUIClient:
    client = OpenWebUIClient(OPEN_WEBUI_URL)
    user = client.sign_in()
    print(f"Signed in as {user.get('email')} ({user.get('role')})")

    model = client.ensure_chat_model()
    print(f"Ollama model ready: {model}")
    preset = client.ensure_model_preset()
    print(
        f"Model preset: {preset['id']} function_calling=native "
        f"toolIds={preset['meta'].get('toolIds')} system_prompt=set"
    )

    kb = client.ensure_knowledge_collection()
    print(f"Knowledge base: {kb['name']} ({kb['id']})")

    linked = client.list_knowledge_files(kb["id"])
    pending = client.list_pending_knowledge_files(kb["id"])
    if skip_kb_upload:
        print("Skipping KB upload (resume mode — assuming CSV already indexed)")
    elif linked and not refresh_kb:
        print("CSV already attached to knowledge base")
    elif pending and not refresh_kb:
        print(f"Waiting for in-flight KB upload ({len(pending)} pending)...")
        client._wait_for_knowledge_file(kb["id"])
    elif refresh_kb and linked:
        print(f"Re-uploading {csv_path.name} via API ({csv_path.stat().st_size} bytes)...")
        client.refresh_knowledge_csv(kb["id"], csv_path)
    else:
        print(f"Uploading {csv_path.name} via API ({csv_path.stat().st_size} bytes)...")
        client.upload_knowledge_file(kb["id"], csv_path)

    tool = client.ensure_tool()
    print(f"Tool registered: {tool.get('name') or tool.get('id')}")

    client.clear_chats()
    return client


def clean_screenshots() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for png in SCREENSHOT_DIR.glob("*.png"):
        png.unlink()


def capture_all(
    headless: bool = True,
    *,
    refresh_kb: bool = False,
    no_clean: bool = False,
    skip_warmup: bool = False,
    kb_ready: bool = False,
    from_step: int = 0,
    to_step: int = 8,
) -> None:
    _load_env()
    docker_ps = check_preconditions()
    csv_name = CSV_PATH.name

    if not no_clean and from_step == 0:
        clean_screenshots()
    else:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    if not skip_warmup and from_step <= 3:
        warmup_ollama()

    client = setup_via_api(
        CSV_PATH,
        refresh_kb=refresh_kb and from_step <= 2 and not kb_ready,
        skip_kb_upload=kb_ready or from_step >= 3,
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        if from_step <= 0 and to_step >= 0:
            print("[step 0] signed-in")
            page.goto(OPEN_WEBUI_URL, wait_until="domcontentloaded")
            dismiss_modals(page)
            ensure_authenticated(page)
            screenshot_page(page, str(SCREENSHOT_DIR / "00-signed-in.png"))

        if from_step <= 1 and to_step >= 1:
            print("[step 1] kb-upload")
            goto_path(page, f"/workspace/knowledge/{client.ensure_knowledge_collection()['id']}")
            if not page.get_by_text(csv_name, exact=False).first.is_visible(timeout=3000):
                upload_csv_to_collection(page, str(CSV_PATH), KB_COLLECTION_NAME, csv_name)
            screenshot_page(page, str(SCREENSHOT_DIR / "01-kb-upload.png"), full_page=True)

        if from_step <= 2 and to_step >= 2:
            print("[step 2] kb-indexed")
            if from_step == 2:
                goto_path(page, f"/workspace/knowledge/{client.ensure_knowledge_collection()['id']}")
            wait_for_knowledge_indexed(page, csv_name, timeout_ms=2_400_000)
            screenshot_page(page, str(SCREENSHOT_DIR / "02-kb-indexed.png"), full_page=True)

        if from_step <= 3 and to_step >= 3:
            print("[step 3] kb-answer via UI chat (may take 10-30 min on llama3.2:3b)...")
            page.goto(OPEN_WEBUI_URL, wait_until="domcontentloaded")
            dismiss_modals(page)
            ensure_authenticated(page)
            start_new_chat(page)
            select_chat_model(page, CHAT_MODEL)
            attach_knowledge_collection(page, KB_COLLECTION_NAME)
            send_chat_message(page, PROMPT_KB_SKILLS)
            wait_for_assistant_reply(page, KB_ANSWER_HINTS, timeout_ms=1_800_000)
            screenshot_chat_exchange(page, str(SCREENSHOT_DIR / "03-kb-answer.png"))

        if from_step <= 4 and to_step >= 4:
            print("[step 4] tool-registered")
            open_workspace_tools(page)
            page.get_by_text(re.compile(r"HW07 Live Job Search|search_live_jobs", re.I)).first.wait_for(
                timeout=30_000
            )
            screenshot_page(page, str(SCREENSHOT_DIR / "04-tool-registered.png"), full_page=True)

        if from_step <= 5 and to_step >= 5:
            print("[step 5] tool-function-io")
            open_tool_editor(page, TOOL_NAME)
            screenshot_page(page, str(SCREENSHOT_DIR / "05-tool-function-io.png"), full_page=True)

        if from_step <= 6 and to_step >= 6:
            print("[step 6] model-system-prompt")
            open_model_settings(page, CHAT_MODEL)
            screenshot_page(page, str(SCREENSHOT_DIR / "06-model-system-prompt.png"), full_page=True)

        if from_step <= 7 and to_step >= 7:
            print("[step 7] live-tool-answer via API + UI screenshot...")
            _, tool_answer, tool_chat_id = client.run_tool_chat_evidence()
            if len(tool_answer) < 40:
                raise PipelineError(f"Tool answer too short: {tool_answer[:300]!r}")
            tool_wait = "Mock Tech IL" if "Mock Tech IL" in tool_answer else tool_answer[:28]
            open_saved_chat(page, tool_chat_id, wait_for=tool_wait)
            page.wait_for_timeout(1500)
            screenshot_chat_exchange(page, str(SCREENSHOT_DIR / "07-live-tool-answer.png"))

        if from_step <= 8 and to_step >= 8:
            print("[step 8] docker-healthy")
            page.set_content(
                f"""<!DOCTYPE html><html><head><meta charset=utf-8>
                <style>body{{font-family:Consolas,monospace;background:#1e1e1e;color:#d4d4d4;padding:24px}}
                h1{{color:#569cd6;font-size:18px}} pre{{white-space:pre-wrap;font-size:13px}}</style></head>
                <body><h1>docker compose ps — hw07 stack (healthy)</h1>
                <pre>{docker_ps}</pre></body></html>"""
            )
            page.screenshot(path=str(SCREENSHOT_DIR / "08-docker-healthy.png"), full_page=True)

        browser.close()

    client.close()
    print("Screenshot capture complete:")
    for png in sorted(SCREENSHOT_DIR.glob("*.png")):
        print(f"  {png.name} ({png.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description="HW07 Open WebUI E2E setup + screenshots")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--setup-only", action="store_true", help="API setup without screenshots")
    parser.add_argument("--refresh-kb", action="store_true", help="Re-upload CSV to knowledge base")
    parser.add_argument("--no-clean", action="store_true", help="Keep existing PNGs")
    parser.add_argument("--skip-warmup", action="store_true", help="Skip Ollama warmup")
    parser.add_argument("--kb-ready", action="store_true", help="Skip KB upload (already indexed)")
    parser.add_argument(
        "--from-step",
        type=int,
        default=0,
        metavar="N",
        help="Resume from step N (0=signed-in … 8=docker)",
    )
    parser.add_argument(
        "--to-step",
        type=int,
        default=8,
        metavar="N",
        help="Stop after step N (0=signed-in … 8=docker)",
    )
    args = parser.parse_args()

    try:
        if args.setup_only:
            _load_env()
            check_preconditions()
            if not args.skip_warmup:
                warmup_ollama()
            client = setup_via_api(CSV_PATH, refresh_kb=args.refresh_kb, skip_kb_upload=False)
            client.close()
            print("Setup complete.")
            return 0
        capture_all(
            headless=not args.headed,
            refresh_kb=args.refresh_kb,
            no_clean=args.no_clean,
            skip_warmup=args.skip_warmup,
            kb_ready=args.kb_ready,
            from_step=args.from_step,
            to_step=args.to_step,
        )
        return 0
    except (PipelineError, TimeoutError, httpx.HTTPError) as exc:
        print(f"PIPELINE FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

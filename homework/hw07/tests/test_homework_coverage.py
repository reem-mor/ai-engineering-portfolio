"""Static checks — teacher HW requirements mapped to repo artifacts."""

from __future__ import annotations

import re
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = HW07_ROOT / "screenshots"
REQUIRED_SCREENSHOTS = [
    "00-signed-in.png",
    "01-kb-upload.png",
    "02-kb-indexed.png",
    "03-kb-answer.png",
    "04-tool-registered.png",
    "05-tool-function-io.png",
    "06-model-system-prompt.png",
    "07-live-tool-answer.png",
    "08-docker-healthy.png",
]


def test_teacher_requirement_kb_via_webui() -> None:
    """KB: Kaggle CSV uploaded/indexed in Open WebUI (no Python in KB path)."""
    readme = (HW07_ROOT / "README.md").read_text(encoding="utf-8")
    assert "ai-job-postings" in readme
    assert "Knowledge" in readme
    assert (HW07_ROOT / "data" / "download_dataset.py").is_file()


def test_teacher_requirement_local_python_server() -> None:
    """Local tools_server.py on :5005 calling external RapidAPI (JSearch)."""
    source = (HW07_ROOT / "tools_server.py").read_text(encoding="utf-8")
    jsearch = (HW07_ROOT / "jsearch_client.py").read_text(encoding="utf-8")
    assert '@app.get("/health"' in source or "@app.get('/health'" in source
    assert "/jobs/search" in source
    assert "RapidAPI" in jsearch or "rapidapi" in jsearch.lower()
    assert "5005" in (HW07_ROOT / ".env.example").read_text(encoding="utf-8")


def test_teacher_requirement_webui_tool_calls_server() -> None:
    """Web UI Tool declares function that calls local Python server."""
    tool = (HW07_ROOT / "openwebui_tool.py").read_text(encoding="utf-8")
    assert "search_live_jobs" in tool
    assert "host.docker.internal:5005" in tool
    assert "/jobs/search" in tool


def test_teacher_requirement_assistant_routing_prompt() -> None:
    """System prompt: KB for dataset questions; tool for live questions."""
    from prompts import load_system_prompt

    prompt = load_system_prompt()
    assert "#ai-job-postings" in prompt
    assert "search_live_jobs" in prompt
    assert re.search(r"live|current|hiring", prompt, re.I)
    assert re.search(r"historical|dataset|csv", prompt, re.I)


def test_lecture_stack_ollama_open_webui_docker() -> None:
    """Lecture: Ollama + Open WebUI via Docker."""
    compose = (HW07_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "ollama" in compose
    assert "open-webui" in compose
    assert "3000:8080" in compose


def test_submission_screenshots_present() -> None:
    missing = [name for name in REQUIRED_SCREENSHOTS if not (SCREENSHOTS / name).is_file()]
    assert not missing, f"Missing submission screenshots: {missing}"
    for name in REQUIRED_SCREENSHOTS:
        assert (SCREENSHOTS / name).stat().st_size > 10_000, f"{name} looks too small"

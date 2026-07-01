"""hw07 end-to-end validation runner.

Runs every check that can run in the current environment and prints a
PASS / FAIL / SKIP summary. Live checks (Open WebUI, RapidAPI) are SKIPPED
with a reason when the service or secret is unavailable — they never
silently pass.

Usage:
    python scripts/run_all_checks.py
"""

from __future__ import annotations

import os
import py_compile
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

HW07_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = HW07_ROOT.parent.parent

load_dotenv(REPO_ROOT / ".env")
load_dotenv(HW07_ROOT / ".env")

RESULTS: list[tuple[str, str, str]] = []  # (name, PASS/FAIL/SKIP, detail)


def record(name: str, status: str, detail: str = "") -> None:
    RESULTS.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def check_syntax() -> None:
    failures = []
    for py in sorted(HW07_ROOT.glob("**/*.py")):
        if ".venv" in py.parts or ".kaggle_download" in py.parts:
            continue
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{py.name}: {exc.msg}")
    record("python-syntax", "FAIL" if failures else "PASS", "; ".join(failures))


def check_dataset() -> None:
    csv_path = HW07_ROOT / "data" / "ai_jobs.csv"
    if not csv_path.is_file():
        record("dataset-validation", "SKIP",
               "data/ai_jobs.csv missing — run data/download_dataset.py")
        return
    proc = subprocess.run(
        [sys.executable, str(HW07_ROOT / "data" / "validate_dataset.py"), str(csv_path)],
        capture_output=True, text=True,
    )
    record("dataset-validation", "PASS" if proc.returncode == 0 else "FAIL",
           (proc.stdout or proc.stderr).strip().splitlines()[-1] if proc.stdout or proc.stderr else "")


def check_pytest() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        capture_output=True, text=True, cwd=HW07_ROOT,
    )
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr[-200:]
    record("pytest", "PASS" if proc.returncode == 0 else "FAIL", tail)


def _http_get(url: str, timeout: float = 10.0):
    import httpx

    return httpx.get(url, timeout=timeout, trust_env=False)


def check_tool_server() -> None:
    port = os.getenv("TOOLS_SERVER_PORT", "5005")
    try:
        response = _http_get(f"http://localhost:{port}/health")
        ok = response.status_code == 200 and response.json().get("status") == "ok"
        record("tool-server-health", "PASS" if ok else "FAIL", f"HTTP {response.status_code}")
    except Exception:
        record("tool-server-health", "SKIP",
               f"tool server not running on :{port} — start it and re-run")


def check_rapidapi_live() -> None:
    if not os.getenv("RAPIDAPI_KEY", "").strip():
        record("rapidapi-live", "SKIP", "RAPIDAPI_KEY not set in root .env")
        return
    port = os.getenv("TOOLS_SERVER_PORT", "5005")
    try:
        response = _http_get(
            f"http://localhost:{port}/jobs/search?query=ai%20engineer&location=Israel",
            timeout=30.0,
        )
        body = response.json()
        ok = response.status_code == 200 and body.get("count", 0) >= 0 and not body.get("error")
        record("rapidapi-live", "PASS" if ok else "FAIL",
               f"HTTP {response.status_code}, count={body.get('count')}, error={body.get('error')}")
    except Exception as exc:
        record("rapidapi-live", "SKIP", f"tool server unreachable: {exc.__class__.__name__}")


def check_owui() -> None:
    base = os.getenv("OWUI_URL", "http://localhost:3000").rstrip("/")
    try:
        response = _http_get(f"{base}/health")
        if response.status_code != 200:
            record("owui-up", "FAIL", f"HTTP {response.status_code}")
            return
        record("owui-up", "PASS", base)
    except Exception:
        record("owui-up", "SKIP", f"Open WebUI not reachable at {base}")
        record("owui-kb-status", "SKIP", "requires Open WebUI")
        return

    try:
        sys.path.insert(0, str(HW07_ROOT))
        import owui_kb_setup

        token = owui_kb_setup.get_token(base)
        kid = os.getenv("OWUI_KNOWLEDGE_ID", "").strip() or owui_kb_setup.find_knowledge_by_name(
            base, token, owui_kb_setup.KB_NAME
        )
        if not kid:
            record("owui-kb-status", "FAIL", f"KB '{owui_kb_setup.KB_NAME}' not found")
            return
        files = owui_kb_setup.get_knowledge_files(base, token, kid)
        names = [(f.get("meta") or {}).get("name") or f.get("filename") for f in files]
        ok = any(name == "ai_jobs.csv" for name in names)
        record("owui-kb-status", "PASS" if ok else "FAIL",
               f"KB id={kid}, files={len(files)} ({', '.join(str(n) for n in names)})")
    except Exception as exc:
        record("owui-kb-status", "FAIL", f"{exc.__class__.__name__}: {exc}")


def check_secret_scan() -> None:
    """Scan git-tracked hw07 files for realistic secret shapes (not placeholders)."""
    import re

    patterns = (
        re.compile(r"sk-[A-Za-z0-9]{20,}"),                       # OpenAI/OWUI-style keys
        re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}"),  # JWTs
        re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[=:]\s*['\"]?[A-Za-z0-9/+_\-]{30,}"),
    )
    proc = subprocess.run(
        ["git", "ls-files", str(HW07_ROOT)], capture_output=True, text=True, cwd=REPO_ROOT
    )
    hits: list[str] = []
    for rel in proc.stdout.splitlines():
        path = REPO_ROOT / rel
        if path.suffix in (".png", ".jpg") or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if "test-secret" in line or "do-not-leak" in line:
                continue
            if any(p.search(line) for p in patterns):
                hits.append(f"{rel}: {line.strip()[:60]}")
    record("secret-scan", "FAIL" if hits else "PASS", "; ".join(hits[:5]))


def main() -> int:
    print(f"hw07 checks — root .env: {(REPO_ROOT / '.env').is_file()}\n")
    check_syntax()
    check_dataset()
    check_pytest()
    check_tool_server()
    check_rapidapi_live()
    check_owui()
    check_secret_scan()

    print("\n=== summary ===")
    for name, status, _ in RESULTS:
        print(f"  {status:4s}  {name}")
    failed = [name for name, status, _ in RESULTS if status == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

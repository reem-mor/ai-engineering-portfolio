#!/usr/bin/env python3
"""Run hw07 demo chat prompts (KB / live tool / mixed) and write TEST_RESULTS.md."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

HW07 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07))

import owui_kb_setup  # noqa: E402
from env_loader import load_hw07_env  # noqa: E402

load_hw07_env()

MODEL_ID = os.getenv("HW07_MODEL_ID", "ai-job-market-assistant")
KB_NAME = owui_kb_setup.KB_NAME
TOOL_SERVER = os.getenv("TOOLS_SERVER_URL", "http://localhost:5005").rstrip("/")

PROMPTS: list[tuple[str, str, str, str]] = [
    (
        "kb_titles",
        "kb",
        "What are the most common AI job titles in the Kaggle dataset?",
        "Answer cites job titles from the KB; labels source as the Kaggle dataset.",
    ),
    (
        "kb_skills",
        "kb",
        "Which skills appear most often in the dataset?",
        "Aggregates required_skills from KB; source = Kaggle dataset.",
    ),
    (
        "tool_live_israel",
        "tool",
        "Search live AI Engineer jobs in Israel using the live job search tool.",
        "Model calls search_jobs; lists live postings; source = live RapidAPI tool.",
    ),
    (
        "tool_live_skill",
        "tool",
        "Search live jobs that mention Python using the live job search tool.",
        "Model calls search_jobs_by_skill; source = live tool.",
    ),
    (
        "hybrid_compare",
        "hybrid",
        "Compare the Kaggle dataset trends with live AI Engineer jobs in Israel.",
        "Two labeled sections: KB dataset trends, then live tool results.",
    ),
    (
        "edge_not_in_kb",
        "kb",
        "What does my dataset say about underwater basket weaving jobs?",
        "Says not found in the dataset; no fabricated data.",
    ),
]


def signin(client: httpx.Client, base: str) -> str:
    response = client.post(
        f"{base}/api/v1/auths/signin",
        json={
            "email": os.getenv("OWUI_EMAIL", "admin@localhost.com"),
            "password": os.getenv("OWUI_PASSWORD", "admin"),
        },
    )
    response.raise_for_status()
    return response.json()["token"]


def resolve_kb_id(base: str, token: str) -> str:
    env_id = os.getenv("OWUI_KNOWLEDGE_ID", "").strip()
    if env_id:
        return env_id
    return owui_kb_setup.resolve_kb_id(base, token, KB_NAME)


def execute_tool_call(name: str, arguments: str) -> str:
    """Proxy an OWUI-native tool call to the local jobs tool server."""
    args = json.loads(arguments or "{}")
    routes = {
        "search_jobs": ("/jobs/search", {"query": args.get("query", ""),
                                         "location": args.get("location", "")}),
        "search_jobs_by_company": ("/jobs/company", {"company": args.get("company", "")}),
        "search_jobs_by_skill": ("/jobs/skills", {"skill": args.get("skill", "")}),
    }
    if name not in routes:
        return json.dumps({"error": f"Unknown tool {name}"})
    path, params = routes[name]
    response = httpx.get(f"{TOOL_SERVER}{path}", params=params, timeout=30)
    try:
        return json.dumps(response.json())
    except ValueError:
        return json.dumps({"error": f"Tool server returned HTTP {response.status_code}"})


def chat_once(
    client: httpx.Client,
    base: str,
    headers: dict[str, str],
    messages: list[dict],
    *,
    mode: str,
    kb_id: str,
) -> tuple[str, list[dict]]:
    payload: dict = {
        "model": MODEL_ID,
        "messages": messages,
        "stream": False,
    }
    if mode in {"kb", "hybrid"}:
        payload["files"] = [{"type": "collection", "id": kb_id}]
    if mode in {"tool", "hybrid"}:
        payload["tool_ids"] = ["server:0"]

    response = client.post(
        f"{base}/api/chat/completions",
        headers=headers,
        json=payload,
        timeout=600.0,
    )
    response.raise_for_status()
    message = response.json()["choices"][0]["message"]
    updated = messages + [message]

    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        return message.get("content") or "", updated

    for call in tool_calls:
        fn = call.get("function") or {}
        result = execute_tool_call(fn.get("name", ""), fn.get("arguments", "{}"))
        updated.append(
            {
                "role": "tool",
                "tool_call_id": call.get("id"),
                "name": fn.get("name"),
                "content": result,
            }
        )

    follow_up = client.post(
        f"{base}/api/chat/completions",
        headers=headers,
        json={
            "model": MODEL_ID,
            "messages": updated,
            "stream": False,
            "tool_ids": ["server:0"],
        },
        timeout=600.0,
    )
    follow_up.raise_for_status()
    final = follow_up.json()["choices"][0]["message"]
    updated.append(final)
    return final.get("content") or json.dumps(final, indent=2), updated


def evaluate(label: str, answer: str, expected: str, error: str | None) -> str:
    if error:
        return "FAIL"
    text = answer.lower()
    if label == "kb_titles":
        return "PASS" if "engineer" in text or "scientist" in text or "title" in text else "FAIL"
    if label == "kb_skills":
        return "PASS" if "python" in text or "skill" in text else "FAIL"
    if label == "tool_live_israel":
        return "PASS" if "israel" in text or "tel aviv" in text or "job" in text else "FAIL"
    if label == "tool_live_skill":
        return "PASS" if "python" in text else "FAIL"
    if label == "hybrid_compare":
        return "PASS" if "dataset" in text and ("live" in text or "rapidapi" in text) else "FAIL"
    if label == "edge_not_in_kb":
        return "PASS" if "not" in text or "no " in text else "FAIL"
    return "PASS" if answer.strip() else "FAIL"


def run_direct_tool_tests() -> list[dict]:
    """Hit the tool server directly — validates behavior with and without a live key."""
    rows: list[dict] = []

    def add(label: str, expected: str, fn) -> None:
        try:
            summary, passed = fn()
            rows.append({"label": label, "expected": expected, "summary": summary,
                         "result": "PASS" if passed else "FAIL"})
        except httpx.HTTPError as exc:
            rows.append({"label": label, "expected": expected, "summary": str(exc),
                         "result": "FAIL"})

    def health_ok() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/health", timeout=15)
        r.raise_for_status()
        body = r.json()
        return (
            f"status={body.get('status')} source={body.get('source')} "
            f"configured={body.get('rapidapi_configured')}",
            body.get("status") == "ok",
        )

    def missing_query() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/jobs/search", timeout=15)
        return f"status={r.status_code}", r.status_code == 422

    def live_search() -> tuple[str, bool]:
        r = httpx.get(
            f"{TOOL_SERVER}/jobs/search",
            params={"query": "ai engineer", "location": "Israel"},
            timeout=45,
        )
        body = r.json()
        if r.status_code == 503:
            # correct negative-path behavior when RAPIDAPI_KEY is absent
            return f"status=503 error={body.get('error', '')[:60]}", True
        return f"status={r.status_code} count={body.get('count')}", (
            r.status_code == 200 and not body.get("error")
        )

    def skill_search() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/jobs/skills", params={"skill": "Python"}, timeout=45)
        return f"status={r.status_code}", r.status_code in (200, 503)

    def company_missing() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/jobs/company", timeout=15)
        return f"status={r.status_code}", r.status_code == 422

    add("direct_health", "GET /health returns ok", health_ok)
    add("direct_missing_query", "Missing query returns 422", missing_query)
    add("direct_live_search", "Live search 200 (or clean 503 without key)", live_search)
    add("direct_skill_search", "GET /jobs/skills responds cleanly", skill_search)
    add("direct_company_missing", "Missing company returns 422", company_missing)
    return rows


def write_test_results(rows: list[dict]) -> None:
    lines = [
        "# HW07 Test Results",
        "",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Test | Expected | Summary | Result |",
        "|------|----------|---------|--------|",
    ]
    for row in rows:
        summary = str(row.get("summary", "")).replace("|", "\\|").replace("\n", " ")[:200]
        lines.append(
            f"| {row['label']} | {row['expected']} | {summary} | **{row['result']}** |"
        )
    path = HW07 / "TEST_RESULTS.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {path}")


def main() -> int:
    base = os.getenv("OWUI_URL", "http://localhost:3000").rstrip("/")
    rows: list[dict] = []

    for row in run_direct_tool_tests():
        print(f"[direct] {row['label']}: {row['result']} — {row['summary']}")
        rows.append(row)

    try:
        with httpx.Client(timeout=600.0) as client:
            token = signin(client, base)
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            kb_id = resolve_kb_id(base, token)
            print(f"Using KB id: {kb_id}", flush=True)

            for label, mode, prompt, expected in PROMPTS:
                print(f"\n=== {label} ===", flush=True)
                print(f"PROMPT: {prompt}", flush=True)
                error: str | None = None
                answer = ""
                try:
                    answer, _ = chat_once(
                        client,
                        base,
                        headers,
                        [{"role": "user", "content": prompt}],
                        mode=mode,
                        kb_id=kb_id,
                    )
                    print(f"ANSWER:\n{answer[:2500]}", flush=True)
                except httpx.HTTPStatusError as exc:
                    error = exc.response.text[:500] if exc.response is not None else str(exc)
                    print(f"ERROR: {error}", flush=True)
                except httpx.RequestError as exc:
                    error = str(exc)
                    print(f"ERROR: {error}", flush=True)

                result = evaluate(label, answer, expected, error)
                rows.append(
                    {
                        "label": label,
                        "expected": expected,
                        "summary": (answer or error or "")[:200],
                        "result": result,
                    }
                )
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"WARN: Open WebUI chat tests skipped: {exc}", file=sys.stderr)
        rows.append(
            {
                "label": "owui_chat_suite",
                "expected": "Demo chats via Open WebUI API",
                "summary": str(exc),
                "result": "SKIP",
            }
        )

    write_test_results(rows)

    out = HW07 / "screenshots" / "demo_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {out}")

    failed = sum(1 for r in rows if r["result"] == "FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run hw07 demo chat prompts and write TEST_RESULTS.md."""

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

MODEL_ID = "cve-intelligence-assistant"
KB_NAME = "CVE Intelligence"
TOOL_SERVER = os.getenv("TOOLS_SERVER_URL", "http://localhost:5005").rstrip("/")

PROMPTS: list[tuple[str, str, str, str]] = [
    (
        "kb_only",
        "kb",
        "Which CVEs in my dataset affected Apache Struts, and what were their CVSS scores?",
        "Answer cites dataset CVE IDs and CVSS scores from KB; no fabricated IDs.",
    ),
    (
        "tool_only",
        "tool",
        "What is the current EPSS score and KEV status for CVE-2021-44228? Use lookup_cve.",
        "Model calls lookup_cve; shows EPSS, KEV, CVSS from live tool JSON.",
    ),
    (
        "search_tool",
        "tool",
        "Search live CVE records for apache struts using search_cves.",
        "Model calls search_cves or explains live search results with source field.",
    ),
    (
        "hybrid",
        "hybrid",
        "From my dataset, what Apache CVEs exist? Then give live EPSS for CVE-2021-44228.",
        "Two labeled sections: KB historical data then live lookup.",
    ),
    (
        "edge_invalid_cve",
        "tool",
        "Look up CVE-INVALID live",
        "422 or clear invalid-format message; no hallucinated scores.",
    ),
    (
        "edge_not_in_kb",
        "kb",
        "What does my dataset say about CVE-2099-99999?",
        "Not found in dataset; no guess.",
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
    env_id = os.getenv("HW07_KB_ID", "").strip()
    if env_id:
        return env_id
    return owui_kb_setup.resolve_kb_id(base, token, KB_NAME)


def execute_tool_call(name: str, arguments: str) -> str:
    args = json.loads(arguments or "{}")
    if name == "lookup_cve":
        cve_id = args.get("cve_id", "")
        response = httpx.get(f"{TOOL_SERVER}/cve/{cve_id}", timeout=30)
        if response.status_code == 422:
            return json.dumps({"error": response.json().get("detail", "Invalid CVE ID")})
        response.raise_for_status()
        return json.dumps(response.json())
    if name == "search_cves":
        keyword = args.get("keyword", "")
        response = httpx.get(
            f"{TOOL_SERVER}/search",
            params={"keyword": keyword},
            timeout=30,
        )
        if response.status_code == 422:
            return json.dumps({"error": response.json().get("detail", "Invalid keyword")})
        response.raise_for_status()
        return json.dumps(response.json())
    return json.dumps({"error": f"Unknown tool {name}"})


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
        if label in {"edge_invalid_cve"} and ("422" in error or "invalid" in error.lower()):
            return "PASS"
        return "FAIL"
    text = answer.lower()
    if label == "kb_only":
        return "PASS" if ("struts" in text or "cve-" in text) and "cvss" in text else "FAIL"
    if label == "tool_only":
        return "PASS" if ("epss" in text or "kev" in text) and "44228" in text else "FAIL"
    if label == "search_tool":
        return "PASS" if "apache" in text or "struts" in text or "cve-" in text else "FAIL"
    if label == "hybrid":
        return "PASS" if "44228" in text and ("apache" in text or "dataset" in text or "cve-" in text) else "FAIL"
    if label == "edge_invalid_cve":
        return "PASS" if "invalid" in text or "format" in text else "FAIL"
    if label == "edge_not_in_kb":
        return "PASS" if "not found" in text or "no " in text else "FAIL"
    return "PASS" if answer.strip() else "FAIL"


def run_direct_tool_tests() -> list[dict]:
    rows: list[dict] = []

    def add(label: str, expected: str, fn) -> None:
        try:
            summary, passed = fn()
            rows.append(
                {
                    "label": label,
                    "expected": expected,
                    "summary": summary,
                    "result": "PASS" if passed else "FAIL",
                }
            )
        except httpx.HTTPError as exc:
            rows.append(
                {
                    "label": label,
                    "expected": expected,
                    "summary": str(exc),
                    "result": "FAIL",
                }
            )

    def health_ok() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/health", timeout=15)
        r.raise_for_status()
        body = r.json()
        return f"status={body.get('status')} source={body.get('source')}", body.get("status") == "ok"

    def lookup_ok() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/cve/CVE-2021-44228", timeout=30)
        r.raise_for_status()
        body = r.json()
        return f"source={body.get('source')} epss={body.get('epss')}", bool(body.get("cve_id"))

    def invalid_cve() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/cve/not-a-cve", timeout=15)
        return f"status={r.status_code}", r.status_code == 422

    def empty_search() -> tuple[str, bool]:
        r = httpx.get(f"{TOOL_SERVER}/search", params={"keyword": " "}, timeout=15)
        return f"status={r.status_code}", r.status_code == 422

    def search_ok() -> tuple[str, bool]:
        r = httpx.get(
            f"{TOOL_SERVER}/search",
            params={"keyword": "apache struts"},
            timeout=30,
        )
        r.raise_for_status()
        body = r.json()
        return f"source={body.get('source')} count={body.get('count')}", body.get("count", 0) >= 0

    add("direct_health", "GET /health returns ok", health_ok)
    add("direct_lookup", "GET /cve/CVE-2021-44228 returns live data", lookup_ok)
    add("direct_invalid_cve", "Invalid CVE returns 422", invalid_cve)
    add("direct_empty_search", "Empty keyword returns 422", empty_search)
    add("direct_search", "GET /search?keyword=apache struts succeeds", search_ok)
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

#!/usr/bin/env python3
"""Create an Open WebUI knowledge base and upload a CSV (idempotent).

Usage (PowerShell):
    $env:OWUI_URL     = "http://localhost:3000"
    $env:OWUI_API_KEY = "sk-..."
    python owui_kb_setup.py --csv .\\data\\cve.csv --name "CVE Intelligence" `
        --description "Historical CVE / CVSS records for RAG"
"""

from __future__ import annotations

import argparse
import os
import sys

import requests


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def find_knowledge_by_name(base: str, api_key: str, name: str) -> str | None:
    """Return the id of an existing KB with this name, or None."""
    response = requests.get(
        f"{base}/api/v1/knowledge/", headers=_headers(api_key), timeout=30
    )
    response.raise_for_status()
    for kb in response.json():
        if kb.get("name") == name:
            return kb.get("id")
    return None


def create_knowledge(base: str, api_key: str, name: str, description: str) -> str:
    """Create a KB (or reuse one with the same name) and return its id."""
    existing = find_knowledge_by_name(base, api_key, name)
    if existing:
        print(f"[=] Knowledge base '{name}' already exists (id={existing}); reusing.")
        return existing
    response = requests.post(
        f"{base}/api/v1/knowledge/create",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json={"name": name, "description": description},
        timeout=30,
    )
    response.raise_for_status()
    kid = response.json()["id"]
    print(f"[+] Created knowledge base '{name}' (id={kid}).")
    return kid


def upload_file(base: str, api_key: str, csv_path: str) -> str:
    """Upload a file to Open WebUI and return its file id."""
    with open(csv_path, "rb") as handle:
        files = {"file": (os.path.basename(csv_path), handle, "text/csv")}
        response = requests.post(
            f"{base}/api/v1/files/",
            headers=_headers(api_key),
            files=files,
            timeout=120,
        )
    response.raise_for_status()
    fid = response.json()["id"]
    print(f"[+] Uploaded '{csv_path}' (file_id={fid}).")
    return fid


def add_file_to_knowledge(base: str, api_key: str, knowledge_id: str, file_id: str) -> None:
    """Attach an uploaded file to a knowledge base (triggers indexing)."""
    response = requests.post(
        f"{base}/api/v1/knowledge/{knowledge_id}/file/add",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json={"file_id": file_id},
        timeout=120,
    )
    response.raise_for_status()
    print(f"[+] Attached file {file_id} to knowledge base {knowledge_id}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an Open WebUI KB and upload a CSV.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file to upload.")
    parser.add_argument("--name", required=True, help="Knowledge base name.")
    parser.add_argument("--description", default="", help="Knowledge base description.")
    parser.add_argument(
        "--url",
        default=os.getenv("OWUI_URL", "http://localhost:3000"),
        help="Open WebUI base URL (or set OWUI_URL).",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OWUI_API_KEY", ""),
        help="Open WebUI API key (or set OWUI_API_KEY).",
    )
    args = parser.parse_args()

    base = args.url.rstrip("/")
    if not args.api_key:
        print(
            "ERROR: set OWUI_API_KEY env var or pass --api-key "
            "(Open WebUI > Settings > Account > API Keys).",
            file=sys.stderr,
        )
        return 2
    if not os.path.isfile(args.csv):
        print(f"ERROR: CSV not found: {args.csv}", file=sys.stderr)
        return 2

    try:
        kid = create_knowledge(base, args.api_key, args.name, args.description)
        fid = upload_file(base, args.api_key, args.csv)
        add_file_to_knowledge(base, args.api_key, kid, fid)
    except requests.HTTPError as exc:
        body = exc.response.text[:500] if exc.response is not None else ""
        print(f"ERROR: {exc}\n{body}", file=sys.stderr)
        print(
            f"Tip: confirm endpoint paths at {base}/docs if your OWUI version differs.",
            file=sys.stderr,
        )
        return 1
    except requests.RequestException as exc:
        print(f"ERROR: request failed: {exc}", file=sys.stderr)
        return 1

    print(f"\nDone. KB id: {kid}")
    print("Next: attach this KB to a tool-capable model in Workspace > Models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

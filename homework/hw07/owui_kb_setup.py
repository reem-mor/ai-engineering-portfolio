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
import time

import requests

from env_loader import load_hw07_env

load_hw07_env()


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _knowledge_items(payload: list | dict) -> list[dict]:
    """Normalize OWUI knowledge list responses (flat list or paginated)."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return items
    return []


def find_knowledge_by_name(base: str, api_key: str, name: str) -> str | None:
    """Return the id of an existing KB with this name, or None."""
    response = requests.get(
        f"{base}/api/v1/knowledge/", headers=_headers(api_key), timeout=30
    )
    response.raise_for_status()
    for kb in _knowledge_items(response.json()):
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


def upload_file(base: str, api_key: str, csv_path: str, knowledge_id: str | None = None) -> str:
    """Upload a file to Open WebUI and return its file id.

    When knowledge_id is set, OWUI auto-links and indexes into that KB (recommended).
    Uses text/plain for CSV to avoid empty-content extraction failures.
    """
    with open(csv_path, "rb") as handle:
        files = {"file": (os.path.basename(csv_path), handle, "text/plain")}
        data: dict[str, str] = {}
        if knowledge_id:
            data["knowledge_id"] = knowledge_id
        response = requests.post(
            f"{base}/api/v1/files/",
            headers=_headers(api_key),
            files=files,
            data=data or None,
            timeout=600,
        )
    response.raise_for_status()
    fid = response.json()["id"]
    print(f"[+] Uploaded '{csv_path}' (file_id={fid}).")
    return fid


def get_file(base: str, token: str, file_id: str) -> dict:
    response = requests.get(
        f"{base}/api/v1/files/{file_id}",
        headers=_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def wait_for_file_processed(
    base: str,
    token: str,
    file_id: str,
    *,
    timeout: int = 600,
    poll_interval: int = 5,
) -> str:
    """Poll until file processing completes; return final status."""
    deadline = time.time() + timeout
    last_status = "pending"
    while time.time() < deadline:
        status_resp = requests.get(
            f"{base}/api/v1/files/{file_id}/process/status",
            headers=_headers(token),
            timeout=30,
        )
        if status_resp.status_code == 200:
            last_status = status_resp.json().get("status", last_status)
        else:
            file_data = get_file(base, token, file_id)
            last_status = (file_data.get("data") or {}).get("status", last_status)
        print(f"[~] file {file_id}: status={last_status}")
        if last_status in {"completed", "failed"}:
            if last_status == "failed":
                raise RuntimeError(f"File processing failed for {file_id}.")
            return last_status
        time.sleep(poll_interval)
    raise TimeoutError(f"File {file_id} not processed within {timeout}s (last={last_status}).")


def add_file_to_knowledge(base: str, api_key: str, knowledge_id: str, file_id: str) -> None:
    """Attach an uploaded file to a knowledge base (triggers indexing)."""
    response = requests.post(
        f"{base}/api/v1/knowledge/{knowledge_id}/file/add",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json={"file_id": file_id},
        timeout=600,
    )
    response.raise_for_status()
    print(f"[+] Attached file {file_id} to knowledge base {knowledge_id}.")


def list_kb_files(base: str, token: str, knowledge_id: str) -> list[dict]:
    """Return files attached to a knowledge base."""
    response = requests.get(
        f"{base}/api/v1/knowledge/{knowledge_id}/files",
        headers=_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return payload
    return payload.get("items") or []


def get_knowledge(base: str, token: str, knowledge_id: str) -> dict:
    """Return a single knowledge base record."""
    response = requests.get(
        f"{base}/api/v1/knowledge/{knowledge_id}",
        headers=_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def resolve_kb_id(base: str, token: str, name: str = "CVE Intelligence") -> str:
    """Return KB id by name or raise if missing."""
    kid = find_knowledge_by_name(base, token, name)
    if not kid:
        raise RuntimeError(f"Knowledge base '{name}' not found — run bootstrap first.")
    return kid


def wait_for_kb_files(
    base: str,
    token: str,
    knowledge_id: str,
    *,
    min_files: int = 1,
    timeout: int = 300,
    poll_interval: int = 5,
) -> int:
    """Poll until the KB has at least min_files attached; return file count."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        files = list_kb_files(base, token, knowledge_id)
        count = len(files)
        print(f"[~] KB {knowledge_id}: {count} file(s) attached.")
        if count >= min_files:
            print(f"[+] KB ready ({count} file(s)).")
            return count
        time.sleep(poll_interval)
    raise TimeoutError(
        f"KB {knowledge_id} did not reach {min_files} file(s) within {timeout}s."
    )


def signin_token(base: str, email: str, password: str) -> str:
    """Obtain a JWT from Open WebUI sign-in."""
    response = requests.post(
        f"{base}/api/v1/auths/signin",
        json={"email": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("token", "").strip()
    if not token:
        raise RuntimeError("Sign-in succeeded but no JWT token returned.")
    return token


def resolve_auth_token(base: str, api_key: str = "") -> str:
    """Use API key if valid; otherwise sign in with OWUI_EMAIL/PASSWORD."""
    key = api_key.strip()
    if key:
        probe = requests.get(
            f"{base}/api/v1/knowledge/",
            headers=_headers(key),
            timeout=15,
        )
        if probe.status_code == 401:
            print("[~] OWUI_API_KEY invalid; falling back to JWT sign-in.")
        else:
            probe.raise_for_status()
            return key
    email = os.getenv("OWUI_EMAIL", "").strip()
    password = os.getenv("OWUI_PASSWORD", "")
    if not email or not password:
        raise RuntimeError(
            "Set OWUI_API_KEY or both OWUI_EMAIL and OWUI_PASSWORD."
        )
    return signin_token(base, email, password)


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
    if not os.path.isfile(args.csv):
        print(f"ERROR: CSV not found: {args.csv}", file=sys.stderr)
        return 2

    try:
        token = resolve_auth_token(base, args.api_key)
        auth_mode = "api_key" if args.api_key.strip() else "jwt"
        print(f"[+] Authenticated via {auth_mode}")
        kid = create_knowledge(base, token, args.name, args.description)
        print(f"[+] Uploading {args.csv} to KB {kid} ...")
        fid = upload_file(base, token, args.csv, knowledge_id=kid)
        print(f"[+] File uploaded (file_id={fid}); waiting for processing ...")
        status = wait_for_file_processed(base, token, fid)
        print(f"[+] File processing status: {status}")
        files = list_kb_files(base, token, kid)
        if not files:
            add_file_to_knowledge(base, token, kid, fid)
        file_count = wait_for_kb_files(base, token, kid)
        print(f"[+] KB ready with {file_count} file(s)")
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
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

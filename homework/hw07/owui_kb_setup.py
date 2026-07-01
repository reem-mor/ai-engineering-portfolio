#!/usr/bin/env python3
"""Create/update the hw07 Open WebUI knowledge base and upload the AI jobs CSV.

Idempotent: reuses an existing KB by name and replaces a same-named file
instead of duplicating it. Polls file processing status after upload.

Auth (from repo root .env — canonical): OWUI_API_KEY (probed, with JWT
fallback), or OWUI_EMAIL + OWUI_PASSWORD via /api/v1/auths/signin.
Secrets are never printed.

Usage:
    python owui_kb_setup.py                       # defaults: data/ai_jobs.csv
    python owui_kb_setup.py --write-env           # also sync KB/file IDs to root .env
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

from env_loader import load_hw07_env

load_hw07_env()

HW07_ROOT = Path(__file__).resolve().parent
REPO_ROOT = HW07_ROOT.parent.parent

KB_NAME = "AI Job Market Intelligence Dataset"
KB_DESCRIPTION = (
    "Kaggle AI job-market dataset (titles, salaries, skills, locations, "
    "experience levels) for RAG — static/historical questions."
)
DEFAULT_CSV = HW07_ROOT / "data" / "ai_jobs.csv"
POLL_INTERVAL_S = 3
POLL_TIMEOUT_S = 600


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def sign_in(base: str, email: str, password: str) -> str:
    """Sign in with email/password and return a bearer token."""
    response = requests.post(
        f"{base}/api/v1/auths/signin",
        json={"email": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("token", "")
    if not token:
        raise RuntimeError("Sign-in succeeded but Open WebUI returned no token.")
    return token


def get_token(base: str) -> str:
    """Resolve an auth token: probe OWUI_API_KEY first, else OWUI_EMAIL/OWUI_PASSWORD."""
    email = os.getenv("OWUI_EMAIL", "").strip()
    password = os.getenv("OWUI_PASSWORD", "").strip()

    api_key = os.getenv("OWUI_API_KEY", "").strip()
    if api_key:
        probe = requests.get(f"{base}/api/v1/knowledge/", headers=_headers(api_key), timeout=15)
        if probe.status_code != 401:
            probe.raise_for_status()
            print("[auth] using OWUI_API_KEY")
            return api_key
        print("[auth] OWUI_API_KEY rejected (401); falling back to JWT sign-in.")

    if email and password:
        token = sign_in(base, email, password)
        print(f"[auth] signed in as {email} — OK")
        return token
    raise RuntimeError(
        "No Open WebUI credentials: set OWUI_API_KEY, or OWUI_EMAIL + OWUI_PASSWORD, "
        "in the repo root .env."
    )


def _knowledge_items(payload: list | dict) -> list[dict]:
    """Normalize OWUI knowledge list responses (flat list or paginated {items})."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return items
    return []


def find_knowledge_by_name(base: str, token: str, name: str) -> str | None:
    """Return the id of an existing KB with this name, or None."""
    response = requests.get(f"{base}/api/v1/knowledge/", headers=_headers(token), timeout=30)
    response.raise_for_status()
    for kb in _knowledge_items(response.json()):
        if kb.get("name") == name:
            return kb.get("id")
    return None


def create_knowledge(base: str, token: str, name: str, description: str) -> str:
    """Create a KB (or reuse one with the same name) and return its id."""
    existing = find_knowledge_by_name(base, token, name)
    if existing:
        print(f"[kb] '{name}' already exists (id={existing}); reusing.")
        return existing
    response = requests.post(
        f"{base}/api/v1/knowledge/create",
        headers={**_headers(token), "Content-Type": "application/json"},
        json={"name": name, "description": description},
        timeout=30,
    )
    response.raise_for_status()
    kid = response.json()["id"]
    print(f"[kb] created '{name}' (id={kid}).")
    return kid


def get_knowledge_files(base: str, token: str, knowledge_id: str) -> list[dict]:
    """Return the files currently attached to a KB."""
    response = requests.get(
        f"{base}/api/v1/knowledge/{knowledge_id}", headers=_headers(token), timeout=30
    )
    response.raise_for_status()
    return response.json().get("files") or []


def upload_file(base: str, token: str, csv_path: Path, knowledge_id: str | None = None) -> str:
    """Upload a file to Open WebUI and return its file id.

    When knowledge_id is set, OWUI auto-links and indexes into that KB.
    Uses text/plain for CSV to avoid empty-content extraction failures.
    """
    with csv_path.open("rb") as handle:
        files = {"file": (csv_path.name, handle, "text/plain")}
        data = {"knowledge_id": knowledge_id} if knowledge_id else None
        response = requests.post(
            f"{base}/api/v1/files/",
            headers=_headers(token),
            files=files,
            data=data,
            timeout=600,
        )
    response.raise_for_status()
    fid = response.json()["id"]
    print(f"[upload] '{csv_path.name}' uploaded — OK (file_id={fid})")
    return fid


def wait_for_file_processed(base: str, token: str, file_id: str) -> str:
    """Poll the uploaded file until Open WebUI finishes extracting/processing it."""
    deadline = time.monotonic() + POLL_TIMEOUT_S
    last_status = "unknown"
    while time.monotonic() < deadline:
        response = requests.get(
            f"{base}/api/v1/files/{file_id}", headers=_headers(token), timeout=30
        )
        response.raise_for_status()
        payload = response.json()
        last_status = (payload.get("data") or {}).get("status") or payload.get("status") or ""
        content = (payload.get("data") or {}).get("content")
        if last_status in ("completed", "processed") or content:
            print(f"[processing] file {file_id}: {last_status or 'content extracted'} — OK")
            return last_status or "completed"
        if last_status in ("failed", "error"):
            raise RuntimeError(f"Open WebUI failed to process file {file_id}.")
        print(f"[processing] file {file_id}: {last_status or 'pending'} ... waiting")
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(
        f"File {file_id} not processed within {POLL_TIMEOUT_S}s (last status: {last_status})."
    )


def remove_file_from_knowledge(base: str, token: str, knowledge_id: str, file_id: str) -> None:
    response = requests.post(
        f"{base}/api/v1/knowledge/{knowledge_id}/file/remove",
        headers={**_headers(token), "Content-Type": "application/json"},
        json={"file_id": file_id},
        timeout=120,
    )
    response.raise_for_status()
    print(f"[kb] removed stale file {file_id} from KB {knowledge_id}.")


def add_file_to_knowledge(base: str, token: str, knowledge_id: str, file_id: str) -> None:
    """Attach an uploaded file to a knowledge base (triggers indexing)."""
    response = requests.post(
        f"{base}/api/v1/knowledge/{knowledge_id}/file/add",
        headers={**_headers(token), "Content-Type": "application/json"},
        json={"file_id": file_id},
        timeout=600,
    )
    response.raise_for_status()
    print(f"[kb] attached file {file_id} to KB {knowledge_id} — indexing triggered.")


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
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        count = len(get_knowledge_files(base, token, knowledge_id))
        print(f"[kb] {knowledge_id}: {count} file(s) attached.")
        if count >= min_files:
            return count
        time.sleep(poll_interval)
    raise TimeoutError(
        f"KB {knowledge_id} did not reach {min_files} file(s) within {timeout}s."
    )


def resolve_kb_id(base: str, token: str, name: str = KB_NAME) -> str:
    """Return KB id by name or raise if missing (used by demo/screenshot scripts)."""
    kid = find_knowledge_by_name(base, token, name)
    if not kid:
        raise RuntimeError(f"Knowledge base '{name}' not found — run owui_kb_setup.py first.")
    return kid


def upsert_env(path: Path, updates: dict[str, str]) -> None:
    """Update or append KEY=VALUE lines in an env file without touching others."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in updates and not line.lstrip().startswith("#"):
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    out.extend(f"{key}={value}" for key, value in updates.items() if key not in seen)
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="CSV to upload.")
    parser.add_argument("--name", default=KB_NAME, help="Knowledge base name.")
    parser.add_argument("--description", default=KB_DESCRIPTION)
    parser.add_argument("--url", default=os.getenv("OWUI_URL", "http://localhost:3000"))
    parser.add_argument(
        "--replace", action="store_true",
        help="Replace an already-attached file with the same name.",
    )
    parser.add_argument(
        "--write-env", action="store_true",
        help="Write OWUI_KNOWLEDGE_ID / OWUI_FILE_ID into the repo root .env.",
    )
    args = parser.parse_args()

    base = args.url.rstrip("/")
    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(
            f"ERROR: CSV not found: {csv_path}. "
            "Run data/download_dataset.py then data/validate_dataset.py first.",
            file=sys.stderr,
        )
        return 2

    try:
        token = get_token(base)
        kid = create_knowledge(base, token, args.name, args.description)

        existing_files = get_knowledge_files(base, token, kid)
        same_name = [
            f for f in existing_files
            if (f.get("meta") or {}).get("name") == csv_path.name
            or (f.get("filename") == csv_path.name)
        ]
        if same_name and not args.replace:
            fid = same_name[0]["id"]
            print(
                f"[kb] '{csv_path.name}' already attached (file_id={fid}); "
                "use --replace to re-upload."
            )
        else:
            for stale in same_name:
                remove_file_from_knowledge(base, token, kid, stale["id"])
            fid = upload_file(base, token, csv_path, knowledge_id=kid)
            wait_for_file_processed(base, token, fid)
            if not any(f.get("id") == fid for f in get_knowledge_files(base, token, kid)):
                # knowledge_id auto-link not supported on this OWUI version — attach explicitly
                add_file_to_knowledge(base, token, kid, fid)

        files = get_knowledge_files(base, token, kid)
        print(f"[kb] verification: KB id={kid}, file count={len(files)}")
        if not any(f.get("id") == fid for f in files):
            print("ERROR: uploaded file is not attached to the KB.", file=sys.stderr)
            return 1
    except requests.HTTPError as exc:
        body = exc.response.text[:300] if exc.response is not None else ""
        print(f"ERROR: Open WebUI API error: {exc}\n{body}", file=sys.stderr)
        print(f"Tip: confirm endpoint paths at {base}/docs if your OWUI version differs.",
              file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"ERROR: cannot reach Open WebUI at {base}: {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.write_env:
        upsert_env(REPO_ROOT / ".env", {"OWUI_KNOWLEDGE_ID": kid, "OWUI_FILE_ID": fid})
        print("[env] OWUI_KNOWLEDGE_ID / OWUI_FILE_ID synced to repo root .env")

    print(f"\nDone. KB '{args.name}' ready (id={kid}, file_id={fid}).")
    print("Next: attach this KB to a tool-capable model in Workspace > Models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

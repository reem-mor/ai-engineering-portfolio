#!/usr/bin/env python3
"""Create Open WebUI API key via REST and sync hw07 vars into repo .env (no secret output)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from env_loader import HW07_ROOT, REPO_ROOT, load_hw07_env  # noqa: E402

ENV_FILES = (REPO_ROOT / ".env", HW07_ROOT / ".env")


def _upsert_env(path: Path, updates: dict[str, str]) -> None:
    lines: list[str] = []
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            out.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in updates:
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def create_owui_api_key(
    base_url: str,
    email: str,
    password: str,
) -> str:
    base = base_url.rstrip("/")
    with httpx.Client(timeout=30.0) as client:
        signin = client.post(
            f"{base}/api/v1/auths/signin",
            json={"email": email, "password": password},
        )
        signin.raise_for_status()
        token = signin.json().get("token")
        if not token:
            raise RuntimeError("Sign-in succeeded but no JWT token returned.")

        headers = {"Authorization": f"Bearer {token}"}
        created = client.post(f"{base}/api/v1/auths/api_key", headers=headers)
        created.raise_for_status()
        api_key = created.json().get("api_key", "").strip()
        if not api_key:
            raise RuntimeError("API key creation returned empty value.")
        return api_key


def main() -> int:
    load_hw07_env()

    parser = argparse.ArgumentParser(description="Sync OWUI API key into repo root .env.")
    parser.add_argument("--url", default=os.getenv("OWUI_URL", "http://localhost:3000"))
    parser.add_argument("--email", default=os.getenv("OWUI_EMAIL", "admin@localhost.com"))
    parser.add_argument("--password", default=os.getenv("OWUI_PASSWORD", "admin"))
    parser.add_argument("--skip-owui", action="store_true", help="Only sync existing env vars.")
    args = parser.parse_args()

    updates: dict[str, str] = {
        "OWUI_URL": args.url.rstrip("/"),
    }

    existing_key = os.getenv("RAPIDAPI_KEY", "").strip()
    existing_cve_host = os.getenv("RAPIDAPI_CVE_HOST", "").strip()
    if existing_key:
        updates["RAPIDAPI_KEY"] = existing_key
    if existing_cve_host:
        updates["RAPIDAPI_CVE_HOST"] = existing_cve_host

    if not args.skip_owui:
        try:
            api_key = create_owui_api_key(args.url, args.email, args.password)
            updates["OWUI_API_KEY"] = api_key
        except httpx.HTTPError as exc:
            print(
                f"WARN: Open WebUI API key creation failed ({exc}). "
                "JWT sign-in still works for bootstrap scripts.",
                file=sys.stderr,
            )
        except RuntimeError as exc:
            print(f"WARN: {exc}", file=sys.stderr)

    owui_key = updates.get("OWUI_API_KEY") or os.getenv("OWUI_API_KEY", "").strip()
    if not owui_key and not args.skip_owui:
        print("WARN: OWUI_API_KEY not refreshed — use JWT (OWUI_EMAIL/PASSWORD) for scripts.")

    _upsert_env(REPO_ROOT / ".env", updates)
    local_only = {k: v for k, v in updates.items() if k == "HW07_KB_ID"}
    if local_only:
        _upsert_env(HW07_ROOT / ".env", local_only)

    print(f"OK: synced hw07 env vars to {REPO_ROOT / '.env'}")
    print(f"  OWUI_URL={updates['OWUI_URL']}")
    print(f"  OWUI_API_KEY={'set' if owui_key else 'unchanged'}")
    print(f"  RAPIDAPI_KEY={'set' if existing_key else 'missing'}")
    print(f"  RAPIDAPI_CVE_HOST={existing_cve_host or '(empty — tools_server uses CVEDB fallback)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

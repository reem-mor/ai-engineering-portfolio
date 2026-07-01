#!/usr/bin/env python3
"""Bootstrap hw07 OWUI: KB upload, tool-server registration, custom model (JWT auth)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

HW07 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07))
sys.path.insert(0, str(HW07 / "scripts"))

import owui_kb_setup  # noqa: E402
from env_loader import REPO_ROOT, load_hw07_env  # noqa: E402
from sync_env_from_services import _upsert_env  # noqa: E402

load_hw07_env()

KB_NAME = owui_kb_setup.KB_NAME
# From dockerized OWUI: tool server runs as compose service `tool-server`.
# Override with HW07_TOOL_URL=http://host.docker.internal:5005/openapi.json
# when running the tool server on the host instead.
TOOL_URL = os.getenv("HW07_TOOL_URL", "http://tool-server:5005/openapi.json")
MODEL_ID = os.getenv("HW07_MODEL_ID", "ai-job-market-assistant")


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


def main() -> int:
    base = os.getenv("OWUI_URL", "http://localhost:3000").rstrip("/")
    csv_path = HW07 / "data" / "ai_jobs.csv"
    prompt = (HW07 / "prompts" / "system_prompt.md").read_text(encoding="utf-8")

    if not csv_path.is_file():
        print(
            f"ERROR: {csv_path} missing — run data/download_dataset.py and "
            "data/validate_dataset.py first.",
            file=sys.stderr,
        )
        return 2

    with httpx.Client(timeout=120.0) as client:
        token = signin(client, base)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        kid = owui_kb_setup.create_knowledge(
            base, token, KB_NAME, owui_kb_setup.KB_DESCRIPTION
        )
        fid = owui_kb_setup.upload_file(base, token, csv_path, knowledge_id=kid)
        owui_kb_setup.wait_for_file_processed(base, token, fid)
        if not owui_kb_setup.get_knowledge_files(base, token, kid):
            owui_kb_setup.add_file_to_knowledge(base, token, kid, fid)
        owui_kb_setup.wait_for_kb_files(base, token, kid)
        print(f"KB id: {kid} (CSV attached file_id={fid})")

        _upsert_env(REPO_ROOT / ".env", {"OWUI_KNOWLEDGE_ID": kid, "OWUI_FILE_ID": fid})
        print("OWUI_KNOWLEDGE_ID / OWUI_FILE_ID saved to repo root .env")

        openapi = client.get("http://localhost:5005/openapi.json").json()
        conn = {
            "url": TOOL_URL,
            "path": "",
            "key": "",
            "auth_type": "none",
            "config": {"enable": True},
            "info": {
                "title": openapi.get("info", {}).get("title", "AI Job Market Tool"),
                "version": openapi.get("info", {}).get("version", "2.0.0"),
            },
        }
        client.post(
            f"{base}/api/v1/configs/tool_servers",
            headers=headers,
            json={"TOOL_SERVER_CONNECTIONS": [conn]},
        ).raise_for_status()
        print("tool_servers registered")

        model = {
            "id": MODEL_ID,
            "base_model_id": os.getenv("OWUI_BASE_MODEL", "llama3.1:latest"),
            "name": "AI Job Market Intelligence Assistant",
            "meta": {
                "profile_image_url": "/static/favicon.png",
                "description": "HW07 AI jobs KB + live job-search tool",
                "toolIds": ["server:0"],
                "knowledge": [kid],
                "system": prompt,
            },
            "params": {"function_calling": "native"},
            "is_active": True,
        }
        r = client.post(f"{base}/api/v1/models/create", headers=headers, json=model)
        if r.status_code != 200:
            client.post(
                f"{base}/api/v1/models/model/delete",
                headers=headers,
                json={"id": MODEL_ID},
            )
            client.post(
                f"{base}/api/v1/models/create", headers=headers, json=model
            ).raise_for_status()
        print(f"model {MODEL_ID} ready")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

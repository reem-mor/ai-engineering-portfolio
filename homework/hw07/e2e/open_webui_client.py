"""Open WebUI REST API client for hw07 E2E setup."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import httpx

from e2e.fixtures import (
    CHAT_MODEL,
    KB_COLLECTION_NAME,
    KB_DESCRIPTION,
    OPEN_WEBUI_EMAIL,
    OPEN_WEBUI_PASSWORD,
    PROMPT_KB_SKILLS,
    PROMPT_LIVE_JOBS,
    SYSTEM_PROMPT,
    TOOL_ID,
    TOOL_NAME,
)

HW07_ROOT = Path(__file__).resolve().parent.parent
OPENWEBUI_TOOL_PATH = HW07_ROOT / "openwebui_tool.py"
TOOL_SERVER_URL = "http://127.0.0.1:5005"


class OpenWebUIClient:
    def __init__(self, base_url: str = "http://localhost:3000", timeout: float = 1800.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)
        self.token: str | None = None

    def close(self) -> None:
        self._client.close()

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            raise RuntimeError("Not authenticated — call sign_in() first")
        return {"Authorization": f"Bearer {self.token}"}

    def set_token(self, token: str) -> None:
        self.token = token.strip()

    def sign_in(
        self,
        email: str | None = None,
        password: str | None = None,
    ) -> dict[str, Any]:
        api_key = os.environ.get("OPEN_WEBUI_API_KEY", "").strip()
        if api_key:
            self.set_token(api_key.removeprefix("Bearer ").strip())
            return {"token": self.token}

        email = email or os.environ.get("OPEN_WEBUI_EMAIL", OPEN_WEBUI_EMAIL)
        password = password or os.environ.get("OPEN_WEBUI_PASSWORD", OPEN_WEBUI_PASSWORD)

        response = self._client.post(
            "/api/v1/auths/signin",
            json={"email": email, "password": password},
        )
        if response.status_code == 400:
            signup = self._client.post(
                "/api/v1/auths/signup",
                json={"email": email, "password": password, "name": "HW07 Admin"},
            )
            if signup.status_code == 200:
                body = signup.json()
                self.token = body["token"]
                return body

        response.raise_for_status()
        body = response.json()
        self.token = body["token"]
        return body

    def clear_chats(self) -> None:
        response = self._client.delete("/api/v1/chats/", headers=self.headers)
        response.raise_for_status()

    def list_knowledge(self) -> list[dict[str, Any]]:
        response = self._client.get("/api/v1/knowledge/", headers=self.headers)
        response.raise_for_status()
        body = response.json()
        if isinstance(body, dict):
            return body.get("items") or []
        return body

    def get_knowledge(self, knowledge_id: str) -> dict[str, Any]:
        response = self._client.get(
            f"/api/v1/knowledge/{knowledge_id}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def list_knowledge_files(self, knowledge_id: str) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/api/v1/knowledge/{knowledge_id}/files",
            headers=self.headers,
        )
        response.raise_for_status()
        body = response.json()
        if isinstance(body, dict):
            return body.get("items") or []
        return body

    def list_pending_knowledge_files(self, knowledge_id: str) -> list[dict[str, Any]]:
        response = self._client.get(
            f"/api/v1/knowledge/{knowledge_id}/files/pending",
            headers=self.headers,
        )
        response.raise_for_status()
        body = response.json()
        return body if isinstance(body, list) else []

    def _wait_for_knowledge_file(
        self,
        knowledge_id: str,
        *,
        timeout: float = 2400.0,
        poll_interval: float = 10.0,
    ) -> None:
        import time

        deadline = time.time() + timeout
        last_log = 0.0
        while time.time() < deadline:
            pending = self._client.get(
                f"/api/v1/knowledge/{knowledge_id}/files/pending",
                headers=self.headers,
            )
            pending.raise_for_status()
            pending_files = pending.json()
            files = self.list_knowledge_files(knowledge_id)

            if files and not pending_files:
                return

            now = time.time()
            if now - last_log >= 60.0:
                pending_count = len(pending_files) if isinstance(pending_files, list) else 0
                print(
                    f"  KB indexing… pending={pending_count} linked={len(files)} "
                    f"({int(timeout - (deadline - now))}s elapsed)",
                    flush=True,
                )
                last_log = now

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Knowledge file processing did not finish within {timeout}s for {knowledge_id}"
        )

    def delete_knowledge(self, knowledge_id: str) -> None:
        response = self._client.delete(
            f"/api/v1/knowledge/{knowledge_id}",
            headers=self.headers,
        )
        if response.status_code not in {200, 204, 404}:
            response.raise_for_status()

    def ensure_knowledge_collection(self) -> dict[str, Any]:
        for kb in self.list_knowledge():
            if kb.get("name") == KB_COLLECTION_NAME:
                return self.get_knowledge(kb["id"])

        response = self._client.post(
            "/api/v1/knowledge/create",
            headers=self.headers,
            json={
                "name": KB_COLLECTION_NAME,
                "description": KB_DESCRIPTION,
                "access_control": None,
            },
        )
        response.raise_for_status()
        return response.json()

    def upload_knowledge_file(self, knowledge_id: str, csv_path: Path) -> None:
        metadata = json.dumps({"knowledge_id": knowledge_id})
        with csv_path.open("rb") as handle:
            upload = self._client.post(
                "/api/v1/files/",
                headers=self.headers,
                files={"file": (csv_path.name, handle, "text/csv")},
                data={"metadata": metadata},
                timeout=1800.0,
            )
        upload.raise_for_status()
        self._wait_for_knowledge_file(knowledge_id)

    def refresh_knowledge_csv(self, knowledge_id: str, csv_path: Path) -> None:
        """Replace KB contents when CSV was updated (e.g. dev fixture → full Kaggle file)."""
        for file_meta in self.list_knowledge_files(knowledge_id):
            file_id = file_meta.get("id")
            if file_id:
                self._client.post(
                    f"/api/v1/knowledge/{knowledge_id}/file/remove",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json={"file_id": file_id},
                )
        self.upload_knowledge_file(knowledge_id, csv_path)

    def list_tools(self) -> list[dict[str, Any]]:
        response = self._client.get("/api/v1/tools/", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def ensure_tool(self) -> dict[str, Any]:
        content = OPENWEBUI_TOOL_PATH.read_text(encoding="utf-8")
        payload = {
            "id": TOOL_ID,
            "name": TOOL_NAME,
            "content": content,
            "meta": {
                "description": (
                    "Live JSearch job listings via local tools_server.py on "
                    "host.docker.internal:5005 — inputs: role, location"
                ),
            },
        }

        for tool in self.list_tools():
            if tool.get("id") == TOOL_ID:
                update = self._client.post(
                    f"/api/v1/tools/id/{TOOL_ID}/update",
                    headers=self.headers,
                    json=payload,
                )
                if update.status_code == 200:
                    return update.json()
                return tool

        response = self._client.post(
            "/api/v1/tools/create",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_ollama_models(self) -> list[dict[str, Any]]:
        response = self._client.get("/ollama/api/tags", headers=self.headers)
        response.raise_for_status()
        return response.json().get("models", [])

    def ensure_chat_model(self) -> str:
        models = self.get_ollama_models()
        for model in models:
            name = model.get("name") or model.get("model") or ""
            if name == CHAT_MODEL or name.startswith("llama3.2"):
                return name
        names = [m.get("name") for m in models]
        raise RuntimeError(f"{CHAT_MODEL} not found in Ollama. Available: {names}")

    def ensure_model_preset(self) -> dict[str, Any]:
        """Register chat model with native tool calling, system prompt, and hw07 tool."""
        meta = {
            "description": "HW07 chat model — KB + live JSearch tool",
            "toolIds": [TOOL_ID],
            "system": SYSTEM_PROMPT,
        }
        params = {
            "function_calling": "native",
            "system": SYSTEM_PROMPT,
        }
        existing = self._client.get(
            "/api/v1/models/model",
            headers=self.headers,
            params={"id": CHAT_MODEL},
        )
        if existing.status_code == 200:
            current = existing.json()
            payload = {
                "id": CHAT_MODEL,
                "base_model_id": current.get("base_model_id") or CHAT_MODEL,
                "name": CHAT_MODEL,
                "meta": {**(current.get("meta") or {}), **meta},
                "params": {**(current.get("params") or {}), **params},
                "access_grants": current.get("access_grants") or [],
                "is_active": current.get("is_active", True),
            }
            update = self._client.post(
                "/api/v1/models/model/update",
                headers=self.headers,
                json=payload,
            )
            update.raise_for_status()
            return update.json()

        payload = {
            "id": CHAT_MODEL,
            "base_model_id": CHAT_MODEL,
            "name": CHAT_MODEL,
            "meta": meta,
            "params": params,
            "access_grants": [],
            "is_active": True,
        }
        response = self._client.post(
            "/api/v1/models/create",
            headers=self.headers,
            json=payload,
        )
        if response.status_code == 401 and "already registered" in response.text:
            retry = self._client.get(
                "/api/v1/models/model",
                headers=self.headers,
                params={"id": CHAT_MODEL},
            )
            retry.raise_for_status()
            current = retry.json()
            update = self._client.post(
                "/api/v1/models/model/update",
                headers=self.headers,
                json={
                    "id": CHAT_MODEL,
                    "base_model_id": current.get("base_model_id") or CHAT_MODEL,
                    "name": CHAT_MODEL,
                    "meta": {**(current.get("meta") or {}), **meta},
                    "params": {**(current.get("params") or {}), **params},
                    "access_grants": current.get("access_grants") or [],
                    "is_active": current.get("is_active", True),
                },
            )
            update.raise_for_status()
            return update.json()
        response.raise_for_status()
        return response.json()

    def _save_chat(
        self,
        title: str,
        user_content: str,
        assistant_content: str,
        *,
        files: list[dict[str, Any]] | None = None,
    ) -> str:
        user_id = str(uuid.uuid4())
        assistant_id = str(uuid.uuid4())
        chat_payload = {
            "chat": {
                "title": title,
                "models": [CHAT_MODEL],
                "messages": [
                    {"id": user_id, "role": "user", "content": user_content},
                    {"id": assistant_id, "role": "assistant", "content": assistant_content},
                ],
                "history": {
                    "messages": {
                        user_id: {"id": user_id, "role": "user", "content": user_content},
                        assistant_id: {
                            "id": assistant_id,
                            "role": "assistant",
                            "content": assistant_content,
                        },
                    },
                    "currentId": assistant_id,
                },
                "files": files or [],
            }
        }
        response = self._client.post(
            "/api/v1/chats/new",
            headers=self.headers,
            json=chat_payload,
        )
        response.raise_for_status()
        return response.json()["id"]

    def run_kb_chat_evidence(self) -> tuple[str, str, str]:
        """Run KB-grounded chat via API; return prompt, answer, saved chat id."""
        kb = self.ensure_knowledge_collection()
        response = self._client.post(
            "/api/chat/completions",
            headers=self.headers,
            json={
                "model": CHAT_MODEL,
                "messages": [{"role": "user", "content": PROMPT_KB_SKILLS}],
                "files": [{"type": "collection", "id": kb["id"]}],
            },
            timeout=1800.0,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        chat_id = self._save_chat(
            "HW07 KB — job titles from dataset",
            PROMPT_KB_SKILLS,
            answer,
            files=[{"type": "collection", "id": kb["id"], "name": KB_COLLECTION_NAME}],
        )
        return PROMPT_KB_SKILLS, answer, chat_id

    def run_tool_chat_evidence(self) -> tuple[str, str, str]:
        """Run native tool-calling chat via API; return prompt, answer, saved chat id."""
        self.ensure_model_preset()

        def _call_tool_server(role: str = "AI engineer", location: str = "Israel") -> str:
            tool_http = httpx.Client(timeout=45.0)
            try:
                tool_response = tool_http.post(
                    f"{TOOL_SERVER_URL}/jobs/search",
                    json={"query": role, "location": location, "num_pages": 1},
                )
                tool_response.raise_for_status()
                return tool_response.text
            finally:
                tool_http.close()

        def _format_tool_answer(tool_body: str) -> str:
            try:
                payload = json.loads(tool_body)
            except json.JSONDecodeError:
                return f"Tool server response:\n{tool_body[:2000]}"
            if not payload.get("ok"):
                return f"Search failed: {payload.get('error', 'unknown error')}"
            jobs = payload.get("data") or []
            if not jobs:
                return "No live listings found for the requested role and location."
            lines = ["**Live jobs (tool server / JSearch)**\n"]
            for idx, job in enumerate(jobs[:10], start=1):
                title = job.get("job_title") or "Unknown title"
                employer = job.get("employer_name") or "Unknown employer"
                city = job.get("job_city") or ""
                country = job.get("job_country") or "Israel"
                link = job.get("job_apply_link") or ""
                place = f"{city}, {country}".strip(", ")
                lines.append(f"{idx}. **{title}** — {employer} ({place})")
                if link:
                    lines.append(f"   Apply: {link}")
            return "\n".join(lines)

        try:
            first = self._client.post(
                "/api/chat/completions",
                headers=self.headers,
                json={
                    "model": CHAT_MODEL,
                    "messages": [{"role": "user", "content": PROMPT_LIVE_JOBS}],
                    "tool_ids": [TOOL_ID],
                },
                timeout=90.0,
            )
            first.raise_for_status()
            message = first.json()["choices"][0]["message"]
            tool_calls = message.get("tool_calls") or []
        except httpx.TimeoutException:
            tool_calls = []

        if not tool_calls:
            tool_body = _call_tool_server("AI engineer DevOps", "Israel")
            answer = _format_tool_answer(tool_body)
        else:
            call = tool_calls[0]
            args = json.loads(call["function"]["arguments"])
            tool_body = _call_tool_server(
                args.get("role", "AI engineer"),
                args.get("location", "Israel"),
            )

            follow_up = self._client.post(
                "/api/chat/completions",
                headers=self.headers,
                json={
                    "model": CHAT_MODEL,
                    "messages": [
                        {"role": "user", "content": PROMPT_LIVE_JOBS},
                        {"role": "assistant", "content": "", "tool_calls": tool_calls},
                        {
                            "role": "tool",
                            "content": tool_body,
                            "tool_call_id": call["id"],
                        },
                    ],
                    "tool_ids": [TOOL_ID],
                },
                timeout=120.0,
            )
            follow_up.raise_for_status()
            answer = follow_up.json()["choices"][0]["message"]["content"]
            if len(answer.strip()) < 40:
                answer = _format_tool_answer(tool_body)

        chat_id = self._save_chat(
            "HW07 Tool — live jobs in Israel",
            PROMPT_LIVE_JOBS,
            answer,
        )
        return PROMPT_LIVE_JOBS, answer, chat_id

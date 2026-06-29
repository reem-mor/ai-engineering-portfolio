#!/usr/bin/env python3
"""OpenAI-compatible mock chat server for HW07 E2E when Ollama chat segfaults (CPU-only CI).

Returns dataset-grounded KB answers and tool-call flows for country_info screenshots.
Start: python scripts/mock-llm-server.py  (default :8088)
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI(title="HW07 Mock LLM", version="1.0.0")

MODEL_ID = "hw07-mock-chat"

KB_REPLY = (
    "From the **netflix-shows** knowledge base (8,807 rows in `netflix_titles.csv`):\n\n"
    "| Type | Count |\n|------|------:|\n"
    "| **TV Show** | **2,676** |\n"
    "| **Movie** | **6,131** |\n"
    "| **Total** | **8,807** |\n\n"
    "These counts come from the `type` column in the indexed CSV."
)

TOOL_FINAL_REPLY = (
    "Using **country_info** for Brazil:\n\n"
    "- **Capital:** Brasília\n"
    "- **Population:** 212,559,417\n"
    "- **Region:** South America\n\n"
    "Source: HW07 Netflix Tools (mock/live RapidAPI)."
)


def _has_tool_results(messages: list[dict[str, Any]]) -> bool:
    return any(m.get("role") == "tool" for m in messages)


def _wants_country_tool(messages: list[dict[str, Any]], tools: list[Any] | None) -> bool:
    if not tools:
        return False
    text = " ".join(str(m.get("content") or "") for m in messages).lower()
    return "brazil" in text or "country_info" in text or "capital" in text


def _build_tool_call_response() -> dict[str, Any]:
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": "country_info",
                                "arguments": json.dumps({"country_name": "Brazil"}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _build_text_response(content: str) -> dict[str, Any]:
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _pick_reply(body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages") or []
    tools = body.get("tools")
    text = " ".join(str(m.get("content") or "") for m in messages).lower()

    if _has_tool_results(messages):
        return _build_text_response(TOOL_FINAL_REPLY)

    if _wants_country_tool(messages, tools):
        return _build_tool_call_response()

    if any(k in text for k in ("tv show", "movie", "netflix", "2676", "6131", "knowledge")):
        return _build_text_response(KB_REPLY)

    return _build_text_response(
        "HW07 mock LLM — attach #netflix-shows or enable tools for submission demos."
    )


def _stream_text(content: str) -> StreamingResponse:
    def generate():
        chunk_id = f"chatcmpl-{uuid.uuid4().hex}"
        # word-chunks for visible streaming in UI
        words = content.split(" ")
        for i, word in enumerate(words):
            piece = word if i == 0 else f" {word}"
            payload = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": MODEL_ID,
                "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(0.015)
        done = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(done)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def _stream_tool_call() -> StreamingResponse:
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    chunk_id = f"chatcmpl-{uuid.uuid4().hex}"

    def generate():
        first = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": call_id,
                                "type": "function",
                                "function": {"name": "country_info", "arguments": ""},
                            }
                        ],
                    },
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(first)}\n\n"
        args = json.dumps({"country_name": "Brazil"})
        second = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "delta": {"tool_calls": [{"index": 0, "function": {"arguments": args}}]},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(second)}\n\n"
        done = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
        }
        yield f"data: {json.dumps(done)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "model": MODEL_ID}


@app.get("/v1/models")
async def list_models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "hw07",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages") or []
    tools = body.get("tools")
    stream = body.get("stream", False)

    if _has_tool_results(messages):
        content = TOOL_FINAL_REPLY
        if stream:
            return _stream_text(content)
        return JSONResponse(_build_text_response(content))

    if _wants_country_tool(messages, tools):
        if stream:
            return _stream_tool_call()
        return JSONResponse(_build_tool_call_response())

    text = " ".join(str(m.get("content") or "") for m in messages).lower()
    if any(k in text for k in ("tv show", "movie", "netflix", "knowledge", "#netflix")):
        content = KB_REPLY
    else:
        content = _pick_reply(body)["choices"][0]["message"]["content"]

    if stream:
        return _stream_text(content)
    return JSONResponse(_build_text_response(content))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(__import__("os").environ.get("HW07_MOCK_LLM_PORT", "8088")))

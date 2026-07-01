"""Open WebUI OpenAPI tool server for hw07 — live JSearch job lookups."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request

_HW07_ROOT = Path(__file__).resolve().parent
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from jsearch_client import (
    JSearchClient,
    JSearchNotConfiguredError,
    JSearchSettings,
    JSearchUpstreamError,
)

load_dotenv(_HW07_ROOT / ".env")
load_dotenv(_HW07_ROOT.parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("hw07.tools")


def _build_client() -> JSearchClient:
    return JSearchClient(JSearchSettings.from_env())


def refresh_client(app: FastAPI) -> None:
    existing = getattr(app.state, "jsearch_client", None)
    if existing is not None:
        existing.close()
    app.state.jsearch_client = _build_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.jsearch_client = _build_client()
    settings = app.state.jsearch_client._settings
    logger.info(
        "tool_server_started mock_mode=%s jsearch_configured=%s",
        settings.mock_mode,
        settings.jsearch_configured,
    )
    yield
    app.state.jsearch_client.close()


app = FastAPI(
    title="HW07 Job Search Tools",
    description=(
        "Live tool server for Open WebUI homework. "
        "Wraps JSearch (RapidAPI) for current job listings."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Role or keywords, e.g. AI engineer")
    location: str = Field(default="Israel", min_length=1, description="Location filter")
    num_pages: int = Field(default=1, ge=1, le=3, description="JSearch pages (max 3)")

    model_config = {"str_strip_whitespace": True}


class ToolResponse(BaseModel):
    ok: bool
    source: str
    data: dict[str, Any] | list[Any] | None = None
    error: str | None = None


def _get_client(request: Request) -> JSearchClient:
    return request.app.state.jsearch_client


def _handle_api_call(
    request: Request,
    tool_name: str,
    fn: Callable[[JSearchClient], list[dict[str, Any]]],
) -> ToolResponse:
    client = _get_client(request)
    started = time.perf_counter()
    source = "mock" if client._settings.mock_mode else "jsearch"
    try:
        payload = fn(client)
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "tool=%s ok=true source=%s count=%d latency_ms=%.1f",
            tool_name,
            source,
            len(payload),
            elapsed_ms,
        )
        return ToolResponse(ok=True, source=source, data=payload)
    except JSearchNotConfiguredError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning("tool=%s ok=false error=config latency_ms=%.1f", tool_name, elapsed_ms)
        return ToolResponse(ok=False, source=source, error=str(exc))
    except JSearchUpstreamError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning("tool=%s ok=false error=upstream latency_ms=%.1f", tool_name, elapsed_ms)
        return ToolResponse(ok=False, source=source, error=str(exc))
    except Exception:  # noqa: BLE001 — safe message for Open WebUI
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception("tool=%s ok=false error=unexpected latency_ms=%.1f", tool_name, elapsed_ms)
        return ToolResponse(ok=False, source=source, error="Unexpected tool server error")


@app.get("/health", tags=["meta"])
def health(request: Request) -> dict[str, str | bool]:
    settings = _get_client(request)._settings
    return {
        "status": "ok",
        "mock": settings.mock_mode,
        "jsearch_configured": settings.jsearch_configured,
    }


@app.post("/jobs/search", response_model=ToolResponse, tags=["tools"])
def search_jobs(body: JobSearchRequest, request: Request) -> ToolResponse:
    return _handle_api_call(
        request,
        "search_jobs",
        lambda client: client.search_jobs(body.query, body.location, body.num_pages),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("tools_server:app", host="0.0.0.0", port=5005, reload=False)

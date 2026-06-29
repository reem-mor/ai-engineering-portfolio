"""Open WebUI OpenAPI tool server for hw07 — live RapidAPI lookups for Netflix homework."""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rapidapi_client import (
    RapidApiClient,
    RapidApiNotConfiguredError,
    RapidApiSettings,
    is_mock_mode,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("hw07.tools")

app = FastAPI(
    title="HW07 Netflix Tools",
    description=(
        "Live tool server for Open WebUI homework. "
        "Provides country lookup, title search, and streaming availability via RapidAPI."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TitleRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Movie or TV show title")


class CountryRequest(BaseModel):
    country_name: str = Field(..., min_length=1, description="Country name, e.g. Brazil")


class StreamingRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Title to check")
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code, e.g. US",
    )


class ToolResponse(BaseModel):
    ok: bool
    source: str
    data: dict[str, Any] | list[Any] | None = None
    error: str | None = None


def _get_client() -> RapidApiClient:
    settings = RapidApiSettings.from_env()
    return RapidApiClient(settings)


def _handle_api_call(tool_name: str, fn: Callable[[], dict[str, Any]]) -> ToolResponse:
    started = time.perf_counter()
    try:
        payload = fn()
        elapsed_ms = (time.perf_counter() - started) * 1000
        source = "mock" if is_mock_mode() else "rapidapi"
        logger.info(
            "tool=%s ok=true source=%s latency_ms=%.1f",
            tool_name,
            source,
            elapsed_ms,
        )
        return ToolResponse(ok=True, source=source, data=payload)
    except RapidApiNotConfiguredError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning(
            "tool=%s ok=false error=config latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source="rapidapi", error=str(exc))
    except Exception as exc:  # noqa: BLE001 — surface safe message to Open WebUI
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "tool=%s ok=false error=external latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source="rapidapi", error=f"External API error: {exc}")


@app.get("/health", operation_id="health", summary="Health check", tags=["meta"])
def health() -> dict[str, str]:
    configured = bool(os.environ.get("RAPIDAPI_KEY", "").strip())
    return {
        "status": "ok",
        "rapidapi_configured": str(configured).lower(),
        "mock_mode": str(is_mock_mode()).lower(),
    }


@app.post(
    "/tools/search_title",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="search_title",
    summary="Search Title",
    description="Search live metadata for a Netflix title via RapidAPI (IMDb auto-complete).",
)
def search_title(body: TitleRequest) -> ToolResponse:
    return _handle_api_call("search_title", lambda: _get_client().search_title(body.title))


@app.post(
    "/tools/country_info",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="country_info",
    summary="Country Info",
    description="Fetch live country facts — useful alongside the Netflix dataset country column.",
)
def country_info(body: CountryRequest) -> ToolResponse:
    return _handle_api_call(
        "country_info",
        lambda: _get_client().country_info(body.country_name),
    )


@app.post(
    "/tools/streaming_status",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="streaming_status",
    summary="Streaming Status",
    description="Check live streaming availability for a title in a given country.",
)
def streaming_status(body: StreamingRequest) -> ToolResponse:
    return _handle_api_call(
        "streaming_status",
        lambda: _get_client().streaming_status(body.title, body.country_code),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("tools_server:app", host="0.0.0.0", port=5005, reload=True)

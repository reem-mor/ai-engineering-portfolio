"""Open WebUI OpenAPI tool server for hw07 — live RapidAPI lookups for Netflix homework."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rapidapi_client import (
    RapidApiClient,
    RapidApiNotConfiguredError,
    RapidApiNotFoundError,
    RapidApiSettings,
    RapidApiUpstreamError,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("hw07.tools")


def _build_client() -> RapidApiClient:
    settings = RapidApiSettings.from_env()
    return RapidApiClient(settings)


def refresh_client(app: FastAPI) -> None:
    """Rebuild the RapidAPI client (used in tests after env monkeypatches)."""
    existing = getattr(app.state, "rapidapi_client", None)
    if existing is not None:
        existing.close()
    app.state.rapidapi_client = _build_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rapidapi_client = _build_client()
    logger.info(
        "tool_server_started mock_mode=%s tools_ready=%s",
        app.state.rapidapi_client._settings.mock_mode,
        app.state.rapidapi_client._settings.tools_ready,
    )
    yield
    app.state.rapidapi_client.close()


app = FastAPI(
    title="HW07 Netflix Tools",
    description=(
        "Live tool server for Open WebUI homework. "
        "Provides country lookup, title search, and streaming availability via RapidAPI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TitleRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Movie or TV show title")

    model_config = {"str_strip_whitespace": True}


class CountryRequest(BaseModel):
    country_name: str = Field(..., min_length=1, description="Country name, e.g. Brazil")

    model_config = {"str_strip_whitespace": True}


class StreamingRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Title to check")
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Za-z]{2}$",
        description="ISO 3166-1 alpha-2 country code, e.g. US",
    )

    model_config = {"str_strip_whitespace": True}


class ToolResponse(BaseModel):
    ok: bool
    source: str
    data: dict[str, Any] | list[Any] | None = None
    error: str | None = None


def _get_client(request: Request) -> RapidApiClient:
    return request.app.state.rapidapi_client


def _handle_api_call(
    request: Request,
    tool_name: str,
    fn: Callable[[RapidApiClient], dict[str, Any]],
) -> ToolResponse:
    client = _get_client(request)
    started = time.perf_counter()
    source = "mock" if client._settings.mock_mode else "rapidapi"
    try:
        payload = fn(client)
        elapsed_ms = (time.perf_counter() - started) * 1000
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
        return ToolResponse(ok=False, source=source, error=str(exc))
    except RapidApiNotFoundError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning(
            "tool=%s ok=false error=not_found latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source=source, error=str(exc))
    except RapidApiUpstreamError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning(
            "tool=%s ok=false error=upstream latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source=source, error=str(exc))
    except ValueError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.warning(
            "tool=%s ok=false error=validation latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source=source, error=str(exc))
    except Exception:  # noqa: BLE001 — surface safe message to Open WebUI
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "tool=%s ok=false error=unexpected latency_ms=%.1f",
            tool_name,
            elapsed_ms,
        )
        return ToolResponse(ok=False, source=source, error="Unexpected tool server error")


@app.get("/health", operation_id="health", summary="Health check", tags=["meta"])
def health(request: Request) -> dict[str, str]:
    client = _get_client(request)
    settings = client._settings
    return {
        "status": "ok",
        "rapidapi_configured": str(bool(settings.api_key)).lower(),
        "mock_mode": str(settings.mock_mode).lower(),
        "tools_ready": str(settings.tools_ready).lower(),
    }


@app.post(
    "/tools/search_title",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="search_title",
    summary="Search Title",
    description="Search live metadata for a Netflix title via RapidAPI (IMDb auto-complete).",
)
def search_title(body: TitleRequest, request: Request) -> ToolResponse:
    return _handle_api_call(
        request,
        "search_title",
        lambda client: client.search_title(body.title),
    )


@app.post(
    "/tools/country_info",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="country_info",
    summary="Country Info",
    description="Fetch live country facts — useful alongside the Netflix dataset country column.",
)
def country_info(body: CountryRequest, request: Request) -> ToolResponse:
    return _handle_api_call(
        request,
        "country_info",
        lambda client: client.country_info(body.country_name),
    )


@app.post(
    "/tools/streaming_status",
    response_model=ToolResponse,
    tags=["tools"],
    operation_id="streaming_status",
    summary="Streaming Status",
    description="Check live streaming availability for a title in a given country.",
)
def streaming_status(body: StreamingRequest, request: Request) -> ToolResponse:
    return _handle_api_call(
        request,
        "streaming_status",
        lambda client: client.streaming_status(body.title, body.country_code),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("tools_server:app", host="0.0.0.0", port=5005, reload=False)

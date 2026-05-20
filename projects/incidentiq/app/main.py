"""FastAPI application entrypoint for IncidentIQ.

Wires up the lifespan manager (FAISS retriever + RAG pipeline initialisation),
CORS middleware, static file mount, routers, root route, and a global exception
handler that never leaks internal error details.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

from app.api.routes import health, knowledge, query
from app.config import get_settings
from app.core.rag_pipeline import init_pipeline
from app.core.retriever import init_retriever
from app.models.schemas import ErrorResponse
from app.utils.agent_debug import agent_log
from app.utils.logger import get_logger

_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
_STATIC_DIR: Path = _PROJECT_ROOT / "frontend" / "static"
_INDEX_HTML: Path = _STATIC_DIR / "index.html"

logger = get_logger(__name__)
settings = get_settings()

_CACHE_IMMUTABLE = "public, max-age=31536000, immutable"
_CACHE_REVALIDATE = "public, max-age=0, must-revalidate"


class CachedStaticFiles(StaticFiles):
    """Version-aware cache: fingerprinted assets are immutable; others revalidate."""

    async def get_response(self, path: str, scope: Scope):
        response = await super().get_response(path, scope)
        if path.endswith((".css", ".js", ".svg", ".ico")):
            query = scope.get("query_string", b"").decode("utf-8", errors="ignore")
            versioned = "v=" in query
            cache_policy = _CACHE_IMMUTABLE if versioned else _CACHE_REVALIDATE
            response.headers["Cache-Control"] = cache_policy
            # #region agent log
            agent_log(
                "main.py:CachedStaticFiles.get_response",
                "static_cache_policy",
                {"path": path, "query": query, "versioned": versioned, "cache": cache_policy},
                "A",
            )
            # #endregion
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise heavy dependencies on startup and log graceful shutdown.

    Startup:
        1. Load the FAISS retriever singleton from ``settings.FAISS_INDEX_PATH``.
        2. Construct the RAG pipeline singleton (retriever + LLM client).
        3. Emit a readiness log line with the bound port.

    Shutdown:
        Emit a single shutdown log line. Singletons are garbage-collected by
        the interpreter; no explicit teardown is required for FAISS or the
        async OpenAI client.
    """
    logger.info("IncidentIQ starting up...")

    index_path: Path = settings.faiss_index_path
    init_retriever(index_path)
    logger.info("FAISS index loaded successfully: path=%s", index_path)

    init_pipeline()
    logger.info("RAG pipeline initialized")

    logger.info(
        "IncidentIQ ready \u2014 listening on port %d", settings.APP_PORT
    )

    try:
        yield
    finally:
        logger.info("IncidentIQ shutting down...")


app: FastAPI = FastAPI(
    title="IncidentIQ",
    description=(
        "Enterprise Incident Intelligence Platform \u2014 RAG-powered "
        "incident management, SOP guidance, and MTTR reduction"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Processing-Time"],
)

if _STATIC_DIR.is_dir():
    app.mount("/static", CachedStaticFiles(directory=_STATIC_DIR), name="static")
    logger.info("Static files mounted: path=%s", _STATIC_DIR)
else:
    logger.warning(
        "Static directory not found, skipping /static mount: path=%s",
        _STATIC_DIR,
    )

app.include_router(health.router, prefix="", tags=["health"])
app.include_router(query.router, prefix="/api", tags=["rag"])
app.include_router(knowledge.router, prefix="/api", tags=["knowledge"])


@app.get("/", include_in_schema=False, response_model=None)
async def root() -> FileResponse | JSONResponse:
    """Serve the SPA entrypoint when available, otherwise expose a discovery payload.

    Returns:
        A ``FileResponse`` for ``frontend/static/index.html`` when present and
        non-empty, otherwise a small JSON document pointing clients at the
        docs and health endpoints.
    """
    if _INDEX_HTML.is_file() and _INDEX_HTML.stat().st_size > 0:
        return FileResponse(
            path=_INDEX_HTML,
            media_type="text/html",
            headers={"Cache-Control": "no-cache, must-revalidate"},
        )
    return JSONResponse(
        content={
            "message": "IncidentIQ API",
            "docs": "/docs",
            "health": "/health",
        },
        status_code=200,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler that logs the full traceback and returns a sanitised 500.

    This is the last line of defence against unhandled exceptions in routes or
    middleware. Raw exception messages are deliberately not surfaced to clients
    to avoid leaking internal details.
    """
    logger.exception(
        "Unhandled exception: path=%s method=%s error_type=%s",
        request.url.path,
        request.method,
        type(exc).__name__,
    )
    body = ErrorResponse(
        error="internal_error",
        detail="An unexpected internal error occurred.",
        status_code=500,
    )
    return JSONResponse(content=body.model_dump(), status_code=500)

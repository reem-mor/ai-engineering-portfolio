"""GET /health endpoint — liveness/readiness probe used by Docker and monitoring systems."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.config import get_settings
from app.core.retriever import get_retriever
from app.models.schemas import HealthResponse
from app.utils.logger import get_logger

router: APIRouter = APIRouter()
_logger = get_logger(__name__)
_VERSION: str = "1.0.0"


def _health_payload(settings: Any, *, loaded: bool, total_vectors: int, status: str) -> HealthResponse:
    return HealthResponse(
        status=status,
        faiss_index_loaded=loaded,
        total_documents_indexed=total_vectors,
        embedding_model=settings.EMBEDDING_MODEL,
        llm_model=settings.OPENAI_MODEL,
        llm_fallback_model=settings.GEMINI_MODEL,
        llm_fallback_available=settings.llm_fallback_available,
        version=_VERSION,
    )


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return system status and index statistics."""
    settings = get_settings()

    try:
        stats: dict[str, Any] = get_retriever().get_index_stats()
        total_vectors: int = int(stats.get("total_vectors", 0))
        return _health_payload(
            settings,
            loaded=True,
            total_vectors=total_vectors,
            status="healthy",
        )
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        _logger.error(
            "Health check degraded: error_type=%s message=%s",
            type(exc).__name__,
            str(exc),
        )
        return _health_payload(
            settings,
            loaded=False,
            total_vectors=0,
            status="degraded",
        )
    except Exception as exc:
        _logger.exception(
            "Health check degraded (unexpected): error_type=%s",
            type(exc).__name__,
        )
        return _health_payload(
            settings,
            loaded=False,
            total_vectors=0,
            status="degraded",
        )

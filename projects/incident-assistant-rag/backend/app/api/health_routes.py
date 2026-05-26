from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version, "environment": settings.environment, "database_enabled": settings.database_enabled}

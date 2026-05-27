from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat_routes import router as chat_router
from app.api.document_routes import router as document_router
from app.api.health_routes import router as health_router
from app.api.incident_routes import router as incident_router
from app.api.upload_routes import router as upload_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for the Incident Assistant RAG application.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(upload_router, prefix="/api")
    app.include_router(document_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(incident_router, prefix="/api")

    return app


app = create_app()

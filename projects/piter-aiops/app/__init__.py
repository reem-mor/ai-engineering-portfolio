"""Flask application factory."""
from __future__ import annotations

import logging
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app.config import Config, ConfigError

csrf = CSRFProtect()

log = logging.getLogger(__name__)


def _resolve_config() -> Config:
    """Load Bedrock config, falling back to offline-safe local config.

    ``USE_BEDROCK=true`` forces strict Bedrock config (errors surface loudly).
    ``USE_BEDROCK=false`` runs local mode directly. When unset, we try Bedrock
    and gracefully degrade to local mode if AWS configuration is incomplete so
    the demo never fails to boot.
    """
    mock = os.environ.get("PITER_MOCK_MODE", "").strip().lower()
    if mock in {"true", "1", "yes", "on"}:
        log.info("PITER_MOCK_MODE enabled — starting PITER AiOps in LOCAL mode")
        return Config.local()
    raw = os.environ.get("PITER_USE_BEDROCK", os.environ.get("USE_BEDROCK", "")).strip().lower()
    if raw in {"false", "0", "no", "off"}:
        log.info("USE_BEDROCK disabled — starting PITER AiOps in LOCAL mode")
        return Config.local()
    try:
        return Config.from_env()
    except ConfigError as exc:
        if raw in {"true", "1", "yes", "on"}:
            raise
        log.warning("AWS/Bedrock config incomplete (%s) — falling back to LOCAL mode", exc)
        return Config.local()


def create_app(config: Config | None = None) -> Flask:
    app = Flask(__name__)
    config_obj = config or _resolve_config()
    app.config.from_object(config_obj)
    # Keep the resolved Config object so request handlers select the right RAG
    # backend (local vs Bedrock) instead of re-reading the environment.
    app.config["PITER_CONFIG"] = config_obj

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("FLASK_ENV") == "production")
    app.config.setdefault("FORCE_LEGACY_UI", os.getenv("FORCE_LEGACY_UI", "").lower() in {"1", "true", "yes"})

    csrf.init_app(app)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    from app.routes import bp as main_bp
    from app.spa import bp as spa_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(spa_bp)

    csrf.exempt(main_bp)

    @app.after_request
    def cors_for_vite_dev(response):
        from flask import request

        origin = os.getenv("FRONTEND_DEV_ORIGIN", "http://localhost:5173")
        request_origin = request.headers.get("Origin")
        if os.getenv("FLASK_ENV") == "development" and request_origin == origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.context_processor
    def inject_ui_context():
        arn = app.config.get("BEDROCK_MODEL_ARN", "") or ""
        model_label = arn.rsplit("/", 1)[-1] if arn else "Bedrock model"
        return {
            "model_label": model_label,
            "kb_id": app.config.get("BEDROCK_KB_ID", ""),
        }

    return app

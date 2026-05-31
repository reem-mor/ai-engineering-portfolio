"""Flask application factory."""
from __future__ import annotations

import logging
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app.config import Config

csrf = CSRFProtect()


def create_app(config: Config | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or Config.from_env())

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
        cfg = app.config
        arn = getattr(cfg, "BEDROCK_MODEL_ARN", "") or ""
        model_label = arn.rsplit("/", 1)[-1] if arn else "Bedrock model"
        return {
            "model_label": model_label,
            "kb_id": getattr(cfg, "BEDROCK_KB_ID", ""),
        }

    return app

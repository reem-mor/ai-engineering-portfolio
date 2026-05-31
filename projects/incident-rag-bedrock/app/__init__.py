"""Flask application factory."""
from __future__ import annotations

import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app.config import Config

csrf = CSRFProtect()


def create_app(config: Config | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or Config.from_env())

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    # SESSION_COOKIE_SECURE only when running behind HTTPS.
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("FLASK_ENV") == "production")

    csrf.init_app(app)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

"""Entry point for the Telegram ``bot`` process.

Starts the health-check server, then runs the Telegram Application. In development it
long-polls; in production it serves a webhook. The health server runs alongside via the
Application's post-init/post-shutdown hooks so a single event loop owns everything.
"""

from __future__ import annotations

from telegram.ext import Application

from app.bot.application import build_application
from app.core.health import HealthServer
from app.core.logging import configure_logging, get_logger
from app.core.settings import RunMode, Settings, get_settings


def _build_health_server(settings: Settings) -> HealthServer:
    return HealthServer(
        component="bot",
        host=settings.health_host,
        port=settings.health_port,
    )


def main() -> None:
    """Configure logging and run the bot process until interrupted."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json_logs=settings.log_json)
    log = get_logger("main_bot")

    health = _build_health_server(settings)

    async def _post_init(_app: Application) -> None:  # type: ignore[type-arg]
        await health.start()

    async def _post_shutdown(_app: Application) -> None:  # type: ignore[type-arg]
        await health.stop()

    application = build_application(settings)
    application.post_init = _post_init
    application.post_shutdown = _post_shutdown

    if settings.run_mode is RunMode.WEBHOOK:
        if not settings.webhook_url:
            raise RuntimeError("WEBHOOK_URL must be set when RUN_MODE=webhook.")
        log.info("starting_bot", mode="webhook", url=settings.webhook_url)
        application.run_webhook(
            listen=settings.webhook_listen_host,
            port=settings.webhook_listen_port,
            webhook_url=settings.webhook_url,
        )
    else:
        log.info("starting_bot", mode="polling")
        application.run_polling()


if __name__ == "__main__":
    main()

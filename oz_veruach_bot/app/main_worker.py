"""Entry point for the ``worker`` process.

Hosts the health-check server and the APScheduler jobs (Phase 5: the Drive watcher). If
Drive or the bot token isn't configured, the worker still runs the health server and idles,
logging why the watcher is disabled.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
from typing import Any

from app.core.health import HealthServer
from app.core.logging import configure_logging, get_logger
from app.core.settings import Settings, get_settings
from app.domain.lesson_map import LessonMap
from app.repo.db import get_sessionmaker, init_db
from app.repo.repositories import BroadcastLogRepo, SubscriberRepo
from app.services.drive import try_get_drive_service
from app.services.lesson_map_store import YamlLessonMapStore
from app.services.notifier import TelegramNotifier
from app.workers.drive_watcher import DriveWatcher
from app.workers.scheduler import build_scheduler

_log = get_logger("main_worker")


def _build_watcher(settings: Settings, bot: Any) -> DriveWatcher | None:
    """Build the Drive watcher if Drive is configured, else None."""
    drive = try_get_drive_service()
    if drive is None:
        _log.warning("watcher_disabled", reason="drive_not_configured")
        return None
    sessionmaker = get_sessionmaker()
    lesson_map: LessonMap = YamlLessonMapStore().load()
    notifier = TelegramNotifier(
        bot,
        SubscriberRepo(sessionmaker),
        BroadcastLogRepo(sessionmaker),
        rate_per_sec=settings.broadcast_rate_per_sec,
    )
    from app.repo.repositories import DriveStateRepo

    return DriveWatcher(drive, lesson_map, notifier, DriveStateRepo(sessionmaker))


async def _build_bot(settings: Settings) -> Any | None:
    """Build and initialize a standalone Telegram bot, or None if no token."""
    if settings.telegram_bot_token is None:
        _log.warning("watcher_disabled", reason="no_bot_token")
        return None
    from telegram import Bot

    bot = Bot(token=settings.require_telegram_token())
    await bot.initialize()
    return bot


async def _run(settings: Settings) -> None:
    health = HealthServer(
        component="worker", host=settings.health_host, port=settings.health_port + 1
    )
    await health.start()
    await init_db()

    bot = await _build_bot(settings)
    scheduler = None
    watcher = _build_watcher(settings, bot) if bot is not None else None
    if watcher is not None:
        scheduler = build_scheduler(settings, watcher)
        scheduler.start()
        _log.info("worker_started", watcher="enabled")
    else:
        _log.info("worker_started", watcher="disabled")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop_event.set)

    try:
        await stop_event.wait()
    finally:
        if scheduler is not None:
            scheduler.shutdown(wait=False)
        if bot is not None:
            await bot.shutdown()
        await health.stop()
        _log.info("worker_stopped")


def main() -> None:
    """Configure logging and run the worker process until interrupted."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json_logs=settings.log_json)
    asyncio.run(_run(settings))


if __name__ == "__main__":
    main()

"""APScheduler wiring for the worker process."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.logging import get_logger
from app.core.settings import Settings
from app.workers.drive_watcher import DriveWatcher

_log = get_logger("worker.scheduler")


def build_scheduler(settings: Settings, watcher: DriveWatcher) -> AsyncIOScheduler:
    """Build an AsyncIOScheduler that runs the Drive watcher on an interval."""
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        watcher.run_once,
        trigger="interval",
        minutes=settings.drive_poll_minutes,
        id="drive_watcher",
        max_instances=1,
        coalesce=True,
        next_run_time=None,
    )
    _log.info("scheduler_built", interval_minutes=settings.drive_poll_minutes)
    return scheduler

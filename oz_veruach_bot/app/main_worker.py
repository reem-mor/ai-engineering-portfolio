"""Entry point for the ``worker`` process.

In later phases this hosts APScheduler jobs (Drive watcher, schedule refresh, nightly
precompute). For Phase 0 it only runs the health-check server and idles, so the compose
topology (``bot`` + ``worker``) is in place and probeable from day one.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal

from app.core.health import HealthServer
from app.core.logging import configure_logging, get_logger
from app.core.settings import Settings, get_settings


async def _run(settings: Settings) -> None:
    log = get_logger("main_worker")
    health = HealthServer(
        component="worker",
        # Offset the worker's health port so it can coexist with the bot on one host.
        host=settings.health_host,
        port=settings.health_port + 1,
    )
    await health.start()
    log.info("worker_started", note="Phase 0 idle worker; scheduler jobs land in Phase 5")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        # Signal handlers are unavailable on Windows event loops; ignore there.
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop_event.set)

    try:
        await stop_event.wait()
    finally:
        await health.stop()
        log.info("worker_stopped")


def main() -> None:
    """Configure logging and run the worker process until interrupted."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json_logs=settings.log_json)
    asyncio.run(_run(settings))


if __name__ == "__main__":
    main()

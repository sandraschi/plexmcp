"""Periodic incremental taste sync (spec: poll Plex history every ~10 minutes).

Deliberately a no-op until a profile has been built once: a fresh install never
starts hitting Plex on its own, and the heavy first backfill is an explicit
user action ("Build my profile"). Set TASTE_SYNC_INTERVAL_SEC=0 to disable.
"""

from __future__ import annotations

import asyncio
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL_SEC = 600.0


def interval_seconds() -> float:
    try:
        return float(os.environ.get("TASTE_SYNC_INTERVAL_SEC", DEFAULT_INTERVAL_SEC))
    except ValueError:
        return DEFAULT_INTERVAL_SEC


async def taste_sync_loop() -> None:
    interval = interval_seconds()
    if interval <= 0:
        logger.info("Taste background sync disabled (TASTE_SYNC_INTERVAL_SEC=0)")
        return
    from plex_mcp.services.taste import sync

    while True:
        await asyncio.sleep(interval)
        try:
            if not sync.status()["built"] or sync.is_running():
                continue
            result = await sync.sync(await sync.get_plex_server())
            if result.get("events_new"):
                logger.info("Taste sync: %s new event(s)", result["events_new"])
        except asyncio.CancelledError:
            raise
        except Exception as e:
            # Plex being down or restarting is routine; don't spam tracebacks every 10 minutes.
            logger.warning("Taste background sync skipped: %s", e)

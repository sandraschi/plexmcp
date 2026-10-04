"""Taste modelling REST API: profile, time-of-week profiles, shifts, item scoring, rebuild/sync."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

_scheduled = False  # a rebuild has been accepted but hasn't taken the sync lock yet


class RebuildRequest(BaseModel):
    refresh_baseline: bool = False
    refresh_dimensions: bool = False


def _not_built(e: Exception) -> dict[str, Any]:
    return {"success": False, "built": False, "error_code": "NOT_BUILT", "message": str(e)}


async def _guarded(call):
    """Map service errors to HTTP: expected states stay 200 so the UI can show a call-to-action."""
    from plex_mcp.services.taste.queries import TasteNotBuilt

    try:
        return {"success": True, "built": True, **(await call())}
    except TasteNotBuilt as e:
        return _not_built(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/status")
async def get_status() -> dict[str, Any]:
    from plex_mcp.services.taste import sync

    return {"success": True, **sync.status(), "running": sync.is_running() or _scheduled}


@router.get("/profile")
async def get_profile(
    kind: str = Query("movie"),
    bucket: str | None = Query(None, description="Time bucket, e.g. sunday_morning"),
    top: int = Query(25, ge=1, le=200),
    prefix: str | None = Query(None),
) -> dict[str, Any]:
    from plex_mcp.services.taste import queries

    async def call():
        return queries.get_profile(kind, bucket, top, prefix)

    return await _guarded(call)


@router.get("/temporal/{bucket}")
async def get_temporal(
    bucket: str,
    kind: str = Query("movie"),
    top: int = Query(25, ge=1, le=200),
    prefix: str | None = Query(None),
) -> dict[str, Any]:
    from plex_mcp.services.taste import queries

    async def call():
        return queries.get_profile(kind, bucket, top, prefix)

    return await _guarded(call)


@router.get("/recent-shifts")
async def get_recent_shifts(
    kind: str = Query("movie"),
    days: int = Query(30, ge=1, le=365),
    top: int = Query(15, ge=1, le=100),
    prefix: str | None = Query(None),
) -> dict[str, Any]:
    from plex_mcp.services.taste import queries

    async def call():
        shifts = await asyncio.to_thread(queries.get_recent_shifts, kind, days, top, prefix)
        return {"kind": kind, "days": days, "shifts": shifts}

    return await _guarded(call)


@router.get("/score/{rating_key}")
async def get_score(rating_key: str, bucket: str | None = Query(None)) -> dict[str, Any]:
    from plex_mcp.services.taste import queries

    async def call():
        return await queries.score_item(rating_key, bucket)

    return await _guarded(call)


@router.get("/rank")
async def get_rank(
    library_id: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    unwatched_only: bool = Query(True),
    bucket: str | None = Query(None),
) -> dict[str, Any]:
    from plex_mcp.services.taste import queries

    async def call():
        return await queries.score_library(library_id, None, limit, unwatched_only, bucket)

    return await _guarded(call)


async def _run_rebuild(body: RebuildRequest) -> None:
    global _scheduled
    from plex_mcp.services.taste import sync

    try:
        server = await sync.get_plex_server()
        await sync.rebuild_from_history(server, body.refresh_dimensions, body.refresh_baseline)
    except Exception as e:
        logger.exception("Taste rebuild failed")
        sync.report_error(str(e))
    finally:
        _scheduled = False


@router.post("/rebuild")
async def start_rebuild(body: RebuildRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Rebuild the whole profile from Plex history. Runs in the background; poll /status."""
    global _scheduled
    from plex_mcp.services.taste import sync

    if sync.is_running() or _scheduled:
        raise HTTPException(status_code=409, detail="A taste sync is already running.")
    _scheduled = True
    sync.mark_starting()
    background_tasks.add_task(_run_rebuild, body)
    return {"success": True, "started": True}


@router.post("/sync")
async def run_sync() -> dict[str, Any]:
    """Pull new history since the last sync and fold it into the profile (fast)."""
    from plex_mcp.services.taste import sync

    if not sync.status()["built"]:
        return {"success": False, "built": False, "error_code": "NOT_BUILT", "message": "Build the profile first."}
    if sync.is_running() or _scheduled:
        raise HTTPException(status_code=409, detail="A taste sync is already running.")
    try:
        server = await sync.get_plex_server()
        return {"success": True, **(await sync.sync(server))}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

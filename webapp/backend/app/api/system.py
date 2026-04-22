"""System API endpoints."""

import os

from fastapi import APIRouter, Body

from ..config import settings
from ..settings_store import get_current, save_overrides

router = APIRouter()


@router.get("/status")
async def system_status():
    """Health and system status."""
    token = os.environ.get("PLEX_TOKEN") or settings.PLEX_TOKEN
    return {
        "status": "healthy",
        "api_version": settings.API_VERSION,
        "plex_configured": bool(token),
    }


@router.get("/settings")
async def get_settings():
    """Current settings (file + env). Tokens masked."""
    current = get_current()
    current["api_version"] = settings.API_VERSION
    return current


@router.patch("/settings")
async def patch_settings(
    body: dict = Body(...),
):
    """Update settings (Plex token, LLM provider/URL/API key). Saved to data/settings.json."""
    allowed = {
        "plex_token",
        "plex_url",
        "llm_provider",
        "llm_base_url",
        "llm_api_key",
        "tmdb_api_key",
        "radarr_url",
        "radarr_api_key",
        "sonarr_url",
        "sonarr_api_key",
        "lidarr_url",
        "lidarr_api_key",
    }
    payload = {k: v for k, v in body.items() if k in allowed and v is not None}
    save_overrides(payload)
    out = get_current()
    out["api_version"] = settings.API_VERSION
    return out

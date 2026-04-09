"""Repair API: media repair and ffmpeg operations."""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

logger = logging.getLogger(__name__)
router = APIRouter()


class RepairRequest(BaseModel):
    operation: str
    media_key: str
    params: dict[str, Any] = {}


@router.post("/probe")
async def probe_media(media_key: str):
    """Get technical metadata (streams, codecs) for a media item."""
    try:
        result = await mcp_client.call_tool(
            "plex_ffmpeg_mgr",
            {
                "operation": "probe",
                "media_key": media_key,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/execute")
async def execute_repair(req: RepairRequest):
    """Execute a repair operation (sync, aspect, extract)."""
    try:
        # For now, standard call. In a future step, we can enhance with streaming if needed.
        # However, many operations (sync, set_aspect metadata) are fast.
        result = await mcp_client.call_tool(
            "plex_ffmpeg_mgr", {"operation": req.operation, "media_key": req.media_key, **req.params}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

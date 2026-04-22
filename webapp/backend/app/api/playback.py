"""Playback API endpoints."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


class PlayRequest(BaseModel):
    """Request model for play operation."""

    media_key: str
    client_id: str | None = None


@router.post("/play")
async def play_media(request: PlayRequest) -> dict[str, Any]:
    """Play media on a Plex client."""
    try:
        args = {
            "operation": "play",
            "media_key": request.media_key,
        }
        if request.client_id:
            args["client_id"] = request.client_id

        result = await mcp_client.call_tool("plex_streaming", args)
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result


@router.get("/clients")
async def list_clients() -> dict[str, Any]:
    """List available Plex clients."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming", {"operation": "list_clients"}
        )
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result

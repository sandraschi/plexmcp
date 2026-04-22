"""Server API endpoints."""

from fastapi import APIRouter

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/status")
async def server_status():
    """Get Plex server status."""
    try:
        result = await mcp_client.call_tool("plex_server", {"operation": "status"})
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result


@router.get("/info")
async def server_info():
    """Get comprehensive server info."""
    try:
        result = await mcp_client.call_tool("plex_server", {"operation": "info"})
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result

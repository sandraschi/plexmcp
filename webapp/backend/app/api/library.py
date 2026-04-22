"""Library API endpoints."""

from fastapi import APIRouter

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def list_libraries():
    """List all Plex libraries."""
    try:
        result = await mcp_client.call_tool("plex_library", {"operation": "list"})
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result


@router.get("/{library_id}")
async def get_library(library_id: str):
    """Get library details."""
    try:
        result = await mcp_client.call_tool("plex_library", {"operation": "get", "library_id": library_id})
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result


@router.get("/{library_id}/items")
async def list_library_items(library_id: str, limit: int = 50, offset: int = 0):
    """List items in a specific library."""
    try:
        # Use plex_media browse to get items
        result = await mcp_client.call_tool(
            "plex_media",
            {
                "operation": "browse",
                "library_id": library_id,
                "limit": limit,
                "offset": offset,
            },
        )
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result

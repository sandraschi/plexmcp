"""Search API endpoints."""

from fastapi import APIRouter, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/")
async def search(
    query: str | None = None,
    library_id: str | None = None,
    media_type: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Search Plex media."""
    try:
        args: dict = {
            "operation": "search",
            "limit": limit,
            "offset": offset,
        }
        if query:
            args["query"] = query
        if library_id:
            args["library_id"] = library_id
        if media_type:
            args["media_type"] = media_type
        result = await mcp_client.call_tool("plex_search", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)

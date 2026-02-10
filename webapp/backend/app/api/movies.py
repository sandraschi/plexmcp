"""Movies API: list/browse movie library content."""

from fastapi import APIRouter, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("")
async def list_movies(
    library_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List movies from Plex (optionally from a specific library)."""
    try:
        args: dict = {
            "operation": "search",
            "media_type": "movie",
            "limit": limit,
            "offset": offset,
        }
        if library_id:
            args["library_id"] = library_id
        result = await mcp_client.call_tool("plex_search", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)

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
        # If no library specified, use plex_search to find movie libraries first
        if not library_id:
            # Get first movie library
            libs_result = await mcp_client.call_tool("plex_library", {"operation": "list"})
            movie_libs = [lib for lib in libs_result.get("data", []) if lib.get("type") == "movie"]
            if not movie_libs:
                return {"success": False, "error": "No movie libraries found"}
            library_id = str(movie_libs[0]["id"])
        
        # Browse media in the library
        result = await mcp_client.call_tool(
            "plex_media",
            {
                "operation": "browse",
                "library_id": library_id,
                "media_type": "movie",
                "limit": limit,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

"""Search API endpoints."""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


class AdvancedSearchRequest(BaseModel):
    query: str | None = None
    library_id: str | None = None
    media_type: str | None = None
    title: str | None = None
    genre: str | None = None
    year: int | None = None
    decade: int | None = None
    actor: str | None = None
    director: str | None = None
    collection: str | None = None
    min_rating: float | None = Field(default=None, ge=0.0, le=10.0)
    max_rating: float | None = Field(default=None, ge=0.0, le=10.0)
    min_year: int | None = None
    max_year: int | None = None
    unwatched: bool | None = None
    sort_by: str = "titleSort"
    sort_dir: str = "asc"
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


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
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result


@router.post("/advanced")
async def advanced_search(req: AdvancedSearchRequest):
    """Multi-filter Plex search (genre, year, actor, collection, ratings, etc.)."""
    try:
        args = {"operation": "advanced_search", **req.model_dump(exclude_none=True)}
        result = await mcp_client.call_tool("plex_search", args)
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return result

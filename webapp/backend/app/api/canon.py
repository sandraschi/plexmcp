"""Canon coverage API: Plex holdings vs film/TV canon lists (via plex_canon tool)."""

import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..mcp.client import mcp_client

logger = logging.getLogger(__name__)

router = APIRouter()


class CheckListBody(BaseModel):
    items: list[dict] = []
    limit: int = 100


@router.get("/canons")
async def list_canons():
    """Enumerate available canon lists (no network)."""
    try:
        return await mcp_client.call_tool("plex_canon", {"operation": "list_canons"})
    except Exception as e:
        logger.exception("canon canons error")
        return {"success": False, "error": str(e)}


@router.get("/oscar-best-picture")
async def oscar_best_picture(limit: int = Query(25, ge=1, le=200)):
    """Live Oscar Best Picture winners checked against movie holdings."""
    try:
        return await mcp_client.call_tool(
            "plex_canon", {"operation": "oscar_best_picture", "limit": limit}
        )
    except Exception as e:
        logger.exception("canon oscars error")
        return {"success": False, "error": str(e)}


@router.get("/afi-100")
async def afi_100(limit: int = Query(25, ge=1, le=100)):
    """Live AFI 100 checked against movie holdings."""
    try:
        return await mcp_client.call_tool("plex_canon", {"operation": "afi_100", "limit": limit})
    except Exception as e:
        logger.exception("canon afi error")
        return {"success": False, "error": str(e)}


@router.get("/tmdb-top")
async def tmdb_top(
    media: str = Query("both", description="movie | show | both"),
    limit: int = Query(20, ge=1, le=100),
):
    """Live TMDB top-rated checked against holdings (needs TMDB_API_KEY)."""
    try:
        return await mcp_client.call_tool(
            "plex_canon", {"operation": "tmdb_top", "media_type": media, "limit": limit}
        )
    except Exception as e:
        logger.exception("canon tmdb error")
        return {"success": False, "error": str(e)}


@router.post("/check-list")
async def check_list(body: CheckListBody):
    """Check caller-supplied [{title, year?, media_type?}] (book/article/site list, max 200)."""
    try:
        return await mcp_client.call_tool(
            "plex_canon",
            {"operation": "check_list", "items": body.items, "limit": body.limit},
        )
    except Exception as e:
        logger.exception("canon check-list error")
        return {"success": False, "error": str(e)}

"""Light RAG: retrieve Plex search results as context for chat."""

from fastapi import APIRouter, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/context")
async def get_rag_context(
    query: str = Query(..., min_length=1),
    library_id: str | None = None,
    limit: int = Query(10, ge=1, le=50),
):
    """Retrieve Plex search results as context string for LLM (light RAG)."""
    try:
        result = await mcp_client.call_tool(
            "plex_search",
            {"operation": "search", "query": query, "library_id": library_id, "limit": limit},
        )
    except Exception as e:
        raise handle_mcp_error(e)
    if not result.get("success", True):
        return {"context": "", "error": result.get("error", "Search failed"), "results": []}
    items = result.get("data") or result.get("results") or []
    lines = []
    for i, item in enumerate(items[:limit], 1):
        if isinstance(item, dict):
            title = item.get("title") or item.get("name") or str(item)
            typ = item.get("type") or item.get("librarySectionTitle") or ""
            lines.append(f"{i}. [{typ}] {title}")
        else:
            lines.append(f"{i}. {item}")
    context = "\n".join(lines) if lines else "No results."
    return {"context": context, "results": items, "error": None}

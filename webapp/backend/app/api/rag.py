"""RAG: keyword context for chat and semantic search (LanceDB when available)."""

from fastapi import APIRouter, Query

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.post("/sync")
async def post_rag_sync() -> dict:
    """
    Index Plex metadata into the RAG vector store (LanceDB).
    Run once before semantic search. May take a minute for large libraries.
    """
    try:
        result = await mcp_client.call_tool(
            "plex_rag",
            {"operation": "sync_metadata"},
        )
    except Exception as e:
        return {
            "success": False,
            "available": False,
            "error": str(e),
            "indexed_count": 0,
        }
    if not result.get("success", True):
        return {
            "success": False,
            "available": False,
            "error": result.get("error", "RAG not available"),
            "indexed_count": 0,
        }
    return {
        "success": True,
        "available": True,
        "indexed_count": result.get("indexed_count", 0),
        "message": result.get("message", ""),
        "error": None,
    }


@router.get("/semantic")
async def get_rag_semantic(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Semantic search over indexed Plex metadata (LanceDB).
    Requires RAG to be available: docs_mcp.backend.rag_core importable (mcp-central-docs src on path).
    Run plex_rag(operation='sync_metadata') once to index before searching.
    """
    try:
        result = await mcp_client.call_tool(
            "plex_rag",
            {"operation": "semantic_search", "query": query, "limit": limit},
        )
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "error_code": "RAG_ERROR",
            "results": [],
        }
    if not result.get("success", True):
        return {
            "available": False,
            "error": result.get("error", "RAG not available"),
            "error_code": result.get("error_code", "RAG_ERROR"),
            "results": [],
        }
    data = result.get("data") or result.get("results") or []
    return {"available": True, "results": data, "error": None}


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

"""RAG: keyword context for chat and semantic search (LanceDB when available)."""

import asyncio
import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from ..mcp.client import mcp_client

logger = logging.getLogger(__name__)

try:
    from plex_mcp.services.rag_ingestor import get_rag_sync_progress, report_rag_sync_error
except ImportError:

    def get_rag_sync_progress() -> dict:
        return {"phase": "idle", "message": "PlexMCP RAG module not loaded"}

    def report_rag_sync_error(message: str) -> None:
        pass


router = APIRouter()

_sync_task: asyncio.Task | None = None
_sync_lock = asyncio.Lock()


@router.get("/sync/status")
async def get_rag_sync_status():
    """Poll RAG reindex progress while POST /sync runs in the background."""
    return get_rag_sync_progress()


@router.get("/stats")
async def get_rag_stats():
    """Get vector store statistics (row counts, backend type)."""
    try:
        result = await mcp_client.call_tool(
            "plex_rag",
            {"operation": "status"},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}
    else:
        return result


@router.post("/sync")
async def post_rag_sync(operation: str = "sync_metadata") -> dict:
    """
    Start indexing Plex metadata or subtitles into the RAG vector store (background task).
    Poll GET /sync/status for phase, library name, and document counts.
    """
    global _sync_task

    async def run_sync(op: str) -> None:
        try:
            result = await mcp_client.call_tool(
                "plex_rag",
                {"operation": op},
            )
            if not result.get("success", True):
                prog = get_rag_sync_progress()
                if prog.get("phase") != "error":
                    report_rag_sync_error(str(result.get("error", "Sync failed")))
        except Exception as e:
            logger.exception("RAG %s task failed", op)
            prog = get_rag_sync_progress()
            if prog.get("phase") != "error":
                report_rag_sync_error(str(e))

    async with _sync_lock:
        if _sync_task is not None and not _sync_task.done():
            return JSONResponse(
                {
                    "success": False,
                    "already_running": True,
                    "error": "A reindex is already in progress.",
                },
                status_code=409,
            )
        _sync_task = asyncio.create_task(run_sync(operation))

    return {
        "success": True,
        "started": True,
        "operation": operation,
        "error": None,
    }


@router.post("/sync/subtitles")
async def post_rag_sync_subtitles():
    """Convenience endpoint to start subtitle sync."""
    return await post_rag_sync(operation="sync_subtitles")


@router.get("/semantic")
async def get_rag_semantic(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    index: str = Query("metadata", enum=["metadata", "subtitles"]),
):
    """
    Semantic search over indexed Plex metadata or subtitles (LanceDB).
    index='metadata' targets plex_media table.
    index='subtitles' targets plex_subtitles table.
    """
    op = "semantic_search" if index == "metadata" else "search_subtitles"
    try:
        result = await mcp_client.call_tool(
            "plex_rag",
            {"operation": op, "query": query, "limit": limit},
        )
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "error_code": "RAG_ERROR",
            "results": [],
        }
    else:
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
    library_id: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
):
    """Retrieve Plex search results as context string for LLM (light RAG)."""
    from ..utils.errors import handle_mcp_error

    try:
        result = await mcp_client.call_tool(
            "plex_search",
            {"operation": "search", "query": query, "library_id": library_id, "limit": limit},
        )
    except Exception as e:
        raise handle_mcp_error(e) from e
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

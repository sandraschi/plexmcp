"""
PlexMCP RAG Portmanteau Tool

Semantic search and ingestion for Plex Media.
"""

from typing import Any, Literal

from ...app import mcp
from ...services.rag_ingestor import PlexIngestor, report_rag_sync_error, reset_rag_sync_progress
from ...utils import get_logger
from .search import _get_plex_service

logger = get_logger(__name__)


@mcp.tool()
async def plex_rag(
    operation: Literal["semantic_search", "sync_metadata"],
    query: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """
    RAG integration for Plex Media. Semantic search over movie, show, and music (artist) descriptions.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates neural search and metadata vectorization into a single tool to manage the
    lifecycle of the local knowledge base.

    OPERATIONS:
    - semantic_search: Natural language search across indexed Plex content using neural embeddings.
    - sync_metadata: Extract and vectorize metadata into the local LanceDB store.

    Returns:
    FastMCP 3.1+ dialogic response with top semantic matches and sync status.
    Enables natural language discovery and contextual media recommendations.
    """
    try:
        plex = _get_plex_service()
        ingestor = PlexIngestor(plex)

        if not ingestor.is_available:
            reset_rag_sync_progress()
            err = (
                "RAG Core dependencies not found. "
                "Install in-repo RAG: pip install plex-mcp-advanced[rag] "
                "(or add mcp-central-docs src to PYTHONPATH for shared vector store)."
            )
            report_rag_sync_error(err)
            return {
                "success": False,
                "error": err,
                "error_code": "RAG_NOT_AVAILABLE",
            }

        if operation == "sync_metadata":
            count = await ingestor.extract_and_index_all()
            return {
                "success": True,
                "operation": "sync_metadata",
                "indexed_count": count,
                "message": f"Successfully synced {count} media items into RAG vector store.",
            }

        elif operation == "semantic_search":
            if not query:
                return {
                    "success": False,
                    "error": "query is required for semantic_search operation",
                    "error_code": "MISSING_PARAMETER",
                }

            results = ingestor.semantic_search(query, limit=limit)
            return {
                "success": True,
                "operation": "semantic_search",
                "query": query,
                "results": results,
                "count": len(results),
            }

        elif operation == "status":
            stats = ingestor.get_stats()
            return {
                "success": True,
                "operation": "status",
                "data": stats,
                "message": f"RAG Status: {stats.get('count', 0)} items indexed using {stats.get('backend', 'unknown')} backend.",
            }

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        logger.error(f"Error in plex_rag operation '{operation}': {e}", exc_info=True)
        if operation == "sync_metadata":
            report_rag_sync_error(str(e))
        return {"success": False, "error": str(e), "error_code": "RAG_EXECUTION_ERROR"}

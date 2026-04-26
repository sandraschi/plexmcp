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
    operation: Literal["semantic_search", "sync_metadata", "sync_subtitles", "search_subtitles", "status"],
    query: str | None = None,
    limit: int = 5,
    enrich: bool = False,
    media_id: str | None = None,
    library_id: str | None = None,
) -> dict[str, Any]:
    """
    RAG integration for Plex Media. Semantic search and metadata enrichment.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates neural search, metadata vectorization, and external high-value
    discovery (Wikipedia) into a single tool to manage the knowledge lifecycle.

    OPERATIONS:
    - semantic_search: Natural language search across indexed Plex metadata (Title, Plot, etc.).
    - search_subtitles: Semantic search across indexed dialogue/subtitles for deep content discovery.
    - sync_metadata: Extract and vectorize core metadata into the local store.
    - sync_subtitles: Download, parse, and index subtitle tracks for semantic dialogue search.
    - status: Check the health and document counts of RAG indices.

    ENRICHMENT (sync_metadata only):
    When 'enrich' is True, the system fetches deep contextual summaries from Wikipedia
    for each item and appends it to the vector index. This significantly improves
    semantic search accuracy for historical or thematic queries.

    FILTERING (sync operations):
    - media_id: Sync subtitles/metadata only for a specific Plex item.
    - library_id: Sync subtitles/metadata only for a specific library.

    Returns:
    FastMCP 3.1+ dialogic response with top semantic matches and sync status.
    """
    try:
        plex = _get_plex_service()
        ingestor = PlexIngestor(plex)

        if not ingestor.is_available:
            reset_rag_sync_progress()
            err = (
                "RAG Core dependencies not found. "
                "Install in-repo RAG: pip install plex-mcp-advanced[rag] "
                "(or add mcp-central-docs src to PYTHONPATH)."
            )
            report_rag_sync_error(err)
            return {
                "success": False,
                "error": err,
                "error_code": "RAG_NOT_AVAILABLE",
            }

        if operation == "sync_metadata":
            count = await ingestor.extract_and_index_all(enrich=enrich)
            return {
                "success": True,
                "operation": "sync_metadata",
                "indexed_count": count,
                "enriched": enrich,
                "message": f"Successfully synced {count} media items into RAG vector store {'with Wikipedia enrichment' if enrich else ''}.",
            }

        if operation == "semantic_search":
            if not query:
                return {
                    "success": False,
                    "error": "query is required for semantic_search operation",
                    "error_code": "MISSING_PARAMETER",
                }

            results = ingestor.semantic_search(query, limit=limit, table="plex_media")
            return {
                "success": True,
                "operation": "semantic_search",
                "query": query,
                "results": results,
                "count": len(results),
            }

        if operation == "search_subtitles":
            if not query:
                return {
                    "success": False,
                    "error": "query is required for search_subtitles operation",
                    "error_code": "MISSING_PARAMETER",
                }

            results = ingestor.semantic_search(query, limit=limit, table="plex_subtitles")
            return {
                "success": True,
                "operation": "search_subtitles",
                "query": query,
                "results": results,
                "count": len(results),
            }

        if operation == "sync_subtitles":
            count = await ingestor.sync_subtitles(library_id=library_id, media_id=media_id)
            return {
                "success": True,
                "operation": "sync_subtitles",
                "indexed_count": count,
                "target": f"media_id={media_id}" if media_id else (f"library_id={library_id}" if library_id else "all"),
                "message": f"Successfully indexed {count} subtitle chunks.",
            }

        if operation == "status":
            stats = ingestor.get_stats()
            return {
                "success": True,
                "operation": "status",
                "data": stats,
                "message": f"RAG Status: {stats.get('count', 0)} items indexed using {stats.get('backend', 'unknown')} backend.",
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Use one of: semantic_search, sync_metadata, status"],
        }

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.error(
            f"Error in plex_rag operation '{operation}': {error_msg}",
            exc_info=not is_unauthorized,
        )

        if operation == "sync_metadata":
            report_rag_sync_error(error_msg)

        suggestions = [
            "Check Plex server is running and accessible",
            "Verify your server URL and token in settings",
        ]

        if is_unauthorized:
            suggestions = [
                "Update your PLEX_TOKEN in settings",
                "Visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return {
            "success": False,
            "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
            "error_code": "AUTH_FAILURE" if is_unauthorized else "RAG_EXECUTION_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

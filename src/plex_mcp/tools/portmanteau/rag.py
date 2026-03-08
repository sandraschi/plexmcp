"""
PlexMCP RAG Portmanteau Tool

Semantic search and ingestion for Plex Media.
"""

from typing import Any, Literal

from ...app import mcp
from ...services.rag_ingestor import PlexIngestor
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

    Operations:
    - semantic_search: Natural language semantic search across indexed Plex content.
      Requires `query`. Returns best matches.
    - sync_metadata: Indexes Plex metadata from movies, shows, and music (artist) libraries
      into LanceDB (title, plot/summary, genres, directors; artist summaries). Data from Plex API.
    """
    try:
        plex = _get_plex_service()
        ingestor = PlexIngestor(plex)

        if not ingestor.is_available:
            return {
                "success": False,
                "error": "RAG Core dependencies not found.",
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

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        logger.error(f"Error in plex_rag operation '{operation}': {e}", exc_info=True)
        return {"success": False, "error": str(e), "error_code": "RAG_EXECUTION_ERROR"}

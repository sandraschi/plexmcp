"""
PlexMCP Advanced Search Portmanteau Tool

Consolidates all search-related operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Any, Literal

from fastmcp.tools import ToolResult

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)

# In-memory storage for recent searches and saved searches
_recent_searches: list[dict[str, Any]] = []
_saved_searches: dict[str, dict[str, Any]] = {}


def _get_plex_service():
    """Get PlexService instance with proper environment variable handling."""
    from ...services.plex_service import PlexService

    base_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    token = os.getenv("PLEX_TOKEN")

    if not token:
        raise RuntimeError(
            "PLEX_TOKEN environment variable is required. "
            "Get your token from Plex Web App (Settings -> Account -> Authorized Devices) "
            "or visit https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ "
            "for detailed instructions."
        )

    return PlexService(base_url=base_url, token=token)


@mcp.tool()
async def plex_search(
    operation: Literal["search", "advanced_search", "suggest", "recent_searches", "save_search"],
    query: str | None = None,
    library_id: str | None = None,
    media_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
    title: str | None = None,
    year: int | list[int] | str | None = None,
    decade: int | None = None,
    genre: str | list[str] | None = None,
    actor: str | list[str] | None = None,
    director: str | list[str] | None = None,
    content_rating: str | list[str] | None = None,
    studio: str | list[str] | None = None,
    country: str | list[str] | None = None,
    language: str | list[str] | None = None,
    collection: str | list[str] | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    unwatched: bool | None = None,
    sort_by: str = "titleSort",
    sort_dir: str = "asc",
    search_name: str | None = None,
    max_recent: int = 10,
    summary_contains: str | None = None,
) -> ToolResult:
    """
    Comprehensive search management tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 5 search modalities (text, advanced, suggest, history, persistence)
    into one tool to provide a unified discovery interface for all media types.

    OPERATIONS:
    - search: Keyword-based text search across libraries.
    - advanced_search: Multi-parameter Boolean filtering (genre, year, actor, etc.).
    - suggest: Partial query autocomplete and suggestions.
    - recent_searches: Retrieve recent session search history.
    - save_search: Persist complex filters for future recall.

    Returns:
    FastMCP 3.1+ dialogic response with visual Prefab rendering where applicable.
    """
    try:
        plex = _get_plex_service()

        if operation == "search":
            if not query and not summary_contains:
                return {
                    "success": False,
                    "error": "query or summary_contains is required for search operation",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": [
                        "Provide a search query string",
                        "Or use summary_contains to search within plot summaries",
                    ],
                }

            # Track recent search
            _recent_searches.insert(
                0,
                {
                    "query": query,
                    "library_id": library_id,
                    "media_type": media_type,
                    "summary_contains": summary_contains,
                    "timestamp": None,
                },
            )
            if len(_recent_searches) > 100:
                _recent_searches.pop()

            # If only summary_contains is provided (no query), search with broader criteria
            if summary_contains and not query:
                search_term = summary_contains.lower()
                all_items = []

                if library_id:
                    # Get all items from specific library
                    result = await plex.get_library_items(library_id=library_id, limit=1000)
                    all_items = result.get("items", [])
                else:
                    # Search across all movie/show libraries
                    libraries = await plex.get_libraries()
                    for lib in libraries:
                        # Only search movie and show libraries for summary
                        if lib.get("type") in ("movie", "show"):
                            try:
                                result = await plex.get_library_items(
                                    library_id=str(lib.get("id")),
                                    limit=500,
                                )
                                all_items.extend(result.get("items", []))
                            except Exception:
                                continue  # Skip libraries that fail

                # Filter by summary - items are dicts from get_library_items
                results = [
                    item
                    for item in all_items
                    if item.get("summary") and search_term in item.get("summary", "").lower()
                ][:limit]
            else:
                results = await plex.search_media(query=query, limit=limit, library_id=library_id)

                # Filter by summary if specified
                if summary_contains and isinstance(results, list):
                    search_term = summary_contains.lower()
                    results = [
                        item
                        for item in results
                        if item.summary and search_term in item.summary.lower()
                    ]

            return ToolResult(
                body={
                    "success": True,
                    "operation": "search",
                    "query": query,
                    "summary_filter": summary_contains,
                    "results": results,
                    "count": len(results) if isinstance(results, list) else 0,
                    "limit": limit,
                    "offset": offset,
                },
                prefabs=["plex_media_browser"],
            )

        elif operation == "advanced_search":
            if not query and not title and not genre and not actor:
                return {
                    "success": False,
                    "error": "At least one search criterion (query, title, genre, actor, etc.) is required",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide at least one search filter"],
                }

            # Track recent search
            search_params = {
                "query": query,
                "title": title,
                "genre": genre,
                "actor": actor,
                "director": director,
                "year": year,
                "library_id": library_id,
                "media_type": media_type,
                "timestamp": None,
            }
            _recent_searches.insert(0, search_params)
            if len(_recent_searches) > 100:
                _recent_searches.pop()

            results = await plex.search_media(
                query=query,
                limit=limit,
                offset=offset,
                library_id=library_id,
                media_type=media_type,
                title=title,
                year=year,
                decade=decade,
                genre=genre,
                actor=actor,
                director=director,
                content_rating=content_rating,
                studio=studio,
                country=country,
                language=language,
                collection=collection,
                min_rating=min_rating,
                max_rating=max_rating,
                min_year=min_year,
                max_year=max_year,
                unwatched=unwatched,
                sort_by=sort_by,
                sort_dir=sort_dir,
            )
            return ToolResult(
                content={
                    "success": True,
                    "operation": "advanced_search",
                    "results": results,
                    "count": results.get("total", 0) if isinstance(results, dict) else 0,
                    "limit": limit,
                    "offset": offset,
                },
                meta={"prefabs": ["plex_media_browser"]},
            )

        elif operation == "suggest":
            if not query:
                return {
                    "success": False,
                    "error": "query is required for suggest operation",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide a partial search query"],
                }

            # Use search with limit=1 to get suggestions
            suggestions = await plex.search_media(
                query=query, limit=min(limit, 10), library_id=library_id
            )
            return {
                "success": True,
                "operation": "suggest",
                "query": query,
                "suggestions": suggestions[:10] if isinstance(suggestions, list) else [],
                "count": len(suggestions) if isinstance(suggestions, list) else 0,
            }

        elif operation == "recent_searches":
            recent = _recent_searches[:max_recent]
            return {
                "success": True,
                "operation": "recent_searches",
                "searches": recent,
                "count": len(recent),
            }

        elif operation == "save_search":
            if not search_name:
                return {
                    "success": False,
                    "error": "search_name is required for save_search operation",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide a name for the saved search"],
                }

            if not query and not title and not genre and not actor:
                return {
                    "success": False,
                    "error": "At least one search criterion is required to save a search",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide search parameters to save"],
                }

            saved_search = {
                "name": search_name,
                "query": query,
                "title": title,
                "genre": genre,
                "actor": actor,
                "director": director,
                "year": year,
                "library_id": library_id,
                "media_type": media_type,
                "min_rating": min_rating,
                "max_rating": max_rating,
                "min_year": min_year,
                "max_year": max_year,
                "unwatched": unwatched,
                "sort_by": sort_by,
                "sort_dir": sort_dir,
            }
            _saved_searches[search_name] = saved_search

            return {
                "success": True,
                "operation": "save_search",
                "saved_search": saved_search,
                "message": f"Search '{search_name}' saved successfully",
            }

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use one of: search, advanced_search, suggest, recent_searches, save_search"
                ],
            }

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg
        
        logger.error(
            f"Error in plex_search operation '{operation}': {error_msg}",
            exc_info=not is_unauthorized,
        )
        
        suggestions = [
            "Check Plex server is running and accessible",
            "Verify your server URL and token in settings",
            "Check server logs for detailed error information",
        ]
        
        if is_unauthorized:
            suggestions = [
                "Update your PLEX_TOKEN in settings",
                "Verify your token hasn't expired",
                "Visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return {
            "success": False,
            "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
            "error_code": "AUTH_FAILURE" if is_unauthorized else "EXECUTION_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

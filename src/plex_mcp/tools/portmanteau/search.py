"""
PlexMCP Advanced Search Portmanteau Tool

Consolidates all search-related operations into a single comprehensive interface.
"""

import os
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...prefabs import build_media_browser
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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_search(
    operation: Annotated[
        Literal["search", "advanced_search", "suggest", "recent_searches", "save_search"],
        Field(description="The search operation to perform."),
    ],
    query: Annotated[str | None, Field(description="Search query string for keyword-based searches.")] = None,
    library_id: Annotated[str | None, Field(description="ID of the library to search within.")] = None,
    media_type: Annotated[str | None, Field(description="Filter by media type (movie, episode, track).")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return.", ge=1)] = 100,
    offset: Annotated[int, Field(description="Number of results to skip for pagination.", ge=0)] = 0,
    title: Annotated[str | None, Field(description="Filter by exact or partial title.")] = None,
    year: Annotated[int | list[int] | str | None, Field(description="Filter by release year or list of years.")] = None,
    decade: Annotated[int | None, Field(description="Filter by decade (e.g. 1990 for 1990s).")] = None,
    genre: Annotated[str | list[str] | None, Field(description="Filter by genre name or list.")] = None,
    actor: Annotated[str | list[str] | None, Field(description="Filter by actor name or list.")] = None,
    director: Annotated[str | list[str] | None, Field(description="Filter by director name or list.")] = None,
    content_rating: Annotated[
        str | list[str] | None, Field(description="Filter by content rating (PG-13, R, etc.) or list.")
    ] = None,
    studio: Annotated[str | list[str] | None, Field(description="Filter by studio name or list.")] = None,
    country: Annotated[str | list[str] | None, Field(description="Filter by country of origin or list.")] = None,
    language: Annotated[str | list[str] | None, Field(description="Filter by audio language or list.")] = None,
    collection: Annotated[str | list[str] | None, Field(description="Filter by collection name or list.")] = None,
    min_rating: Annotated[float | None, Field(description="Minimum rating threshold (0.0-10.0).")] = None,
    max_rating: Annotated[float | None, Field(description="Maximum rating threshold (0.0-10.0).")] = None,
    min_year: Annotated[int | None, Field(description="Minimum release year.")] = None,
    max_year: Annotated[int | None, Field(description="Maximum release year.")] = None,
    unwatched: Annotated[bool | None, Field(description="Filter to only unwatched items.")] = None,
    sort_by: Annotated[str, Field(description="Sort field (titleSort, year, rating, etc.).")] = "titleSort",
    sort_dir: Annotated[str, Field(description="Sort direction: asc or desc.")] = "asc",
    search_name: Annotated[str | None, Field(description="Name to save the search under for future recall.")] = None,
    max_recent: Annotated[int, Field(description="Maximum number of recent searches to return.", ge=1)] = 10,
    summary_contains: Annotated[str | None, Field(description="Filter items whose summary contains this text.")] = None,
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

    ## Return Format
    {"success": bool, "data": dict|list, "operation": str, "count": int}

    ## Examples
    await plex_search(operation="search", query="star wars")
    await plex_search(operation="advanced_search", genre="comedy", year=2020)
    await plex_search(operation="suggest", query="incept")
    """
    try:
        plex = _get_plex_service()

        if operation == "search":
            if not query and not summary_contains:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "query or summary_contains is required for search operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": [
                            "Provide a search query string",
                            "Or use summary_contains to search within plot summaries",
                        ],
                    },
                )

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
                    item for item in all_items if item.get("summary") and search_term in item.get("summary", "").lower()
                ][:limit]
            else:
                results = await plex.search_media(query=query, limit=limit, library_id=library_id)

                # Filter by summary if specified
                if summary_contains and isinstance(results, list):
                    search_term = summary_contains.lower()
                    results = [item for item in results if item.summary and search_term in item.summary.lower()]

            # Convert MediaItem models to dicts before passing to prefab builder
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in results]
            from ...utils.summarize import summarize_items

            return ToolResult(
                content=summarize_items(data, "result"),
                structured_content=build_media_browser(data),
                meta={"prefabs": ["plex_media_browser"]},
            )

        if operation == "advanced_search":
            if not query and not title and not genre and not actor:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "At least one search criterion (query, title, genre, actor, etc.) is required",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide at least one search filter"],
                    },
                )

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
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in results]
            from ...utils.summarize import summarize_items

            return ToolResult(
                content=summarize_items(data, "result"),
                structured_content=build_media_browser(data),
                meta={"prefabs": ["plex_media_browser"]},
            )

        if operation == "suggest":
            if not query:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "query is required for suggest operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide a partial search query"],
                    },
                )

            # Use search with limit=1 to get suggestions
            suggestions = await plex.search_media(query=query, limit=min(limit, 10), library_id=library_id)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "suggest",
                    "query": query,
                    "suggestions": suggestions[:10] if isinstance(suggestions, list) else [],
                    "count": len(suggestions) if isinstance(suggestions, list) else 0,
                },
            )

        if operation == "recent_searches":
            recent = _recent_searches[:max_recent]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "recent_searches",
                    "searches": recent,
                    "count": len(recent),
                },
            )

        if operation == "save_search":
            if not search_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "search_name is required for save_search operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide a name for the saved search"],
                    },
                )

            if not query and not title and not genre and not actor:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "At least one search criterion is required to save a search",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide search parameters to save"],
                    },
                )

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

            return ToolResult(
                content={
                    "success": True,
                    "operation": "save_search",
                    "saved_search": saved_search,
                    "message": f"Search '{search_name}' saved successfully",
                },
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": ["Use one of: search, advanced_search, suggest, recent_searches, save_search"],
            },
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
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

        return ToolResult(
            content={
                "success": False,
                "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
                "error_code": "AUTH_FAILURE" if is_unauthorized else "EXECUTION_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            },
        )

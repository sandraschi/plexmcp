"""
PlexMCP Media Management Portmanteau Tool

Consolidates all media-related operations into a single comprehensive interface.
"""

import os
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...prefabs import build_media_browser, build_media_detail
from ...utils import get_logger

logger = get_logger(__name__)


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
async def plex_media(
    operation: Annotated[
        Literal["browse", "search", "get_details", "get_recent", "update_metadata"],
        Field(description="The media operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="ID of the library to browse or search within.")] = None,
    media_key: Annotated[
        str | None, Field(description="Key of the specific media item for detail or update operations.")
    ] = None,
    query: Annotated[str | None, Field(description="Search query string for text-based searches.")] = None,
    media_type: Annotated[str | None, Field(description="Filter by media type (movie, episode, track).")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return.", ge=1)] = 100,
    offset: Annotated[int, Field(description="Number of results to skip for pagination.", ge=0)] = 0,
    genre: Annotated[str | None, Field(description="Filter by genre name.")] = None,
    year: Annotated[int | None, Field(description="Filter by release year.")] = None,
    actor: Annotated[str | None, Field(description="Filter by actor name.")] = None,
    director: Annotated[str | None, Field(description="Filter by director name.")] = None,
    min_rating: Annotated[float | None, Field(description="Minimum rating filter (0.0-10.0).")] = None,
    unwatched: Annotated[bool | None, Field(description="Filter to only unwatched items.")] = None,
    metadata: Annotated[
        dict[str, Any] | None, Field(description="Metadata fields to update (title, year, summary, etc.).")
    ] = None,
) -> ToolResult:
    """
    Comprehensive media management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates media browsing, advanced searching, and metadata updates into a single tool.
    Optimizes for discovery and detail retrieval across all library types.

    OPERATIONS:
    - browse: Browse library contents with optional filtering.
    - search: Advanced search across libraries with multiple filters.
    - get_details: Get comprehensive details about a specific media item.
    - get_recent: Get recently added media items.
    - update_metadata: Update metadata (title, year, summary) for an item.

    ## Return Format
    {"success": bool, "data": dict|list, "operation": str, "count": int}

    ## Examples
    await plex_media(operation="browse", library_id="1")
    await plex_media(operation="search", query="inception")
    await plex_media(operation="get_details", media_key="12345")
    """
    try:
        plex = _get_plex_service()

        # Operation: browse
        if operation == "browse":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for browse operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": [
                            "Use plex_library('list') to find available library IDs",
                            "Provide library_id parameter: plex_media('browse', library_id='1')",
                        ],
                        "related_tools": ["plex_library"],
                    },
                )

            # Use search_media with empty query to simulate browse, passing all filters
            filter_kwargs: dict[str, Any] = {}
            if genre:
                filter_kwargs["genre"] = genre
            if year:
                filter_kwargs["year"] = year
            if actor:
                filter_kwargs["actor"] = actor
            if director:
                filter_kwargs["director"] = director
            if min_rating is not None:
                filter_kwargs["min_rating"] = min_rating
            if unwatched is not None:
                filter_kwargs["unwatched"] = unwatched
            if media_type:
                filter_kwargs["media_type"] = media_type
            items = await plex.search_media("", limit=limit, offset=offset, library_id=library_id, **filter_kwargs)
            raw_data = items.data if hasattr(items, "data") else items
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in raw_data]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "browse",
                    "data": data,
                    "count": len(data),
                    "limit": limit,
                    "offset": offset,
                },
                meta={"prefabs": ["plex_media_browser"]},
                structured_content=build_media_browser(data),
            )

        # Operation: search
        if operation == "search":
            if not query:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "query is required for search operation",
                        "error_code": "MISSING_QUERY",
                    },
                )

            filter_kwargs: dict[str, Any] = {}
            if genre:
                filter_kwargs["genre"] = genre
            if year:
                filter_kwargs["year"] = year
            if actor:
                filter_kwargs["actor"] = actor
            if director:
                filter_kwargs["director"] = director
            if min_rating is not None:
                filter_kwargs["min_rating"] = min_rating
            if unwatched is not None:
                filter_kwargs["unwatched"] = unwatched
            if media_type:
                filter_kwargs["media_type"] = media_type
            items = await plex.search_media(query, limit=limit, offset=offset, library_id=library_id, **filter_kwargs)
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "search",
                    "data": data,
                    "count": len(data),
                    "limit": limit,
                    "offset": offset,
                },
                meta={"prefabs": ["plex_media_browser"]},
                structured_content=build_media_browser(data),
            )

        # Operation: get_details
        if operation == "get_details":
            if not media_key:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "media_key is required for get_details operation",
                        "error_code": "MISSING_MEDIA_KEY",
                        "suggestions": [
                            "Get media_key from browse or search results",
                            "Example: plex_media('get_details', media_key='12345')",
                        ],
                        "related_tools": ["plex_media with browse or search operation"],
                    },
                )

            details = await plex.get_media_info(media_key)
            return ToolResult(
                content={"success": True, "operation": "get_details", "data": details},
                meta={"prefabs": ["plex_media_detail"]},
                structured_content=build_media_detail(details or {}),
            )

        # Operation: get_recent
        if operation == "get_recent":
            items = await plex.get_recently_added(library_id=library_id, limit=limit)
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_recent",
                    "data": data,
                    "count": len(data),
                    "limit": limit,
                },
                meta={"prefabs": ["plex_media_browser"]},
                structured_content=build_media_browser(data),
            )

        # Operation: update_metadata
        if operation == "update_metadata":
            if not media_key:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "media_key is required for update_metadata operation",
                        "error_code": "MISSING_MEDIA_KEY",
                        "suggestions": ["Get media_key from browse or search results"],
                    },
                )

            if not metadata:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "metadata dictionary is required for update_metadata operation",
                        "error_code": "MISSING_METADATA",
                        "suggestions": [
                            "Provide metadata dict: {'title': 'New Title', 'year': 2020}",
                            "Available fields: title, year, summary, rating, genres, etc.",
                        ],
                    },
                )

            # Update metadata via plex service
            updated = await plex.update_media_metadata(media_key, metadata)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "update_metadata",
                    "data": updated,
                    "media_key": media_key,
                    "updated_fields": list(metadata.keys()),
                },
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: browse, search, get_details, get_recent, update_metadata",
                    f"You provided: '{operation}'",
                ],
            },
        )

    except RuntimeError as e:
        error_msg = str(e)
        suggestions = []

        if "PLEX_TOKEN" in error_msg:
            suggestions = [
                "Set PLEX_TOKEN environment variable",
                "Get token from: Plex Web App -> Settings -> Account -> Authorized Devices",
                "Or visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]
        elif "not found" in error_msg.lower():
            suggestions = [
                "Verify the ID/key is correct",
                "Use plex_media('browse') or plex_media('search') to find valid items",
                "Check that the library/item still exists",
            ]
        elif "connection" in error_msg.lower():
            suggestions = [
                "Verify Plex Media Server is running",
                "Check PLEX_SERVER_URL is correct (default: http://localhost:32400)",
                "Test server access in web browser",
            ]

        return ToolResult(
            content={
                "success": False,
                "error": error_msg,
                "error_code": "RUNTIME_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            },
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
            f"Error in plex_media operation '{operation}': {error_msg}",
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
                "error_code": "AUTH_FAILURE" if is_unauthorized else "UNEXPECTED_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            },
        )

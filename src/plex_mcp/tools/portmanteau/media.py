"""
PlexMCP Media Management Portmanteau Tool

Consolidates all media-related operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Any, Literal

from fastmcp.tools import ToolResult

from ...app import mcp
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


@mcp.tool()
async def plex_media(
    operation: Literal["browse", "search", "get_details", "get_recent", "update_metadata"],
    library_id: str | None = None,
    media_key: str | None = None,
    query: str | None = None,
    media_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
    genre: str | None = None,
    year: int | None = None,
    actor: str | None = None,
    director: str | None = None,
    min_rating: float | None = None,
    unwatched: bool | None = None,
    metadata: dict[str, Any] | None = None,
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

    Returns:
    FastMCP 3.1+ dialogic response with visual Prefab rendering where applicable.
    """
    try:
        plex = _get_plex_service()

        # Operation: browse
        if operation == "browse":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for browse operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": [
                        "Use plex_library('list') to find available library IDs",
                        "Provide library_id parameter: plex_media('browse', library_id='1')",
                    ],
                    "related_tools": ["plex_library"],
                }

            # Use search_media with empty query to simulate browse
            items = await plex.search_media("", limit=limit, offset=offset, library_id=library_id)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "browse",
                    "data": (items.data if hasattr(items, "data") else items),
                    "count": len(items.data if hasattr(items, "data") else items),
                    "limit": limit,
                    "offset": offset,
                },
                meta={"prefabs": ["plex_media_browser"]},
            )

        # Operation: search
        if operation == "search":
            if not query:
                return {
                    "success": False,
                    "error": "query is required for search operation",
                    "error_code": "MISSING_QUERY",
                }

            items = await plex.search_media(query, limit=limit, offset=offset, library_id=library_id)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "search",
                    "data": [item.dict() if hasattr(item, "dict") else item for item in items],
                    "count": len(items),
                    "limit": limit,
                    "offset": offset,
                },
                meta={"prefabs": ["plex_media_browser"]},
            )

        # Operation: get_details
        if operation == "get_details":
            if not media_key:
                return {
                    "success": False,
                    "error": "media_key is required for get_details operation",
                    "error_code": "MISSING_MEDIA_KEY",
                    "suggestions": [
                        "Get media_key from browse or search results",
                        "Example: plex_media('get_details', media_key='12345')",
                    ],
                    "related_tools": ["plex_media with browse or search operation"],
                }

            details = await plex.get_media_info(media_key)
            return ToolResult(
                content={"success": True, "operation": "get_details", "data": details},
                meta={"prefabs": ["plex_media_detail"]},
            )

        # Operation: get_recent
        if operation == "get_recent":
            items = await plex.get_recently_added(library_id=library_id, limit=limit)
            return ToolResult(
                structured_content={
                    "success": True,
                    "operation": "get_recent",
                    "data": [item.dict() if hasattr(item, "dict") else item for item in items],
                    "count": len(items),
                    "limit": limit,
                },
                meta={"prefabs": ["plex_media_browser"]},
            )

        # Operation: update_metadata
        if operation == "update_metadata":
            if not media_key:
                return {
                    "success": False,
                    "error": "media_key is required for update_metadata operation",
                    "error_code": "MISSING_MEDIA_KEY",
                    "suggestions": ["Get media_key from browse or search results"],
                }

            if not metadata:
                return {
                    "success": False,
                    "error": "metadata dictionary is required for update_metadata operation",
                    "error_code": "MISSING_METADATA",
                    "suggestions": [
                        "Provide metadata dict: {'title': 'New Title', 'year': 2020}",
                        "Available fields: title, year, summary, rating, genres, etc.",
                    ],
                }

            # Update metadata via plex service
            updated = await plex.update_media_metadata(media_key, metadata)
            return {
                "success": True,
                "operation": "update_metadata",
                "data": updated,
                "media_key": media_key,
                "updated_fields": list(metadata.keys()),
            }

        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'",
            "error_code": "INVALID_OPERATION",
            "suggestions": [
                "Valid operations: browse, search, get_details, get_recent, update_metadata",
                f"You provided: '{operation}'",
            ],
        }

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

        return {
            "success": False,
            "error": error_msg,
            "error_code": "RUNTIME_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.error(
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

        return {
            "success": False,
            "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
            "error_code": "AUTH_FAILURE" if is_unauthorized else "UNEXPECTED_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

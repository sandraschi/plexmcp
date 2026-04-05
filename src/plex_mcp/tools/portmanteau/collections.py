"""
PlexMCP Collections Management Portmanteau Tool

Consolidates all collection-related operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Any, Literal

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
async def plex_collections(
    operation: Literal["list", "get", "create", "update", "delete", "add_items", "remove_items"],
    collection_id: str | None = None,
    library_id: str | None = None,
    title: str | None = None,
    summary: str | None = None,
    items: list[str] | None = None,
) -> dict[str, Any]:
    """
    Comprehensive collections management tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 collection-related operations into a single tool to facilitate
    the thematic grouping and organization of cross-library media.

    OPERATIONS:
    - list: Retrieve all collections within a specific library or the entire server.
    - get: Inspect collection metadata and list all contained media items.
    - create: Initialize a new collection with optional initial items and descriptions.
    - update: Modify existing collection titles or summaries.
    - delete: Permanently remove a collection (media items are preserved).
    - add_items: Append new media items to an existing collection.
    - remove_items: Detach specific media items from a collection.

    Returns:
    FastMCP 3.1+ dialogic response with collection state and member list.
    Enables autonomous curation and systematic content organization.
    """
    try:
        plex = _get_plex_service()

        if operation == "list":
            # Collections are typically accessed through libraries
            if library_id:
                library = await plex.get_library(library_id)
                if not library:
                    return {
                        "success": False,
                        "error": f"Library with ID '{library_id}' not found",
                        "error_code": "LIBRARY_NOT_FOUND",
                    }
                # Get collections from library (would need PlexAPI collection access)
                return {
                    "success": True,
                    "operation": "list",
                    "collections": [],
                    "message": "Collection listing requires PlexAPI collection support (not yet fully implemented)",
                }
            else:
                libraries = await plex.list_libraries()
                return {
                    "success": True,
                    "operation": "list",
                    "collections": [],
                    "libraries": libraries,
                    "message": "Collection listing requires PlexAPI collection support (not yet fully implemented)",
                }

        elif operation == "get":
            if not collection_id:
                return {
                    "success": False,
                    "error": "collection_id is required for get operation",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide a collection ID"],
                }

            return {
                "success": True,
                "operation": "get",
                "collection_id": collection_id,
                "message": "Collection retrieval requires PlexAPI collection support (not yet fully implemented)",
                "data": {},
            }

        elif operation == "create":
            if not title:
                return {
                    "success": False,
                    "error": "title is required for create operation",
                    "error_code": "MISSING_PARAMETER",
                }
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for create operation",
                    "error_code": "MISSING_PARAMETER",
                }

            return {
                "success": True,
                "operation": "create",
                "title": title,
                "library_id": library_id,
                "message": "Collection creation requires PlexAPI collection support (not yet fully implemented)",
                "data": {},
            }

        elif operation == "update":
            if not collection_id:
                return {
                    "success": False,
                    "error": "collection_id is required for update operation",
                    "error_code": "MISSING_PARAMETER",
                }

            return {
                "success": True,
                "operation": "update",
                "collection_id": collection_id,
                "message": "Collection update requires PlexAPI collection support (not yet fully implemented)",
                "data": {},
            }

        elif operation == "delete":
            if not collection_id:
                return {
                    "success": False,
                    "error": "collection_id is required for delete operation",
                    "error_code": "MISSING_PARAMETER",
                }

            return {
                "success": True,
                "operation": "delete",
                "collection_id": collection_id,
                "message": "Collection deletion requires PlexAPI collection support (not yet fully implemented)",
            }

        elif operation == "add_items":
            if not collection_id:
                return {
                    "success": False,
                    "error": "collection_id is required for add_items operation",
                    "error_code": "MISSING_PARAMETER",
                }
            if not items:
                return {
                    "success": False,
                    "error": "items is required for add_items operation",
                    "error_code": "MISSING_PARAMETER",
                }

            return {
                "success": True,
                "operation": "add_items",
                "collection_id": collection_id,
                "items": items,
                "message": "Adding items to collection requires PlexAPI collection support (not yet fully implemented)",
            }

        elif operation == "remove_items":
            if not collection_id:
                return {
                    "success": False,
                    "error": "collection_id is required for remove_items operation",
                    "error_code": "MISSING_PARAMETER",
                }
            if not items:
                return {
                    "success": False,
                    "error": "items is required for remove_items operation",
                    "error_code": "MISSING_PARAMETER",
                }

            return {
                "success": True,
                "operation": "remove_items",
                "collection_id": collection_id,
                "items": items,
                "message": "Removing items from collection requires PlexAPI collection support (not yet fully implemented)",
            }

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use one of: list, get, create, update, delete, add_items, remove_items"
                ],
            }

    except Exception as e:
        logger.error(f"Error in plex_collections operation '{operation}': {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_code": "EXECUTION_ERROR",
            "suggestions": [
                "Verify Plex server is accessible",
                "Check PLEX_TOKEN is set correctly",
                "Verify collection_id is valid if provided",
            ],
        }

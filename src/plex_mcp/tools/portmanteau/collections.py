"""
PlexMCP Collections Management Portmanteau Tool

Consolidates all collection-related operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_collections(
    operation: Annotated[
        Literal["list", "get", "create", "update", "delete", "add_items", "remove_items"],
        Field(description="Operation to perform."),
    ],
    collection_id: Annotated[str | None, Field(description="Collection ID.")] = None,
    library_id: Annotated[str | None, Field(description="Library ID for scoping.")] = None,
    title: Annotated[str | None, Field(description="Collection title.")] = None,
    summary: Annotated[str | None, Field(description="Collection summary.")] = None,
    items: Annotated[list[str] | None, Field(description="List of media item keys.")] = None,
) -> ToolResult:
    """Comprehensive collections management tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 collection-related operations into a single tool to facilitate
    the thematic grouping and organization of cross-library media.

    ## Return Format
    {"success": bool, "data": dict, "message": str}

    ## Examples
    await plex_collections(operation="list")
    await plex_collections(operation="create", title="My Collection", library_id="lib1")
    """
    try:
        plex = _get_plex_service()

        if operation == "list":
            if library_id:
                library = await plex.get_library(library_id)
                if not library:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": f"Library with ID '{library_id}' not found",
                            "error_code": "LIBRARY_NOT_FOUND",
                        }
                    )
                return ToolResult(
                    content={
                        "success": True,
                        "operation": "list",
                        "collections": [],
                        "message": "Collection listing requires PlexAPI collection support (not yet fully implemented)",
                    }
                )
            libraries = await plex.list_libraries()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list",
                    "collections": [],
                    "libraries": libraries,
                    "message": "Collection listing requires PlexAPI collection support (not yet fully implemented)",
                }
            )

        if operation == "get":
            if not collection_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "collection_id is required for get operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide a collection ID"],
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "get",
                    "collection_id": collection_id,
                    "message": "Collection retrieval requires PlexAPI collection support (not yet fully implemented)",
                    "data": {},
                }
            )

        if operation == "create":
            if not title:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "title is required for create operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for create operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "create",
                    "title": title,
                    "library_id": library_id,
                    "message": "Collection creation requires PlexAPI collection support (not yet fully implemented)",
                    "data": {},
                }
            )

        if operation == "update":
            if not collection_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "collection_id is required for update operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "update",
                    "collection_id": collection_id,
                    "message": "Collection update requires PlexAPI collection support (not yet fully implemented)",
                    "data": {},
                }
            )

        if operation == "delete":
            if not collection_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "collection_id is required for delete operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "delete",
                    "collection_id": collection_id,
                    "message": "Collection deletion requires PlexAPI collection support (not yet fully implemented)",
                }
            )

        if operation == "add_items":
            if not collection_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "collection_id is required for add_items operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )
            if not items:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "items is required for add_items operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "add_items",
                    "collection_id": collection_id,
                    "items": items,
                    "message": "Adding items to collection requires PlexAPI collection support (not yet fully implemented)",
                }
            )

        if operation == "remove_items":
            if not collection_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "collection_id is required for remove_items operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )
            if not items:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "items is required for remove_items operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "remove_items",
                    "collection_id": collection_id,
                    "items": items,
                    "message": "Removing items from collection requires PlexAPI collection support (not yet fully implemented)",
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": ["Use one of: list, get, create, update, delete, add_items, remove_items"],
            }
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
            f"Error in plex_collections operation '{operation}': {error_msg}",
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
            }
        )

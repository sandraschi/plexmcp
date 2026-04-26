"""
PlexMCP Library Management Portmanteau Tool

Consolidates all library-related operations into a single comprehensive interface.
FastMCP 2.14.3 compliant with conversational tool returns and sampling capabilities.
"""

from typing import Literal

from fastmcp.tools import ToolResult

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)


def _get_plex_service():
    """Get PlexService instance with proper environment variable handling."""
    from ...config import get_settings
    from ...services.plex_service import PlexService

    settings = get_settings()

    if not settings.plex_token:
        raise RuntimeError(
            "PLEX_TOKEN environment variable is required. "
            "Get your token from Plex Web App (Settings > Account > Authorized Devices) "
            "or visit https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ "
            "for detailed instructions."
        )

    return PlexService(base_url=settings.server_url, token=settings.plex_token, timeout=settings.timeout)


@mcp.tool()
async def plex_library(
    operation: Literal[
        "list",
        "get",
        "create",
        "update",
        "delete",
        "scan",
        "refresh",
        "optimize",
        "empty_trash",
        "add_location",
        "remove_location",
        "clean_bundles",
    ],
    library_id: str | None = None,
    name: str | None = None,
    library_type: Literal["movie", "show", "music", "photo"] | None = None,
    path: str | None = None,
    agent: str | None = None,
    scanner: str | None = None,
    language: str | None = "en",
    thumb: str | None = None,
    force: bool = False,
) -> ToolResult:
    """
    Comprehensive library management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 12+ library-related operations into a single tool to prevent tool explosion.
    Simplifies library lifecycle management (CRUD, scan, optimize) for agents.

    OPERATIONS:
    - list: List all media libraries.
    - get: Get detailed information about a specific library.
    - create/update/delete: Manage library existence and settings.
    - scan/refresh: Update media index and metadata.
    - optimize/empty_trash/clean_bundles: Maintain library database health.
    - add_location/remove_location: Manage physical media paths.

    Returns:
    FastMCP 3.1+ dialogic response with visual Prefab rendering where applicable.
    """
    try:
        plex = _get_plex_service()

        # Operation: list
        if operation == "list":
            libraries = await plex.get_libraries()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list",
                    "data": libraries,
                    "count": len(libraries),
                },
                meta={"prefabs": ["plex_library_grid"]},
            )

        # Operation: get
        if operation == "get":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for get operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Use plex_library('list') to find available library IDs"],
                }

            library = await plex.get_library(library_id)
            if library is None:
                return {
                    "success": False,
                    "error": f"Library {library_id} not found",
                    "error_code": "LIBRARY_NOT_FOUND",
                    "suggestions": [
                        "Use plex_library(operation='list') to find available library IDs",
                        "Verify the library_id is correct",
                    ],
                }
            return ToolResult(
                structured_content={"success": True, "operation": "get", "data": library},
                meta={"prefabs": ["plex_library_detail"]},
            )

        # Operation: scan
        if operation == "scan":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for scan operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to scan"],
                }

            result = await plex.scan_library(library_id, force=force)
            return {
                "success": result.get("scan_successful", False),
                "operation": "scan",
                "library_id": library_id,
                "force": force,
                "data": result,
            }

        # Operation: refresh
        if operation == "refresh":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for refresh operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to refresh"],
                }

            result = await plex.refresh_library_metadata(library_id)
            return {
                "success": result,
                "operation": "refresh",
                "library_id": library_id,
                "data": {"refreshed": result},
            }

        # Operation: empty_trash
        if operation == "empty_trash":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for empty_trash operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to empty trash"],
                }

            result = await plex.empty_trash(library_id)
            return {
                "success": result,
                "operation": "empty_trash",
                "library_id": library_id,
                "data": {"trash_emptied": result},
            }

        # Operation: create
        if operation == "create":
            if not name:
                return {
                    "success": False,
                    "error": "name is required for create operation",
                    "error_code": "MISSING_NAME",
                    "suggestions": ["Provide name parameter for the new library"],
                }
            if not library_type:
                return {
                    "success": False,
                    "error": "library_type is required for create operation",
                    "error_code": "MISSING_LIBRARY_TYPE",
                    "suggestions": ["Provide library_type: movie, show, music, or photo"],
                }
            if not path:
                return {
                    "success": False,
                    "error": "path is required for create operation",
                    "error_code": "MISSING_PATH",
                    "suggestions": ["Provide path parameter for the media folder"],
                }

            result = await plex.add_library(
                name=name,
                libtype=library_type,
                agent=agent or "com.plexapp.agents.imdb",
                scanner=scanner or "Plex Movie Scanner",
                language=language or "en",
                location=path,
                thumb=thumb,
            )
            if result is None:
                return {
                    "success": False,
                    "error": "Library creation not fully supported via Plex API",
                    "error_code": "NOT_SUPPORTED",
                    "suggestions": [
                        "Use Plex Web App to create libraries manually",
                        "The Plex API has limited support for programmatic library creation",
                    ],
                }
            return {
                "success": True,
                "operation": "create",
                "data": result,
            }

        # Operation: update
        if operation == "update":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for update operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to update"],
                }

            update_kwargs = {}
            if name:
                update_kwargs["name"] = name
            if agent:
                update_kwargs["agent"] = agent
            if scanner:
                update_kwargs["scanner"] = scanner
            if language:
                update_kwargs["language"] = language
            if thumb:
                update_kwargs["thumb"] = thumb

            if not update_kwargs:
                return {
                    "success": False,
                    "error": "At least one update field (name, agent, scanner, language, thumb) is required",
                    "error_code": "MISSING_UPDATE_FIELDS",
                    "suggestions": ["Provide at least one field to update"],
                }

            result = await plex.update_library(library_id, **update_kwargs)
            if result is None:
                return {
                    "success": False,
                    "error": f"Failed to update library {library_id}",
                    "error_code": "UPDATE_FAILED",
                    "suggestions": [
                        "Verify library_id is correct",
                        "Check that you have admin permissions",
                        "Verify the library exists",
                    ],
                }
            return {
                "success": True,
                "operation": "update",
                "library_id": library_id,
                "data": result,
            }

        # Operation: delete
        if operation == "delete":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for delete operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to delete"],
                }

            result = await plex.delete_library(library_id)
            return {
                "success": result,
                "operation": "delete",
                "library_id": library_id,
                "data": {"deleted": result},
            }

        # Operation: optimize
        if operation == "optimize":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for optimize operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to optimize"],
                }

            result = await plex.optimize_library(library_id)
            return {
                "success": result,
                "operation": "optimize",
                "library_id": library_id,
                "data": {"optimized": result},
            }

        # Operation: add_location
        if operation == "add_location":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for add_location operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to add location"],
                }
            if not path:
                return {
                    "success": False,
                    "error": "path is required for add_location operation",
                    "error_code": "MISSING_PATH",
                    "suggestions": ["Provide path parameter for the new location"],
                }

            result = await plex.add_library_location(library_id, path)
            return {
                "success": result,
                "operation": "add_location",
                "library_id": library_id,
                "path": path,
                "data": {"location_added": result},
            }

        # Operation: remove_location
        if operation == "remove_location":
            if not library_id:
                return {
                    "success": False,
                    "error": "library_id is required for remove_location operation",
                    "error_code": "MISSING_LIBRARY_ID",
                    "suggestions": ["Provide library_id to remove location"],
                }
            if not path:
                return {
                    "success": False,
                    "error": "path is required for remove_location operation",
                    "error_code": "MISSING_PATH",
                    "suggestions": ["Provide path parameter for the location to remove"],
                }

            result = await plex.remove_library_location(library_id, path)
            return {
                "success": result,
                "operation": "remove_location",
                "library_id": library_id,
                "path": path,
                "data": {"location_removed": result},
            }

        # Operation: clean_bundles
        if operation == "clean_bundles":
            result = await plex.clean_bundles(library_id=library_id)
            return {
                "success": result.get("cleaned", False),
                "operation": "clean_bundles",
                "library_id": library_id,
                "data": result,
            }

        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'",
            "error_code": "INVALID_OPERATION",
            "suggestions": [
                "Valid operations: list, get, create, update, delete, scan, refresh, optimize, empty_trash, add_location, remove_location, clean_bundles",
                f"You provided: '{operation}'",
            ],
        }

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.error(
            f"Error in plex_library operation '{operation}': {error_msg}",
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

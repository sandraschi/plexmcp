"""
PlexMCP Library Management Portmanteau Tool

Consolidates all library-related operations into a single comprehensive interface.
"""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...prefabs import build_library_detail, build_library_grid
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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def plex_library(
    operation: Annotated[
        Literal[
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
            "list_items",
        ],
        Field(description="The library operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="ID of the target library section.")] = None,
    name: Annotated[str | None, Field(description="Name for the new or updated library.")] = None,
    library_type: Annotated[
        Literal["movie", "show", "music", "photo"] | None, Field(description="Type of media library to create.")
    ] = None,
    path: Annotated[str | None, Field(description="Filesystem path to add or remove as a library location.")] = None,
    agent: Annotated[
        str | None, Field(description="Plex metadata agent identifier (e.g. com.plexapp.agents.imdb).")
    ] = None,
    scanner: Annotated[str | None, Field(description="Plex scanner identifier (e.g. Plex Movie Scanner).")] = None,
    language: Annotated[str | None, Field(description="Language code for the library metadata.")] = None,
    thumb: Annotated[str | None, Field(description="URL or path for the library thumbnail.")] = None,
    force: Annotated[bool, Field(description="Force operations like scan even if already up to date.")] = False,
    limit: Annotated[int, Field(description="Max items to return for list_items.", ge=1)] = 50,
    offset: Annotated[int, Field(description="Pagination offset for list_items.", ge=0)] = 0,
    sort: Annotated[str | None, Field(description="Sort field for list_items (title, rating, year, added).")] = None,
    media_type: Annotated[
        str | None, Field(description="Filter by media type for list_items (movie, show, episode, track, photo).")
    ] = None,
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
    - list_items: List paginated library contents with sort and type filters.

    ## Return Format
    {"success": bool, "data": dict|list, "operation": str, "count": int}

    ## Examples
    await plex_library(operation="list")
    await plex_library(operation="get", library_id="1")
    await plex_library(operation="scan", library_id="1", force=True)
    await plex_library(operation="list_items", library_id="1", sort="title", media_type="movie")
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
                structured_content=build_library_grid(libraries),
                meta={"prefabs": ["plex_library_grid"]},
            )

        # Operation: get
        if operation == "get":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for get operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Use plex_library('list') to find available library IDs"],
                    },
                )

            library = await plex.get_library(library_id)
            if library is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": f"Library {library_id} not found",
                        "error_code": "LIBRARY_NOT_FOUND",
                        "suggestions": [
                            "Use plex_library(operation='list') to find available library IDs",
                            "Verify the library_id is correct",
                        ],
                    },
                )
            return ToolResult(
                content={"success": True, "operation": "get", "data": library},
                structured_content=build_library_detail(library),
                meta={"prefabs": ["plex_library_detail"]},
            )

        # Operation: scan
        if operation == "scan":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for scan operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to scan"],
                    },
                )

            result = await plex.scan_library(library_id, force=force)
            return ToolResult(
                content={
                    "success": result.get("scan_successful", False),
                    "message": result.get("message", "Scan triggered"),
                    "next_steps": result.get("next_steps", []),
                    "operation": "scan",
                    "library_id": library_id,
                    "force": force,
                    "data": result,
                },
            )

        # Operation: refresh
        if operation == "refresh":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for refresh operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to refresh"],
                    },
                )

            result = await plex.refresh_library_metadata(library_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "refresh",
                    "library_id": library_id,
                    "data": {"refreshed": result},
                },
            )

        # Operation: empty_trash
        if operation == "empty_trash":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for empty_trash operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to empty trash"],
                    },
                )

            result = await plex.empty_trash(library_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "empty_trash",
                    "library_id": library_id,
                    "data": {"trash_emptied": result},
                },
            )

        # Operation: create
        if operation == "create":
            if not name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "name is required for create operation",
                        "error_code": "MISSING_NAME",
                        "suggestions": ["Provide name parameter for the new library"],
                    },
                )
            if not library_type:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_type is required for create operation",
                        "error_code": "MISSING_LIBRARY_TYPE",
                        "suggestions": ["Provide library_type: movie, show, music, or photo"],
                    },
                )
            if not path:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "path is required for create operation",
                        "error_code": "MISSING_PATH",
                        "suggestions": ["Provide path parameter for the media folder"],
                    },
                )

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
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Library creation not fully supported via Plex API",
                        "error_code": "NOT_SUPPORTED",
                        "suggestions": [
                            "Use Plex Web App to create libraries manually",
                            "The Plex API has limited support for programmatic library creation",
                        ],
                    },
                )
            return ToolResult(
                content={
                    "success": True,
                    "operation": "create",
                    "data": result,
                },
            )

        # Operation: update
        if operation == "update":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for update operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to update"],
                    },
                )

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
                return ToolResult(
                    content={
                        "success": False,
                        "error": "At least one update field (name, agent, scanner, language, thumb) is required",
                        "error_code": "MISSING_UPDATE_FIELDS",
                        "suggestions": ["Provide at least one field to update"],
                    },
                )

            result = await plex.update_library(library_id, **update_kwargs)
            if result is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": f"Failed to update library {library_id}",
                        "error_code": "UPDATE_FAILED",
                        "suggestions": [
                            "Verify library_id is correct",
                            "Check that you have admin permissions",
                            "Verify the library exists",
                        ],
                    },
                )
            return ToolResult(
                content={
                    "success": True,
                    "operation": "update",
                    "library_id": library_id,
                    "data": result,
                },
            )

        # Operation: delete
        if operation == "delete":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for delete operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to delete"],
                    },
                )

            result = await plex.delete_library(library_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "delete",
                    "library_id": library_id,
                    "data": {"deleted": result},
                },
            )

        # Operation: optimize
        if operation == "optimize":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for optimize operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to optimize"],
                    },
                )

            result = await plex.optimize_library(library_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "optimize",
                    "library_id": library_id,
                    "data": {"optimized": result},
                },
            )

        # Operation: add_location
        if operation == "add_location":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for add_location operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to add location"],
                    },
                )
            if not path:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "path is required for add_location operation",
                        "error_code": "MISSING_PATH",
                        "suggestions": ["Provide path parameter for the new location"],
                    },
                )

            result = await plex.add_library_location(library_id, path)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "add_location",
                    "library_id": library_id,
                    "path": path,
                    "data": {"location_added": result},
                },
            )

        # Operation: remove_location
        if operation == "remove_location":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for remove_location operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to remove location"],
                    },
                )
            if not path:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "path is required for remove_location operation",
                        "error_code": "MISSING_PATH",
                        "suggestions": ["Provide path parameter for the location to remove"],
                    },
                )

            result = await plex.remove_library_location(library_id, path)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "remove_location",
                    "library_id": library_id,
                    "path": path,
                    "data": {"location_removed": result},
                },
            )

        # Operation: clean_bundles
        if operation == "clean_bundles":
            result = await plex.clean_bundles(library_id=library_id)
            return ToolResult(
                content={
                    "success": result.get("cleaned", False),
                    "message": result.get("message", "Clean bundles completed"),
                    "next_steps": result.get("next_steps", []),
                    "operation": "clean_bundles",
                    "library_id": library_id,
                    "data": result,
                },
            )

        # Operation: list_items
        if operation == "list_items":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for list_items operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id to list items"],
                    },
                )

            from ...services.plex_media_service import PlexMediaService

            media_service = PlexMediaService(plex)
            items = await media_service.search_media(
                "",
                limit=limit or 50,
                offset=offset,
                library_id=library_id,
                sort=sort,
                media_type=media_type,
            )
            data = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_items",
                    "library_id": library_id,
                    "data": data,
                    "count": len(data),
                    "limit": limit,
                    "offset": offset,
                    "sort": sort,
                    "media_type": media_type,
                    "has_more": len(data) >= limit,
                },
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: list, get, create, update, delete, scan, refresh, optimize, empty_trash, add_location, remove_location, clean_bundles, list_items",
                    f"You provided: '{operation}'",
                ],
            },
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
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

        return ToolResult(
            content={
                "success": False,
                "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
                "error_code": "AUTH_FAILURE" if is_unauthorized else "EXECUTION_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            },
        )

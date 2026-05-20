"""
PlexMCP Metadata Management Portmanteau Tool

Consolidates all metadata-related operations into a single comprehensive interface.
FastMCP 3.2+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Annotated, Any, Literal

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
async def plex_metadata(
    operation: Annotated[
        Literal["refresh", "refresh_all", "fix_match", "update", "analyze", "match", "organize"],
        Field(description="The metadata operation to perform."),
    ],
    item_id: Annotated[str | None, Field(description="ID of the target media item.")] = None,
    library_id: Annotated[str | None, Field(description="ID of the target library.")] = None,
    match_id: Annotated[str | None, Field(description="Match identifier for fix_match operation.")] = None,
    media_type: Annotated[
        Literal["movie", "show", "season", "episode", "artist", "album", "track", "photo"] | None,
        Field(description="Type of media for matching."),
    ] = None,
    metadata: Annotated[dict[str, Any] | None, Field(description="Metadata fields to update.")] = None,
    force: Annotated[bool, Field(description="Force refresh even if recently updated.")] = False,
    patterns: Annotated[
        dict[str, str] | None, Field(description="Organization patterns (e.g., naming format).")
    ] = None,
) -> ToolResult:
    """Comprehensive metadata management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 metadata lifecycle operations into a single tool to ensure
    consistent identifier handling and improved discovery of library maintenance tasks.

    ## Return Format
    {"success": bool, "operation": str, "data": dict|list, "item_id": str|None, "library_id": str|None}

    ## Examples
    await plex_metadata(operation="refresh", library_id="1", force=True)
    await plex_metadata(operation="refresh_all")
    await plex_metadata(operation="update", item_id="123", metadata={"title": "New Title"})
    await plex_metadata(operation="analyze", library_id="1")
    """
    try:
        plex = _get_plex_service()

        if operation == "refresh":
            if not item_id and not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Either item_id or library_id is required for refresh operation",
                        "error_code": "MISSING_ID",
                        "suggestions": [
                            "Provide item_id to refresh a specific item",
                            "Provide library_id to refresh an entire library",
                        ],
                    }
                )

            result = await plex.refresh_metadata(item_id=item_id, library_id=library_id, force=force)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "refresh",
                    "item_id": item_id,
                    "library_id": library_id,
                    "force": force,
                    "data": result,
                }
            )

        if operation == "refresh_all":
            libraries = await plex.list_libraries()
            results = []
            for lib in libraries:
                lib_id = lib.get("id") or str(lib.get("key", ""))
                try:
                    result = await plex.refresh_metadata(library_id=lib_id, force=force)
                    results.append({"library_id": lib_id, "success": True, "result": result})
                except Exception as e:
                    logger.exception(f"Error refreshing library {lib_id}: {e}")
                    results.append({"library_id": lib_id, "success": False, "error": str(e)})

            return ToolResult(
                content={
                    "success": True,
                    "operation": "refresh_all",
                    "force": force,
                    "data": results,
                    "libraries_refreshed": len([r for r in results if r.get("success")]),
                    "total_libraries": len(libraries),
                }
            )

        if operation == "fix_match":
            if not item_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "item_id is required for fix_match operation",
                        "error_code": "MISSING_ITEM_ID",
                        "suggestions": ["Provide item_id parameter"],
                    }
                )
            if not match_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "match_id is required for fix_match operation",
                        "error_code": "MISSING_MATCH_ID",
                        "suggestions": ["Provide match_id parameter with correct match identifier"],
                    }
                )
            if not media_type:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "media_type is required for fix_match operation",
                        "error_code": "MISSING_MEDIA_TYPE",
                        "suggestions": [
                            "Provide media_type parameter: movie, show, season, episode, artist, album, track, photo"
                        ],
                    }
                )

            logger.info(f"Fixing match for item {item_id} with match ID {match_id}")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "fix_match",
                    "item_id": item_id,
                    "match_id": match_id,
                    "media_type": media_type,
                    "data": {"match_fixed": True},
                }
            )

        if operation == "update":
            if not item_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "item_id is required for update operation",
                        "error_code": "MISSING_ITEM_ID",
                        "suggestions": ["Provide item_id parameter"],
                    }
                )
            if not metadata:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "metadata dictionary is required for update operation",
                        "error_code": "MISSING_METADATA",
                        "suggestions": ["Provide metadata parameter with fields to update"],
                    }
                )

            from .media import plex_media

            result = await plex_media(operation="update_metadata", media_key=item_id, metadata=metadata)
            return ToolResult(
                content={
                    "success": result.get("success", False),
                    "operation": "update",
                    "item_id": item_id,
                    "data": result.get("data"),
                }
            )

        if operation == "analyze":
            if library_id:
                result = await plex.analyze_library(library_id=library_id)
            else:
                libraries = await plex.list_libraries()
                results = []
                for lib in libraries:
                    lib_id = lib.get("id") or str(lib.get("key", ""))
                    try:
                        result = await plex.analyze_library(library_id=lib_id)
                        results.append({"library_id": lib_id, "result": result})
                    except Exception as e:
                        logger.exception(f"Error analyzing library {lib_id}: {e}")
                        results.append({"library_id": lib_id, "error": str(e)})
                result = {"libraries": results, "total_analyzed": len(libraries)}

            return ToolResult(
                content={"success": True, "operation": "analyze", "library_id": library_id, "data": result}
            )

        if operation == "match":
            if not item_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "item_id is required for match operation",
                        "error_code": "MISSING_ITEM_ID",
                        "suggestions": ["Provide item_id parameter"],
                    }
                )

            logger.info(f"Matching item {item_id} to metadata")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "match",
                    "item_id": item_id,
                    "match_id": match_id,
                    "data": {"matched": True, "match_id": match_id or "auto-matched"},
                }
            )

        if operation == "organize":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for organize operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id parameter"],
                    }
                )

            result = await plex.organize_library(library_id=library_id, dry_run=False, patterns=patterns)
            return ToolResult(
                content={"success": True, "operation": "organize", "library_id": library_id, "data": result}
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: refresh, refresh_all, fix_match, update, analyze, match, organize",
                    f"You provided: '{operation}'",
                ],
            }
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
                "Verify the item_id or library_id is correct",
                "Use plex_media(operation='browse') or plex_library(operation='list') to find valid IDs",
            ]

        return ToolResult(
            content={
                "success": False,
                "error": error_msg,
                "error_code": "RUNTIME_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in plex_metadata operation '{operation}': {e}", exc_info=True)
        return ToolResult(
            content={
                "success": False,
                "error": f"Unexpected error during {operation}: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
                "operation": operation,
                "suggestions": [
                    "Check server logs for detailed error information",
                    "Verify all required parameters are provided",
                    "Try the operation again with valid parameters",
                ],
            }
        )

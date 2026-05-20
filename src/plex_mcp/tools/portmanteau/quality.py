"""
PlexMCP Quality Profiles Portmanteau Tool

Consolidates all quality profile management operations into a single comprehensive interface.
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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def plex_quality(
    operation: Annotated[
        Literal["list_profiles", "get_profile", "create_profile", "update_profile", "delete_profile", "set_default"],
        Field(description="The quality profile operation to perform."),
    ],
    profile_name: Annotated[str | None, Field(description="Name of the quality profile.")] = None,
    settings: Annotated[dict[str, Any] | None, Field(description="Quality profile settings dictionary.")] = None,
    is_default: Annotated[bool, Field(description="Set this profile as the system default.")] = False,
) -> ToolResult:
    """Comprehensive quality profile management tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 quality profile operations into a single tool to standardize
    transcoding rules and resolution limits across multiple devices.

    ## Return Format
    {"success": bool, "operation": str, "profile_name": str|None, "profiles": list|None, "settings": dict|None, "result": dict|None}

    ## Examples
    await plex_quality(operation="list_profiles")
    await plex_quality(operation="get_profile", profile_name="Remote")
    await plex_quality(operation="create_profile", profile_name="4K Limited", settings={"max_bitrate": 40000})
    await plex_quality(operation="delete_profile", profile_name="Old Profile")
    """
    try:
        plex = _get_plex_service()

        if operation == "list_profiles":
            profiles = await plex.list_quality_profiles()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_profiles",
                    "profiles": profiles,
                    "count": len(profiles) if isinstance(profiles, list) else 0,
                }
            )

        if operation == "get_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for get_profile operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Provide a profile name"],
                    }
                )

            settings = await plex.get_transcode_settings(profile_name=profile_name)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_profile",
                    "profile_name": profile_name,
                    "settings": settings,
                }
            )

        if operation == "create_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for create_profile operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )
            if not settings:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "settings is required for create_profile operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            result = await plex.create_quality_profile(name=profile_name, settings=settings, is_default=is_default)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "create_profile",
                    "profile_name": profile_name,
                    "is_default": is_default,
                    "result": result,
                }
            )

        if operation == "update_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for update_profile operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )
            if not settings:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "settings is required for update_profile operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            result = await plex.update_transcode_settings(profile_name=profile_name, settings=settings)
            return ToolResult(
                content={"success": True, "operation": "update_profile", "profile_name": profile_name, "result": result}
            )

        if operation == "delete_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for delete_profile operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            result = await plex.delete_quality_profile(profile_name=profile_name)
            return ToolResult(
                content={"success": True, "operation": "delete_profile", "profile_name": profile_name, "result": result}
            )

        if operation == "set_default":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for set_default operation",
                        "error_code": "MISSING_PARAMETER",
                    }
                )

            result = await plex.create_quality_profile(name=profile_name, settings={}, is_default=True)
            return ToolResult(
                content={"success": True, "operation": "set_default", "profile_name": profile_name, "result": result}
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use one of: list_profiles, get_profile, create_profile, update_profile, delete_profile, set_default"
                ],
            }
        )

    except Exception as e:
        logger.error(f"Error in plex_quality operation '{operation}': {e}", exc_info=True)
        return ToolResult(
            content={
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR",
                "suggestions": [
                    "Verify Plex server is accessible",
                    "Check PLEX_TOKEN is set correctly",
                    "Verify profile_name is valid if provided",
                    "Ensure you have admin permissions for create/update/delete operations",
                ],
            }
        )

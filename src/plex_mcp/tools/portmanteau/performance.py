"""
PlexMCP Performance & Quality Management Portmanteau Tool

Consolidates all performance, quality, transcoding, and server status operations into a single comprehensive interface.
"""

import os
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...prefabs import build_performance_dashboard
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
async def plex_performance(
    operation: Annotated[
        Literal[
            "get_transcode_settings",
            "update_transcode_settings",
            "get_transcoding_status",
            "get_bandwidth",
            "set_quality",
            "get_throttling",
            "set_throttling",
            "list_profiles",
            "create_profile",
            "delete_profile",
            "get_server_status",
            "get_server_info",
        ],
        Field(description="The performance operation to perform."),
    ],
    profile_name: Annotated[str | None, Field(description="Name of the quality profile to target.")] = None,
    settings: Annotated[
        dict[str, Any] | None, Field(description="Configuration dictionary for profile settings.")
    ] = None,
    quality: Annotated[str | None, Field(description="Stream quality setting (e.g., '1080p', '720p', '480p').")] = None,
    bitrate: Annotated[int | None, Field(description="Target bitrate in kbps for quality settings.")] = None,
    enabled: Annotated[bool | None, Field(description="Whether throttling should be enabled.")] = None,
    download_limit: Annotated[int | None, Field(description="Download rate limit in kbps.")] = None,
    upload_limit: Annotated[int | None, Field(description="Upload rate limit in kbps.")] = None,
    time_range: Annotated[
        str, Field(description="Time range for bandwidth stats (e.g., 'day', 'week', 'month').")
    ] = "day",
    is_default: Annotated[bool, Field(description="Whether the profile should be the default.")] = False,
) -> ToolResult:
    """
    Comprehensive performance, quality, and server status operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates transcoding settings, bandwidth monitoring, and server health into a single tool.

    OPERATIONS:
    - get_transcode_settings: Get current transcode settings for a quality profile.
    - update_transcode_settings: Update transcode settings for a quality profile.
    - get_transcoding_status: Get current transcoding status.
    - get_bandwidth: Get bandwidth usage statistics.
    - set_quality: Set streaming quality settings for a profile.
    - get_throttling: Get current throttling status for a profile.
    - set_throttling: Enable or disable throttling for a profile.
    - list_profiles: List all quality profiles.
    - create_profile: Create a new quality profile.
    - delete_profile: Delete a quality profile.
    - get_server_status: Get current server status and health.
    - get_server_info: Get combined server status and library info.

    ## Return Format
    {"success": bool, "operation": str, "data": dict | list, "error": str | None}

    ## Examples
    await plex_performance(operation="get_server_status")
    await plex_performance(operation="set_quality", profile_name="Remote", quality="1080p")
    await plex_performance(operation="list_profiles")
    """
    try:
        plex = _get_plex_service()

        # Operation: get_transcode_settings
        if operation == "get_transcode_settings":
            result = await plex.get_transcode_settings(profile_name=profile_name)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_transcode_settings",
                    "data": result,
                },
                meta={"prefabs": ["plex_performance_dashboard"]},
                structured_content=build_performance_dashboard(result),
            )

        # Operation: update_transcode_settings
        if operation == "update_transcode_settings":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for update_transcode_settings operation",
                        "error_code": "MISSING_PROFILE_NAME",
                        "suggestions": ["Provide profile_name parameter"],
                    }
                )
            if not settings:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "settings dictionary is required for update_transcode_settings operation",
                        "error_code": "MISSING_SETTINGS",
                        "suggestions": ["Provide settings parameter with configuration dictionary"],
                    }
                )

            result = await plex.update_transcode_settings(profile_name=profile_name, settings=settings)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "update_transcode_settings",
                    "profile_name": profile_name,
                    "data": {"updated": result},
                }
            )

        # Operation: get_transcoding_status
        if operation == "get_transcoding_status":
            result = await plex.get_transcoding_status()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_transcoding_status",
                    "data": result.model_dump() if hasattr(result, "model_dump") else result,
                }
            )

        # Operation: get_bandwidth
        if operation == "get_bandwidth":
            result = await plex.get_bandwidth_usage(time_range=time_range)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_bandwidth",
                    "time_range": time_range,
                    "data": result.model_dump() if hasattr(result, "model_dump") else result,
                }
            )

        # Operation: set_quality
        if operation == "set_quality":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for set_quality operation",
                        "error_code": "MISSING_PROFILE_NAME",
                        "suggestions": ["Provide profile_name parameter"],
                    }
                )
            if not quality:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "quality is required for set_quality operation",
                        "error_code": "MISSING_QUALITY",
                        "suggestions": ["Provide quality parameter (e.g., '1080p', '720p', '480p')"],
                    }
                )

            result = await plex.set_stream_quality(profile_name=profile_name, quality=quality, bitrate=bitrate)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "set_quality",
                    "profile_name": profile_name,
                    "quality": quality,
                    "data": {"quality_set": result},
                }
            )

        # Operation: get_throttling
        if operation == "get_throttling":
            result = await plex.get_throttling_status(profile_name=profile_name)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_throttling",
                    "data": result,
                }
            )

        # Operation: set_throttling
        if operation == "set_throttling":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for set_throttling operation",
                        "error_code": "MISSING_PROFILE_NAME",
                        "suggestions": ["Provide profile_name parameter"],
                    }
                )
            if enabled is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "enabled is required for set_throttling operation",
                        "error_code": "MISSING_ENABLED",
                        "suggestions": ["Provide enabled parameter (True or False)"],
                    }
                )

            result = await plex.set_throttling(
                profile_name=profile_name,
                enabled=enabled,
                download_limit=download_limit,
                upload_limit=upload_limit,
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "set_throttling",
                    "profile_name": profile_name,
                    "enabled": enabled,
                    "data": {"throttling_set": result},
                }
            )

        # Operation: list_profiles
        if operation == "list_profiles":
            result = await plex.list_quality_profiles()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_profiles",
                    "data": [p.model_dump() if hasattr(p, "model_dump") else p for p in result],
                    "count": len(result),
                }
            )

        # Operation: create_profile
        if operation == "create_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for create_profile operation",
                        "error_code": "MISSING_PROFILE_NAME",
                        "suggestions": ["Provide profile_name parameter"],
                    }
                )
            if not settings:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "settings dictionary is required for create_profile operation",
                        "error_code": "MISSING_SETTINGS",
                        "suggestions": ["Provide settings parameter with profile configuration"],
                    }
                )

            result = await plex.create_quality_profile(name=profile_name, settings=settings, is_default=is_default)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "create_profile",
                    "profile_name": profile_name,
                    "data": {"created": result},
                }
            )

        # Operation: delete_profile
        if operation == "delete_profile":
            if not profile_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "profile_name is required for delete_profile operation",
                        "error_code": "MISSING_PROFILE_NAME",
                        "suggestions": ["Provide profile_name parameter"],
                    }
                )

            result = await plex.delete_quality_profile(profile_name=profile_name)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "delete_profile",
                    "profile_name": profile_name,
                    "data": {"deleted": result},
                }
            )

        # Operation: get_server_status
        if operation == "get_server_status":
            status = await plex.get_server_status()
            status_data = status.model_dump() if hasattr(status, "model_dump") else status
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_server_status",
                    "data": status_data,
                },
                meta={"prefabs": ["plex_performance_dashboard"]},
                structured_content=build_performance_dashboard(status_data),
            )

        # Operation: get_server_info
        if operation == "get_server_info":
            # This combines get_server_status and list_libraries
            status = await plex.get_server_status()
            libraries = await plex.list_libraries()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "get_server_info",
                    "data": {
                        "status": status.model_dump() if hasattr(status, "model_dump") else status,
                        "libraries": libraries,
                    },
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: get_transcode_settings, update_transcode_settings, get_transcoding_status, "
                    "get_bandwidth, set_quality, get_throttling, set_throttling, list_profiles, create_profile, "
                    "delete_profile, get_server_status, get_server_info",
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
                "Verify the profile_name is correct",
                "Use plex_performance(operation='list_profiles') to find valid profile names",
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
        logger.error(
            f"Unexpected error in plex_performance operation '{operation}': {e}",
            exc_info=True,
        )
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

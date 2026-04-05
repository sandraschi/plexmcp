"""
PlexMCP Quality Profiles Portmanteau Tool

Consolidates all quality profile management operations into a single comprehensive interface.
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
async def plex_quality(
    operation: Literal[
        "list_profiles",
        "get_profile",
        "create_profile",
        "update_profile",
        "delete_profile",
        "set_default",
    ],
    profile_name: str | None = None,
    settings: dict[str, Any] | None = None,
    is_default: bool = False,
) -> dict[str, Any]:
    """
    Comprehensive quality profile management tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 quality profile operations into a single tool to standardize
    transcoding rules and resolution limits across multiple devices.

    OPERATIONS:
    - list_profiles: Retrieve all custom and system quality profiles.
    - get_profile: Inspect transcode bitrates and resolution settings.
    - create_profile: Define a new profile with specific bandwidth constraints.
    - update_profile: Modify existing profile parameters.
    - delete_profile: Remove obsolete quality profiles.
    - set_default: Assign a global default for automatic transcode selections.

    Returns:
    FastMCP 3.1+ dialogic response with transcode policy and profile details.
    Enables autonomous bandwidth management and resolution optimization.
    """
    try:
        plex = _get_plex_service()

        if operation == "list_profiles":
            profiles = await plex.list_quality_profiles()
            return {
                "success": True,
                "operation": "list_profiles",
                "profiles": profiles,
                "count": len(profiles) if isinstance(profiles, list) else 0,
            }

        elif operation == "get_profile":
            if not profile_name:
                return {
                    "success": False,
                    "error": "profile_name is required for get_profile operation",
                    "error_code": "MISSING_PARAMETER",
                    "suggestions": ["Provide a profile name"],
                }

            settings = await plex.get_transcode_settings(profile_name=profile_name)
            return {
                "success": True,
                "operation": "get_profile",
                "profile_name": profile_name,
                "settings": settings,
            }

        elif operation == "create_profile":
            if not profile_name:
                return {
                    "success": False,
                    "error": "profile_name is required for create_profile operation",
                    "error_code": "MISSING_PARAMETER",
                }
            if not settings:
                return {
                    "success": False,
                    "error": "settings is required for create_profile operation",
                    "error_code": "MISSING_PARAMETER",
                }

            result = await plex.create_quality_profile(
                name=profile_name, settings=settings, is_default=is_default
            )
            return {
                "success": True,
                "operation": "create_profile",
                "profile_name": profile_name,
                "is_default": is_default,
                "result": result,
            }

        elif operation == "update_profile":
            if not profile_name:
                return {
                    "success": False,
                    "error": "profile_name is required for update_profile operation",
                    "error_code": "MISSING_PARAMETER",
                }
            if not settings:
                return {
                    "success": False,
                    "error": "settings is required for update_profile operation",
                    "error_code": "MISSING_PARAMETER",
                }

            result = await plex.update_transcode_settings(
                profile_name=profile_name, settings=settings
            )
            return {
                "success": True,
                "operation": "update_profile",
                "profile_name": profile_name,
                "result": result,
            }

        elif operation == "delete_profile":
            if not profile_name:
                return {
                    "success": False,
                    "error": "profile_name is required for delete_profile operation",
                    "error_code": "MISSING_PARAMETER",
                }

            result = await plex.delete_quality_profile(profile_name=profile_name)
            return {
                "success": True,
                "operation": "delete_profile",
                "profile_name": profile_name,
                "result": result,
            }

        elif operation == "set_default":
            if not profile_name:
                return {
                    "success": False,
                    "error": "profile_name is required for set_default operation",
                    "error_code": "MISSING_PARAMETER",
                }

            # Update profile to set as default
            result = await plex.create_quality_profile(
                name=profile_name, settings={}, is_default=True
            )
            return {
                "success": True,
                "operation": "set_default",
                "profile_name": profile_name,
                "result": result,
            }

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use one of: list_profiles, get_profile, create_profile, update_profile, delete_profile, set_default"
                ],
            }

    except Exception as e:
        logger.error(f"Error in plex_quality operation '{operation}': {e}", exc_info=True)
        return {
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

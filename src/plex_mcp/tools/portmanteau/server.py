"""
PlexMCP Server Management Portmanteau Tool

Consolidates all server management operations into a single comprehensive interface.
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
async def plex_server(
    operation: Literal[
        "status",
        "info",
        "health",
        "maintenance",
        "restart",
        "update",
    ],
    maintenance_operation: str | None = None,
    options: dict[str, Any] | None = None,
) -> ToolResult:
    """
    Comprehensive server management operations for Plex Media Server.

    Consolidates server lifecycle and maintenance operations into a single tool to prevent
    tool explosion and improve discoverability of admin-level tasks.

    OPERATIONS:
    - status: Current server availability and basic state.
    - info: Detailed server identity and library overview.
    - health: Real-time resource usage and health metrics.
    - maintenance: Trigger optimization, cleaning, and trash emptying.
    - restart: Trigger server restart (where supported by OS/wrapper).
    - update: Check and apply server software updates (where supported).

    Returns:
    FastMCP 3.1+ dialogic response with visual Prefab rendering where applicable.
    """
    try:
        plex = _get_plex_service()

        # Operation: status
        if operation == "status":
            status = await plex.get_server_status()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "status",
                    "data": status.dict() if hasattr(status, "dict") else status,
                },
                meta={"prefabs": ["plex_server_status"]},
            )

        # Operation: info
        elif operation == "info":
            status = await plex.get_server_status()
            libraries = await plex.list_libraries()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "info",
                    "data": {
                        "status": status.dict() if hasattr(status, "dict") else status,
                        "libraries": libraries,
                    },
                },
                meta={"prefabs": ["plex_server_info"]},
            )

        # Operation: health
        elif operation == "health":
            # Import admin service for health check
            from ...api.admin import get_server_health

            health_data = await get_server_health()
            return {
                "success": True,
                "operation": "health",
                "data": health_data,
            }

        # Operation: maintenance
        elif operation == "maintenance":
            if not maintenance_operation:
                return {
                    "success": False,
                    "error": "maintenance_operation is required for maintenance operation",
                    "error_code": "MISSING_MAINTENANCE_OPERATION",
                    "suggestions": [
                        "Provide maintenance_operation parameter",
                        "Valid values: optimize, clean_bundles, empty_trash, etc.",
                    ],
                }

            # Import admin service for maintenance
            from ...api.admin import run_server_maintenance

            result = await run_server_maintenance(
                operation=maintenance_operation, options=options or {}
            )
            return {
                "success": True,
                "operation": "maintenance",
                "maintenance_operation": maintenance_operation,
                "data": result.dict() if hasattr(result, "dict") else result,
            }

        # Operation: restart
        elif operation == "restart":
            # Note: Plex API may not support programmatic restart
            logger.warning("Server restart operation may not be fully supported by Plex API")
            return {
                "success": False,
                "error": "Server restart is not yet fully implemented",
                "error_code": "NOT_IMPLEMENTED",
                "suggestions": [
                    "Use Plex Web App or system service manager to restart the server",
                    "This operation may not be supported by the Plex API",
                ],
            }

        # Operation: update
        elif operation == "update":
            # Note: Plex API may not support programmatic updates
            logger.warning("Server update operation may not be fully supported by Plex API")
            return {
                "success": False,
                "error": "Server update is not yet fully implemented",
                "error_code": "NOT_IMPLEMENTED",
                "suggestions": [
                    "Use Plex Web App or system package manager to update the server",
                    "This operation may not be supported by the Plex API",
                ],
            }

        else:
            return {
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: status, info, health, maintenance, restart, update",
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
            f"Error in plex_server operation '{operation}': {error_msg}",
            exc_info=not is_unauthorized, # Minimize noise for auth errors
        )
        
        suggestions = [
            "Check server logs for detailed error information",
            "Verify all required parameters are provided",
            "Try the operation again with valid parameters",
        ]
        
        if is_unauthorized:
            suggestions = [
                "Update your PLEX_TOKEN in the settings",
                "Ensure the Plex server is reachable at the configured PLEX_URL",
                "Verify your token hasn't expired (Log out and in to Plex Web to refresh)",
                "Visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return {
            "success": False,
            "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else f"Unexpected error during {operation}: {error_msg}",
            "error_code": "AUTH_FAILURE" if is_unauthorized else "UNEXPECTED_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

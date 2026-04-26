"""
PlexMCP Streaming/Playback Control Portmanteau Tool

Consolidates all playback control and session management operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Literal

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
async def plex_streaming(
    operation: Literal[
        "list_sessions",
        "list_clients",
        "play",
        "pause",
        "stop",
        "seek",
        "skip_next",
        "skip_previous",
        "set_quality",
        "set_volume",
        "control",
    ],
    client_id: str | None = None,
    media_key: str | None = None,
    seek_to: int | None = None,
    offset: int | None = 30,
    action: str | None = None,
    volume: int | None = None,
    quality: str | None = None,
) -> ToolResult:
    """
    Comprehensive playback control and session management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates session monitoring, client discovery, and remote playback control into a single tool.
    Enables seamless media orchestration across the entire Plex ecosystem.

    OPERATIONS:
    - list_sessions: List all active sessions with client and playback details.
    - list_clients: List all available Plex clients for remote control.
    - play: Start media playback on a specific client (auto-selects if omitted).
    - pause/stop: Control current playback state on a client.
    - seek: Jump to a specific position (milliseconds) in the media.
    - skip_next/skip_previous: Navigate through the play queue.
    - set_volume: Adjust the playback volume (0-100) on a client.
    - control: Generic playback control for custom actions (e.g., step_forward).

    Returns:
    FastMCP 3.1+ dialogic response with visual Prefab rendering where applicable.
    """
    try:
        plex = _get_plex_service()

        # Operation: list_sessions
        if operation == "list_sessions":
            sessions = await plex.get_sessions()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_sessions",
                    "data": sessions,
                    "count": len(sessions) if isinstance(sessions, list) else 0,
                },
                meta={"prefabs": ["plex_streaming_session"]},
            )

        # Operation: list_clients
        if operation == "list_clients":
            clients = await plex.get_clients()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_clients",
                    "data": clients,
                    "count": len(clients) if isinstance(clients, list) else 0,
                },
                meta={"prefabs": ["plex_streaming_client"]},
            )

        # Operation: play (can auto-select client, so check before requiring client_id)
        if operation == "play":
            if not media_key:
                return {
                    "success": False,
                    "error": "media_key is required for play operation",
                    "error_code": "MISSING_MEDIA_KEY",
                    "suggestions": [
                        "Get media_key from plex_media(operation='browse') or plex_media(operation='search')",
                        "Provide media_key parameter",
                    ],
                }

            # Auto-select client if not provided
            if not client_id:
                # Get media type to select appropriate client
                media_type = await plex._run_in_executor(plex._get_media_type, media_key)
                if not media_type:
                    return {
                        "success": False,
                        "error": "Could not determine media type. Please provide client_id explicitly.",
                        "error_code": "MEDIA_TYPE_UNKNOWN",
                        "suggestions": [
                            "Provide client_id parameter explicitly",
                            "Use plex_streaming(operation='list_clients') to see available clients",
                        ],
                    }

                # Get all clients
                all_clients = await plex.get_clients()
                if not all_clients:
                    return {
                        "success": False,
                        "error": "No clients available",
                        "error_code": "NO_CLIENTS",
                        "suggestions": [
                            "Ensure at least one Plex client is open and connected",
                            "Try plex_streaming(operation='list_clients') to check available clients",
                        ],
                    }

                # Select best client for this media type
                selected_client = await plex._run_in_executor(plex._select_client_for_media, media_type, all_clients)
                if not selected_client:
                    return {
                        "success": False,
                        "error": "Could not select appropriate client",
                        "error_code": "CLIENT_SELECTION_FAILED",
                        "suggestions": [
                            "Provide client_id parameter explicitly",
                            f"Available clients: {[c.get('name') for c in all_clients]}",
                        ],
                    }

                client_id = selected_client.get("machineIdentifier") or selected_client.get("id")
                logger.info(
                    f"Auto-selected client '{selected_client.get('name')}' ({selected_client.get('product')}) for {media_type} media"
                )

            result = await plex.control_playback(
                client_identifier=client_id,
                action="play",
                media_key=media_key,
            )
            return {
                "success": result,
                "operation": "play",
                "client_id": client_id,
                "media_key": media_key,
                "data": {"played": result},
            }

        # All other operations require client_id
        if not client_id:
            return {
                "success": False,
                "error": f"client_id is required for {operation} operation",
                "error_code": "MISSING_CLIENT_ID",
                "suggestions": [
                    "Use plex_streaming(operation='list_clients') to find available client IDs",
                    f"Provide client_id parameter: plex_streaming(operation='{operation}', client_id='...')",
                ],
            }

        # Operation: pause
        if operation == "pause":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="pause",
            )
            return {
                "success": result,
                "operation": "pause",
                "client_id": client_id,
                "data": {"paused": result},
            }

        # Operation: stop
        if operation == "stop":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="stop",
            )
            return {
                "success": result,
                "operation": "stop",
                "client_id": client_id,
                "data": {"stopped": result},
            }

        # Operation: seek
        if operation == "seek":
            if seek_to is None:
                return {
                    "success": False,
                    "error": "seek_to is required for seek operation",
                    "error_code": "MISSING_SEEK_TO",
                    "suggestions": ["Provide seek_to parameter (position in milliseconds)"],
                }

            result = await plex.control_playback(
                client_identifier=client_id,
                action="seek_to",
                seek_to=seek_to,
            )
            return {
                "success": result,
                "operation": "seek",
                "client_id": client_id,
                "seek_to": seek_to,
                "data": {"seeked": result},
            }

        # Operation: skip_next
        if operation == "skip_next":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="skip_next",
            )
            return {
                "success": result,
                "operation": "skip_next",
                "client_id": client_id,
                "data": {"skipped": result},
            }

        # Operation: skip_previous
        if operation == "skip_previous":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="skip_previous",
            )
            return {
                "success": result,
                "operation": "skip_previous",
                "client_id": client_id,
                "data": {"skipped": result},
            }

        # Operation: set_quality
        if operation == "set_quality":
            if not quality:
                return {
                    "success": False,
                    "error": "quality is required for set_quality operation",
                    "error_code": "MISSING_QUALITY",
                    "suggestions": ["Provide quality parameter (e.g., '1080p', '720p', '480p')"],
                }

            # Note: Plex API may have limited support for quality settings
            # This is a placeholder implementation
            return {
                "success": False,
                "error": "set_quality operation is not yet fully implemented",
                "error_code": "NOT_IMPLEMENTED",
                "suggestions": [
                    "Use plex_performance tool for quality profile management",
                    "Quality settings may need to be configured via Plex Web App",
                ],
            }

        # Operation: set_volume
        if operation == "set_volume":
            if not client_id:
                return {
                    "success": False,
                    "error": "client_id is required for set_volume operation",
                    "error_code": "MISSING_CLIENT_ID",
                }
            if volume is None:
                return {
                    "success": False,
                    "error": "volume is required for set_volume operation",
                    "error_code": "MISSING_VOLUME",
                }

            result = await plex.control_playback(client_identifier=client_id, action="set_volume", volume=volume)
            return {
                "success": result,
                "operation": "set_volume",
                "client_id": client_id,
                "volume": volume,
            }

        # Operation: control
        if operation == "control":
            if not action:
                return {
                    "success": False,
                    "error": "action is required for control operation",
                    "error_code": "MISSING_ACTION",
                    "suggestions": [
                        "Provide action parameter: play, pause, stop, skip_next, skip_previous, step_forward, step_back, seek_to, set_volume",
                    ],
                }

            valid_actions = [
                "play",
                "pause",
                "stop",
                "skip_next",
                "skip_previous",
                "step_forward",
                "step_back",
                "seek_to",
                "set_volume",
            ]
            if action not in valid_actions:
                return {
                    "success": False,
                    "error": f"Invalid action: '{action}'",
                    "error_code": "INVALID_ACTION",
                    "suggestions": [
                        f"Valid actions: {', '.join(valid_actions)}",
                        f"You provided: '{action}'",
                    ],
                }

            # Build kwargs for control_playback
            kwargs = {}
            if media_key:
                kwargs["media_key"] = media_key
            if seek_to is not None:
                kwargs["seek_to"] = seek_to
            if offset is not None:
                kwargs["offset"] = offset
            if volume is not None:
                kwargs["volume"] = volume

            result = await plex.control_playback(
                client_identifier=client_id,
                action=action,
                **kwargs,
            )
            return {
                "success": result,
                "operation": "control",
                "client_id": client_id,
                "action": action,
                "data": {"controlled": result},
            }

        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'",
            "error_code": "INVALID_OPERATION",
            "suggestions": [
                "Valid operations: list_sessions, list_clients, play, pause, stop, seek, skip_next, skip_previous, set_quality, control",
                f"You provided: '{operation}'",
            ],
        }

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.error(
            f"Error in plex_streaming operation '{operation}': {error_msg}",
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

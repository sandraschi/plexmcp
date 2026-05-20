"""
PlexMCP Streaming/Playback Control Portmanteau Tool

Consolidates all playback control and session management operations into a single comprehensive interface.
"""

import os
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...prefabs import build_streaming_client, build_streaming_session
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
async def plex_streaming(
    operation: Annotated[
        Literal[
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
        Field(description="The streaming operation to perform."),
    ],
    client_id: Annotated[str | None, Field(description="Machine identifier of the target Plex client.")] = None,
    media_key: Annotated[str | None, Field(description="Media key (rating key) of the item to stream.")] = None,
    seek_to: Annotated[int | None, Field(description="Position in milliseconds to seek to.")] = None,
    offset: Annotated[int | None, Field(description="Offset in seconds for skip operations.")] = 30,
    action: Annotated[
        str | None, Field(description="Playback action for the control operation (play, pause, stop, etc.).")
    ] = None,
    volume: Annotated[int | None, Field(description="Volume level (0-100) for set_volume operation.")] = None,
    quality: Annotated[str | None, Field(description="Stream quality setting (e.g., '1080p', '720p', '480p').")] = None,
) -> ToolResult:
    """
    Comprehensive playback control and session management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates session monitoring, client discovery, and remote playback control into a single tool.

    OPERATIONS:
    - list_sessions: List all active sessions with client and playback details.
    - list_clients: List all available Plex clients for remote control.
    - play: Start media playback on a specific client (auto-selects if omitted).
    - pause/stop: Control current playback state on a client.
    - seek: Jump to a specific position (milliseconds) in the media.
    - skip_next/skip_previous: Navigate through the play queue.
    - set_volume: Adjust the playback volume (0-100) on a client.
    - control: Generic playback control for custom actions (e.g., step_forward).

    ## Return Format
    {"success": bool, "operation": str, "data": dict, "count": int | None, "error": str | None}

    ## Examples
    await plex_streaming(operation="list_sessions")
    await plex_streaming(operation="play", client_id="abc123", media_key="12345")
    await plex_streaming(operation="seek", client_id="abc123", seek_to=60000)
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
                structured_content=build_streaming_session(sessions),
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
                structured_content=build_streaming_client(clients),
            )

        # Operation: play (can auto-select client, so check before requiring client_id)
        if operation == "play":
            if not media_key:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "media_key is required for play operation",
                        "error_code": "MISSING_MEDIA_KEY",
                        "suggestions": [
                            "Get media_key from plex_media(operation='browse') or plex_media(operation='search')",
                            "Provide media_key parameter",
                        ],
                    }
                )

            # Auto-select client if not provided
            if not client_id:
                # Get media type to select appropriate client
                media_type = await plex._run_in_executor(plex._get_media_type, media_key)
                if not media_type:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": "Could not determine media type. Please provide client_id explicitly.",
                            "error_code": "MEDIA_TYPE_UNKNOWN",
                            "suggestions": [
                                "Provide client_id parameter explicitly",
                                "Use plex_streaming(operation='list_clients') to see available clients",
                            ],
                        }
                    )

                # Get all clients
                all_clients = await plex.get_clients()
                if not all_clients:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": "No clients available",
                            "error_code": "NO_CLIENTS",
                            "suggestions": [
                                "Ensure at least one Plex client is open and connected",
                                "Try plex_streaming(operation='list_clients') to check available clients",
                            ],
                        }
                    )

                # Select best client for this media type
                selected_client = await plex._run_in_executor(plex._select_client_for_media, media_type, all_clients)
                if not selected_client:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": "Could not select appropriate client",
                            "error_code": "CLIENT_SELECTION_FAILED",
                            "suggestions": [
                                "Provide client_id parameter explicitly",
                                f"Available clients: {[c.get('name') for c in all_clients]}",
                            ],
                        }
                    )

                client_id = selected_client.get("machineIdentifier") or selected_client.get("id")
                logger.info(
                    f"Auto-selected client '{selected_client.get('name')}' ({selected_client.get('product')}) for {media_type} media"
                )

            result = await plex.control_playback(
                client_identifier=client_id,
                action="play",
                media_key=media_key,
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "play",
                    "client_id": client_id,
                    "media_key": media_key,
                    "data": {"played": result},
                }
            )

        # All other operations require client_id
        if not client_id:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"client_id is required for {operation} operation",
                    "error_code": "MISSING_CLIENT_ID",
                    "suggestions": [
                        "Use plex_streaming(operation='list_clients') to find available client IDs",
                        f"Provide client_id parameter: plex_streaming(operation='{operation}', client_id='...')",
                    ],
                }
            )

        # Operation: pause
        if operation == "pause":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="pause",
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "pause",
                    "client_id": client_id,
                    "data": {"paused": result},
                }
            )

        # Operation: stop
        if operation == "stop":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="stop",
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "stop",
                    "client_id": client_id,
                    "data": {"stopped": result},
                }
            )

        # Operation: seek
        if operation == "seek":
            if seek_to is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "seek_to is required for seek operation",
                        "error_code": "MISSING_SEEK_TO",
                        "suggestions": ["Provide seek_to parameter (position in milliseconds)"],
                    }
                )

            result = await plex.control_playback(
                client_identifier=client_id,
                action="seek_to",
                seek_to=seek_to,
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "seek",
                    "client_id": client_id,
                    "seek_to": seek_to,
                    "data": {"seeked": result},
                }
            )

        # Operation: skip_next
        if operation == "skip_next":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="skip_next",
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "skip_next",
                    "client_id": client_id,
                    "data": {"skipped": result},
                }
            )

        # Operation: skip_previous
        if operation == "skip_previous":
            result = await plex.control_playback(
                client_identifier=client_id,
                action="skip_previous",
            )
            return ToolResult(
                content={
                    "success": result,
                    "operation": "skip_previous",
                    "client_id": client_id,
                    "data": {"skipped": result},
                }
            )

        # Operation: set_quality
        if operation == "set_quality":
            if not quality:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "quality is required for set_quality operation",
                        "error_code": "MISSING_QUALITY",
                        "suggestions": ["Provide quality parameter (e.g., '1080p', '720p', '480p')"],
                    }
                )

            # Note: Plex API may have limited support for quality settings
            # This is a placeholder implementation
            return ToolResult(
                content={
                    "success": False,
                    "error": "set_quality operation is not yet fully implemented",
                    "error_code": "NOT_IMPLEMENTED",
                    "suggestions": [
                        "Use plex_performance tool for quality profile management",
                        "Quality settings may need to be configured via Plex Web App",
                    ],
                }
            )

        # Operation: set_volume
        if operation == "set_volume":
            if not client_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "client_id is required for set_volume operation",
                        "error_code": "MISSING_CLIENT_ID",
                    }
                )
            if volume is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "volume is required for set_volume operation",
                        "error_code": "MISSING_VOLUME",
                    }
                )

            result = await plex.control_playback(client_identifier=client_id, action="set_volume", volume=volume)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "set_volume",
                    "client_id": client_id,
                    "volume": volume,
                }
            )

        # Operation: control
        if operation == "control":
            if not action:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "action is required for control operation",
                        "error_code": "MISSING_ACTION",
                        "suggestions": [
                            "Provide action parameter: play, pause, stop, skip_next, skip_previous, step_forward, step_back, seek_to, set_volume",
                        ],
                    }
                )

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
                return ToolResult(
                    content={
                        "success": False,
                        "error": f"Invalid action: '{action}'",
                        "error_code": "INVALID_ACTION",
                        "suggestions": [
                            f"Valid actions: {', '.join(valid_actions)}",
                            f"You provided: '{action}'",
                        ],
                    }
                )

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
            return ToolResult(
                content={
                    "success": result,
                    "operation": "control",
                    "client_id": client_id,
                    "action": action,
                    "data": {"controlled": result},
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: list_sessions, list_clients, play, pause, stop, seek, skip_next, skip_previous, set_quality, control",
                    f"You provided: '{operation}'",
                ],
            }
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
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

        return ToolResult(
            content={
                "success": False,
                "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
                "error_code": "AUTH_FAILURE" if is_unauthorized else "UNEXPECTED_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            }
        )

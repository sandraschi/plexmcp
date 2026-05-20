"""
PlexMCP Audio Management Portmanteau Tool

Consolidates all audio-specific operations into a single comprehensive interface.
Supports volume control, audio stream selection, and media handover between clients.
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
async def plex_audio_mgr(
    operation: Annotated[
        Literal[
            "get_volume",
            "set_volume",
            "mute",
            "unmute",
            "list_streams",
            "select_stream",
            "handover",
        ],
        Field(description="Operation to perform."),
    ],
    client_id: Annotated[str | None, Field(description="Client identifier for playback control.")] = None,
    target_client_id: Annotated[str | None, Field(description="Target client for handover.")] = None,
    media_key: Annotated[str | None, Field(description="Media key for stream listing.")] = None,
    volume: Annotated[int | None, Field(description="Volume level (0-100).")] = None,
    stream_id: Annotated[str | None, Field(description="Stream ID for stream selection.")] = None,
) -> ToolResult:
    """Comprehensive audio management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 audio-focused control operations into a single interface to minimize
    latency during real-time playback adjustments and stream switching.

    ## Return Format
    {"success": bool, "data": dict, "message": str}

    ## Examples
    await plex_audio_mgr(operation="list_streams", media_key="12345")
    await plex_audio_mgr(operation="set_volume", client_id="client-abc", volume=75)
    """
    plex = _get_plex_service()

    try:
        if operation in ("set_volume", "mute", "unmute"):
            if not client_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": f"client_id is required for {operation} operation",
                        "error_code": "MISSING_CLIENT_ID",
                    }
                )

            target_volume = volume
            if operation == "mute":
                target_volume = 0
            elif operation == "unmute":
                target_volume = 50

            if target_volume is None and operation == "set_volume":
                return ToolResult(
                    content={
                        "success": False,
                        "error": "volume parameter is required for set_volume",
                        "error_code": "MISSING_VOLUME",
                    }
                )

            result = await plex.control_playback(client_identifier=client_id, action="set_volume", volume=target_volume)
            return ToolResult(
                content={
                    "success": result,
                    "operation": operation,
                    "client_id": client_id,
                    "volume": target_volume,
                }
            )

        if operation == "get_volume":
            if not client_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "client_id is required for get_volume operation",
                        "error_code": "MISSING_CLIENT_ID",
                    }
                )
            return ToolResult(
                content={
                    "success": False,
                    "operation": "get_volume",
                    "client_id": client_id,
                    "error": "Retrieving volume level is not supported by the Plex remote control API",
                    "error_code": "NOT_SUPPORTED",
                }
            )

        if operation == "list_streams":
            if not media_key:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "media_key is required for list_streams operation",
                        "error_code": "MISSING_MEDIA_KEY",
                    }
                )

            streams = await plex.get_audio_streams(media_key)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_streams",
                    "media_key": media_key,
                    "streams": streams,
                    "count": len(streams),
                }
            )

        if operation == "select_stream":
            if not client_id or not stream_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "client_id and stream_id are required for select_stream operation",
                        "error_code": "MISSING_PARAMETERS",
                    }
                )

            result = await plex.set_audio_stream(client_id, stream_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "select_stream",
                    "client_id": client_id,
                    "stream_id": stream_id,
                }
            )

        if operation == "handover":
            if not client_id or not target_client_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "client_id (source) and target_client_id are required for handover operation",
                        "error_code": "MISSING_PARAMETERS",
                    }
                )

            result = await plex.handover_media(client_id, target_client_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "handover",
                    "source_client_id": client_id,
                    "target_client_id": target_client_id,
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Operation {operation} not yet fully implemented or recognized",
                "error_code": "NOT_IMPLEMENTED",
            }
        )

    except Exception as e:
        logger.exception(f"Error in plex_audio_mgr({operation}): {str(e)}")
        return ToolResult(content={"success": False, "error": str(e), "error_code": "EXECUTION_ERROR"})

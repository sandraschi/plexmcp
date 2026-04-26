"""
PlexMCP Audio Management Portmanteau Tool

Consolidates all audio-specific operations into a single comprehensive interface.
Supports volume control, audio stream selection, and media handover between clients.
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
async def plex_audio_mgr(
    operation: Literal[
        "get_volume",
        "set_volume",
        "mute",
        "unmute",
        "list_streams",
        "select_stream",
        "handover",
    ],
    client_id: str | None = None,
    target_client_id: str | None = None,
    media_key: str | None = None,
    volume: int | None = None,
    stream_id: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive audio management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 audio-focused control operations into a single interface to minimize
    latency during real-time playback adjustments and stream switching.

    OPERATIONS:
    - get_volume: Retrieve the current output level of a connected Plex client.
    - set_volume: Precise adjustment of playback volume (0-100 scale).
    - mute: Immediate suppression of audio output.
    - unmute: Restoration of audio at the previous or default level.
    - list_streams: Enumerate all available audio tracks (codecs, languages) for a media item.
    - select_stream: Dynamic switching between available audio tracks during playback.
    - handover: Seamless transfer of the current audio session to a different target client.

    Returns:
    FastMCP 3.1+ dialogic response with client audio state and track details.
    Enables autonomous multi-room audio control and track optimization.
    """
    plex = _get_plex_service()

    try:
        # Operation: set_volume / mute / unmute
        if operation in ("set_volume", "mute", "unmute"):
            if not client_id:
                return {
                    "success": False,
                    "error": f"client_id is required for {operation} operation",
                    "error_code": "MISSING_CLIENT_ID",
                }

            target_volume = volume
            if operation == "mute":
                target_volume = 0
            elif operation == "unmute":
                target_volume = 50  # Default restoration if previous not known

            if target_volume is None and operation == "set_volume":
                return {
                    "success": False,
                    "error": "volume parameter is required for set_volume",
                    "error_code": "MISSING_VOLUME",
                }

            result = await plex.control_playback(client_identifier=client_id, action="set_volume", volume=target_volume)
            return {
                "success": result,
                "operation": operation,
                "client_id": client_id,
                "volume": target_volume,
            }

        # Operation: get_volume
        if operation == "get_volume":
            if not client_id:
                return {
                    "success": False,
                    "error": "client_id is required for get_volume operation",
                    "error_code": "MISSING_CLIENT_ID",
                }
            # Note: Plex remote control API is primarily one-way.
            # Retrieving real-time volume from a client is often not supported via this interface.
            return {
                "success": False,
                "operation": "get_volume",
                "client_id": client_id,
                "error": "Retrieving volume level is not supported by the Plex remote control API",
                "error_code": "NOT_SUPPORTED",
            }

        # Operation: list_streams
        if operation == "list_streams":
            if not media_key:
                return {
                    "success": False,
                    "error": "media_key is required for list_streams operation",
                    "error_code": "MISSING_MEDIA_KEY",
                }

            streams = await plex.get_audio_streams(media_key)
            return {
                "success": True,
                "operation": "list_streams",
                "media_key": media_key,
                "streams": streams,
                "count": len(streams),
            }

        # Operation: select_stream
        if operation == "select_stream":
            if not client_id or not stream_id:
                return {
                    "success": False,
                    "error": "client_id and stream_id are required for select_stream operation",
                    "error_code": "MISSING_PARAMETERS",
                }

            result = await plex.set_audio_stream(client_id, stream_id)
            return {
                "success": result,
                "operation": "select_stream",
                "client_id": client_id,
                "stream_id": stream_id,
            }

        # Operation: handover
        if operation == "handover":
            if not client_id or not target_client_id:
                return {
                    "success": False,
                    "error": "client_id (source) and target_client_id are required for handover operation",
                    "error_code": "MISSING_PARAMETERS",
                }

            result = await plex.handover_media(client_id, target_client_id)
            return {
                "success": result,
                "operation": "handover",
                "source_client_id": client_id,
                "target_client_id": target_client_id,
            }

        return {
            "success": False,
            "error": f"Operation {operation} not yet fully implemented or recognized",
            "error_code": "NOT_IMPLEMENTED",
        }

    except Exception as e:
        logger.error(f"Error in plex_audio_mgr({operation}): {str(e)}")
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR"}

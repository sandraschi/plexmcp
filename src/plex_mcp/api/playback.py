"""
Playback-related API endpoints for PlexMCP.

This module contains API endpoints for managing Plex playback, sessions, and clients.
"""

from typing import List, Optional, Dict, Any
# Import the shared FastMCP instance from the package level
from ..app import mcp

# Import models
from ..models import (
    PlexSession,
    PlexClient,
    RemotePlaybackRequest,
    CastRequest,
    PlaybackControlResult
)

@mcp.tool()
async def get_clients() -> List[PlexClient]:
    """
    Get all available Plex client devices.
    
    Returns information about connected Plex clients that can
    be used for remote playback control.
    
    Returns:
        List of available Plex client devices
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        PlexClient(
            name="Living Room TV",
            host="192.168.1.100",
            machine_identifier="client123",
            product="Plex for Android (TV)",
            platform="Android",
            platform_version="11",
            device="Sony Bravia"
        ),
        PlexClient(
            name="Bedroom",
            host="192.168.1.101",
            machine_identifier="client456",
            product="Plex Web",
            platform="Chrome",
            platform_version="96.0",
            device="Desktop"
        )
    ]

@mcp.tool()
async def get_sessions() -> List[PlexSession]:
    """
    Get active playback sessions on the Plex server.
    
    Shows who is currently watching what content,
    including playback progress and player information.
    
    Returns:
        List of active playback sessions
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        PlexSession(
            session_key="session123",
            user="user1",
            player="Living Room TV",
            state="playing",
            title="Sample Movie",
            progress=3600,  # 1 hour in seconds
            duration=7200   # 2 hours in seconds
        )
    ]

@mcp.tool()
async def control_playback(request: RemotePlaybackRequest) -> PlaybackControlResult:
    """
    Control playback on a remote Plex client.
    
    Args:
        request: Remote playback control request
        
    Returns:
        Result of the playback control operation
    """
    # TODO: Implement actual Plex service call
    print(f"Controlling playback on client {request.client_id}: {request.action}")
    
    if request.media_key:
        print(f"Media key: {request.media_key}")
    if request.seek_offset is not None:
        print(f"Seek offset: {request.seek_offset}ms")
    if request.volume_level is not None:
        print(f"Volume level: {request.volume_level}")
    
    return PlaybackControlResult(
        status="success",
        client_id=request.client_id,
        action=request.action,
        current_state="playing",
        position=1800000,  # 30 minutes in milliseconds
        duration=7200000,  # 2 hours in milliseconds
        volume=75,
        message=f"Successfully executed {request.action} on {request.client_id}"
    )

@mcp.tool()
async def cast_media(request: CastRequest) -> PlaybackControlResult:
    """
    Cast media to a Plex client.
    
    Args:
        request: Cast request with media and client information
        
    Returns:
        Result of the cast operation
    """
    # TODO: Implement actual Plex service call
    print(f"Casting media {request.media_key} to client {request.client_id}")
    
    if request.start_offset is not None:
        print(f"Starting at offset: {request.start_offset}ms")
    if request.queue_items:
        print(f"Queue items: {len(request.queue_items)}")
    print(f"Replace queue: {request.replace_queue}")
    
    return PlaybackControlResult(
        status="success",
        client_id=request.client_id,
        action="play_media",
        current_state="playing",
        position=0,
        duration=7200000,  # 2 hours in milliseconds
        volume=50,
        message=f"Successfully cast media to {request.client_id}"
    )

# No need to export app - tools are registered with the shared mcp instance

"""Plex session management tools for FastMCP 2.10.1."""
from typing import Dict, List, Optional

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.session import Session
from ..services.plex_service import PlexService

@mcp_tool("plex.sessions.list")
async def list_sessions(plex: PlexService) -> List[Session]:
    """Get a list of all active Plex sessions.
    
    Returns:
        List of active sessions with client and playback information
    """
    return await plex.get_sessions()

class ClientInfo(BaseModel):
    """Information about a Plex client."""
    id: str = Field(..., description="Client identifier")
    name: str = Field(..., description="Client name")
    product: str = Field(..., description="Client product name")
    platform: str = Field(..., description="Client platform")
    local: bool = Field(..., description="Whether the client is on the local network")

@mcp_tool("plex.clients.list")
async def list_clients(plex: PlexService) -> List[ClientInfo]:
    """Get a list of all available Plex clients.
    
    Returns:
        List of available Plex clients
    """
    clients = await plex.get_clients()
    return [
        ClientInfo(
            id=client['machine_identifier'],
            name=client['name'],
            product=client['product'],
            platform=client['platform'],
            local=client['local']
        )
        for client in clients
    ]

class PlaybackControlRequest(BaseModel):
    """Request model for controlling playback."""
    client_id: str = Field(..., description="ID of the client to control")
    action: str = Field(..., description="Action to perform (play, pause, stop, skip_next, skip_previous, step_forward, step_back, seek_to)")
    media_key: Optional[str] = Field(None, description="Media key to play (required for play action)")
    seek_to: Optional[int] = Field(None, description="Position in milliseconds to seek to (for seek_to action)")
    offset: Optional[int] = Field(30, description="Time offset in seconds (for step_forward/step_back actions)")

@mcp_tool("plex.playback.control")
async def control_playback(
    plex: PlexService,
    request: PlaybackControlRequest
) -> bool:
    """Control playback on a Plex client.
    
    Args:
        request: Playback control request
        
    Returns:
        bool: True if the operation was successful
    """
    return await plex.control_playback(
        client_identifier=request.client_id,
        action=request.action,
        media_key=request.media_key,
        seek_to=request.seek_to,
        offset=request.offset
    )

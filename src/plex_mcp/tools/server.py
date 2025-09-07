"""Plex server tools for FastMCP 2.10.1."""
from typing import Any, Dict, List, Optional

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..services.plex_service import PlexService

class ServerStatusResponse(BaseModel):
    """Response model for server status."""
    name: str = Field(..., description="Server friendly name")
    version: str = Field(..., description="Plex server version")
    platform: str = Field(..., description="Server platform")
    active_sessions: int = Field(..., description="Number of active sessions")
    updated_at: float = Field(..., description="Last update timestamp")

@mcp_tool("plex.server.status")
async def get_server_status(plex: PlexService) -> ServerStatusResponse:
    """Get the current status of the Plex server.
    
    Returns:
        Server status information including version, platform, and active sessions.
    """
    status = await plex.get_server_status()
    return ServerStatusResponse(**status.dict())

class LibraryInfo(BaseModel):
    """Model for library information."""
    id: str = Field(..., description="Library ID")
    title: str = Field(..., description="Library title")
    type: str = Field(..., description="Library type (movie, show, artist, photo, etc.)")
    count: int = Field(..., description="Number of items in the library")
    updated_at: float = Field(..., description="Last update timestamp")

@mcp_tool("plex.libraries.list")
async def list_libraries(plex: PlexService) -> List[LibraryInfo]:
    """List all libraries available on the Plex server.
    
    Returns:
        List of libraries with their basic information.
        
    Raises:
        RuntimeError: If there's an error fetching libraries from Plex server
    """
    try:
        libraries = await plex.list_libraries()
        if not libraries:
            raise RuntimeError("No libraries found on Plex server")
            
        return [
            LibraryInfo(
                id=lib.get('id', ''),
                title=lib.get('title', 'Unknown'),
                type=lib.get('type', 'unknown'),
                count=lib.get('count', 0),
                updated_at=lib.get('updated_at', 0)
            )
            for lib in libraries
        ]
    except Exception as e:
        error_msg = f"Failed to list libraries: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

class ServerInfoResponse(BaseModel):
    """Comprehensive server information response."""
    status: ServerStatusResponse = Field(..., description="Server status information")
    libraries: List[LibraryInfo] = Field(..., description="List of libraries on the server")

@mcp_tool("plex.server.info")
async def get_server_info(plex: PlexService) -> ServerInfoResponse:
    """Get comprehensive information about the Plex server.
    
    Returns:
        Combined server status and library information.
    """
    status = await get_server_status(plex)
    libraries = await list_libraries(plex)
    return ServerInfoResponse(status=status, libraries=libraries)

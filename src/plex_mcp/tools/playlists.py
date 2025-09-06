"""Plex playlist management tools for FastMCP 2.10.1."""
from typing import List, Optional, Dict, Any

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.playlists import PlexPlaylist, PlaylistCreateRequest, PlaylistAnalytics
from ..services.plex_service import PlexService

class CreatePlaylistRequest(BaseModel):
    """Request model for creating a new playlist."""
    title: str = Field(..., min_length=1, max_length=255, description="Title of the playlist")
    items: List[str] = Field(..., description="List of media item IDs to include in the playlist")
    description: Optional[str] = Field(None, description="Optional description for the playlist")
    public: bool = Field(False, description="Whether the playlist should be publicly visible")
    sort: Optional[str] = Field(None, description="Sort order for playlist items")

@mcp_tool("plex.playlists.create")
async def create_playlist(plex: PlexService, request: CreatePlaylistRequest) -> PlexPlaylist:
    """Create a new playlist.
    
    Args:
        request: Playlist creation parameters
        
    Returns:
        The created playlist information
    """
    return await plex.create_playlist(
        title=request.title,
        items=request.items,
        description=request.description,
        public=request.public,
        sort=request.sort
    )

class GetPlaylistRequest(BaseModel):
    """Request model for getting a specific playlist."""
    playlist_id: str = Field(..., description="ID of the playlist to retrieve")

@mcp_tool("plex.playlists.get")
async def get_playlist(plex: PlexService, request: GetPlaylistRequest) -> Optional[PlexPlaylist]:
    """Get a specific playlist by ID.
    
    Args:
        request: Playlist retrieval parameters
        
    Returns:
        Playlist information if found, None otherwise
    """
    return await plex.get_playlist(playlist_id=request.playlist_id)

@mcp_tool("plex.playlists.list")
async def list_playlists(plex: PlexService) -> List[PlexPlaylist]:
    """List all playlists.
    
    Returns:
        List of all playlists
    """
    return await plex.list_playlists()

class UpdatePlaylistRequest(BaseModel):
    """Request model for updating a playlist."""
    playlist_id: str = Field(..., description="ID of the playlist to update")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the playlist")
    description: Optional[str] = Field(None, description="New description for the playlist")
    public: Optional[bool] = Field(None, description="Whether the playlist should be publicly visible")
    sort: Optional[str] = Field(None, description="New sort order for playlist items")

@mcp_tool("plex.playlists.update")
async def update_playlist(plex: PlexService, request: UpdatePlaylistRequest) -> PlexPlaylist:
    """Update an existing playlist.
    
    Args:
        request: Playlist update parameters
        
    Returns:
        The updated playlist information
    """
    return await plex.update_playlist(
        playlist_id=request.playlist_id,
        title=request.title,
        description=request.description,
        public=request.public,
        sort=request.sort
    )

class DeletePlaylistRequest(BaseModel):
    """Request model for deleting a playlist."""
    playlist_id: str = Field(..., description="ID of the playlist to delete")

@mcp_tool("plex.playlists.delete")
async def delete_playlist(plex: PlexService, request: DeletePlaylistRequest) -> bool:
    """Delete a playlist.
    
    Args:
        request: Playlist deletion parameters
        
    Returns:
        True if deletion was successful, False otherwise
    """
    return await plex.delete_playlist(playlist_id=request.playlist_id)

class AddToPlaylistRequest(BaseModel):
    """Request model for adding items to a playlist."""
    playlist_id: str = Field(..., description="ID of the playlist to add items to")
    items: List[str] = Field(..., description="List of media item IDs to add to the playlist")

@mcp_tool("plex.playlists.add_items")
async def add_to_playlist(plex: PlexService, request: AddToPlaylistRequest) -> PlexPlaylist:
    """Add items to an existing playlist.
    
    Args:
        request: Playlist item addition parameters
        
    Returns:
        The updated playlist information
    """
    return await plex.add_to_playlist(
        playlist_id=request.playlist_id,
        items=request.items
    )

class RemoveFromPlaylistRequest(BaseModel):
    """Request model for removing items from a playlist."""
    playlist_id: str = Field(..., description="ID of the playlist to remove items from")
    items: List[str] = Field(..., description="List of media item IDs to remove from the playlist")

@mcp_tool("plex.playlists.remove_items")
async def remove_from_playlist(plex: PlexService, request: RemoveFromPlaylistRequest) -> PlexPlaylist:
    """Remove items from a playlist.
    
    Args:
        request: Playlist item removal parameters
        
    Returns:
        The updated playlist information
    """
    return await plex.remove_from_playlist(
        playlist_id=request.playlist_id,
        items=request.items
    )

class GetPlaylistAnalyticsRequest(BaseModel):
    """Request model for getting playlist analytics."""
    playlist_id: str = Field(..., description="ID of the playlist to get analytics for")

@mcp_tool("plex.playlists.get_analytics")
async def get_playlist_analytics(plex: PlexService, request: GetPlaylistAnalyticsRequest) -> PlaylistAnalytics:
    """Get analytics for a specific playlist.
    
    Args:
        request: Playlist analytics parameters
        
    Returns:
        Analytics data for the specified playlist
    """
    return await plex.get_playlist_analytics(playlist_id=request.playlist_id)

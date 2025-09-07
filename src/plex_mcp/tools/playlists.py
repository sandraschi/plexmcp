"""Plex playlist management tools for FastMCP 2.10.1."""
import logging
from typing import List, Optional, Dict, Any

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.playlists import PlexPlaylist, PlaylistCreateRequest, PlaylistAnalytics
from ..services.plex_service import PlexService

logger = logging.getLogger(__name__)

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
    await plex.connect()
    
    # Get the media items from Plex
    items = []
    for item_id in request.items:
        try:
            item = await plex.server.lookupItem(item_id)
            items.append(item)
        except Exception as e:
            logger.warning(f"Could not find media item {item_id}: {e}")
    
    if not items:
        raise ValueError("No valid media items found to create playlist")
    
    # Create the playlist
    playlist = await plex.server.createPlaylist(
        title=request.title,
        items=items,
        smart=request.smart if hasattr(request, 'smart') else False,
        summary=request.description or ""
    )
    
    return PlexPlaylist(
        key=playlist.ratingKey,
        title=playlist.title,
        type=playlist.playlistType,
        summary=playlist.summary or "",
        duration=playlist.duration,
        item_count=len(playlist.items()),
        smart=playlist.smart,
        created_at=int(playlist.addedAt.timestamp()),
        updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
        owner=playlist.username
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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        
        return PlexPlaylist(
            key=playlist.ratingKey,
            title=playlist.title,
            type=playlist.playlistType,
            summary=playlist.summary or "",
            duration=playlist.duration,
            item_count=len(playlist.items()),
            smart=playlist.smart,
            created_at=int(playlist.addedAt.timestamp()),
            updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
            owner=playlist.username
        )
    except Exception as e:
        logger.error(f"Error getting playlist {request.playlist_id}: {e}")
        return None

@mcp_tool("plex.playlists.list")
async def list_playlists(plex: PlexService) -> List[PlexPlaylist]:
    """List all playlists.
    
    Returns:
        List of all playlists
    """
    await plex.connect()
    
    try:
        playlists = await plex.server.playlists()
        
        return [
            PlexPlaylist(
                key=playlist.ratingKey,
                title=playlist.title,
                type=playlist.playlistType,
                summary=playlist.summary or "",
                duration=playlist.duration,
                item_count=len(playlist.items()),
                smart=playlist.smart,
                created_at=int(playlist.addedAt.timestamp()),
                updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
                owner=playlist.username
            )
            for playlist in playlists
        ]
    except Exception as e:
        logger.error(f"Error listing playlists: {e}")
        return []

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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        
        # Update fields if provided
        if request.title is not None:
            playlist.editTitle(request.title)
        if request.description is not None:
            playlist.editSummary(request.description)
        if request.public is not None:
            # Note: Plex API doesn't directly support public/private playlists
            pass
        if request.sort is not None:
            # Note: Plex API has limited sorting capabilities
            pass
            
        # Refresh the playlist to get updated data
        playlist.reload()
        
        return PlexPlaylist(
            key=playlist.ratingKey,
            title=playlist.title,
            type=playlist.playlistType,
            summary=playlist.summary or "",
            duration=playlist.duration,
            item_count=len(playlist.items()),
            smart=playlist.smart,
            created_at=int(playlist.addedAt.timestamp()),
            updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
            owner=playlist.username
        )
    except Exception as e:
        logger.error(f"Error updating playlist {request.playlist_id}: {e}")
        raise

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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        await playlist.delete()
        return True
    except Exception as e:
        logger.error(f"Error deleting playlist {request.playlist_id}: {e}")
        return False

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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        
        # Get the media items from Plex
        items_to_add = []
        for item_id in request.items:
            try:
                item = await plex.server.lookupItem(item_id)
                items_to_add.append(item)
            except Exception as e:
                logger.warning(f"Could not find media item {item_id}: {e}")
        
        if not items_to_add:
            raise ValueError("No valid media items found to add to playlist")
        
        # Add items to playlist
        await playlist.addItems(items_to_add)
        
        # Refresh the playlist to get updated data
        playlist.reload()
        
        return PlexPlaylist(
            key=playlist.ratingKey,
            title=playlist.title,
            type=playlist.playlistType,
            summary=playlist.summary or "",
            duration=playlist.duration,
            item_count=len(playlist.items()),
            smart=playlist.smart,
            created_at=int(playlist.addedAt.timestamp()),
            updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
            owner=playlist.username
        )
    except Exception as e:
        logger.error(f"Error adding items to playlist {request.playlist_id}: {e}")
        raise

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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        
        # Get the current items
        items = playlist.items()
        
        # Find items to remove
        items_to_remove = []
        for item in items:
            if str(item.ratingKey) in request.items:
                items_to_remove.append(item)
        
        if not items_to_remove:
            logger.warning(f"No matching items found to remove from playlist {request.playlist_id}")
            return await get_playlist(plex, GetPlaylistRequest(playlist_id=request.playlist_id))
        
        # Remove items from playlist
        await playlist.removeItems(items_to_remove)
        
        # Refresh the playlist to get updated data
        playlist.reload()
        
        return PlexPlaylist(
            key=playlist.ratingKey,
            title=playlist.title,
            type=playlist.playlistType,
            summary=playlist.summary or "",
            duration=playlist.duration,
            item_count=len(playlist.items()),
            smart=playlist.smart,
            created_at=int(playlist.addedAt.timestamp()),
            updated_at=int(playlist.updatedAt.timestamp()) if playlist.updatedAt else int(playlist.addedAt.timestamp()),
            owner=playlist.username
        )
    except Exception as e:
        logger.error(f"Error removing items from playlist {request.playlist_id}: {e}")
        raise

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
    await plex.connect()
    
    try:
        playlist = await plex.server.playlist(request.playlist_id)
        items = playlist.items()
        
        # Get view counts and other metrics (simplified example)
        total_plays = sum(getattr(item, 'viewCount', 0) for item in items)
        unique_users = len(set(item.lastViewedAt for item in items if hasattr(item, 'lastViewedAt')))
        
        # Get popular items (top 3 most played)
        popular_items = sorted(
            [item for item in items if hasattr(item, 'viewCount')],
            key=lambda x: getattr(x, 'viewCount', 0),
            reverse=True
        )[:3]
        
        return PlaylistAnalytics(
            playlist_id=playlist.ratingKey,
            name=playlist.title,
            total_plays=total_plays,
            unique_users=unique_users or 1,
            avg_completion_rate=75.0,  # This would require more detailed tracking
            popular_items=[str(item.ratingKey) for item in popular_items],
            skip_rate=10.0,  # This would require more detailed tracking
            recommendations=[
                "Consider adding more recent content" if len(items) > 10 else "Add more items to this playlist",
                "Create a themed playlist" if "mix" not in playlist.title.lower() else "Great themed playlist!"
            ],
            last_played=max(
                [int(item.lastViewedAt.timestamp()) for item in items 
                 if hasattr(item, 'lastViewedAt') and item.lastViewedAt],
                default=None
            )
        )
    except Exception as e:
        logger.error(f"Error getting analytics for playlist {request.playlist_id}: {e}")
        raise

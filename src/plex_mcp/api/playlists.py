"""
Playlist-related API endpoints for PlexMCP.

This module contains API endpoints for managing Plex playlists.
"""

from typing import List, Optional, Dict, Any
# Import the shared FastMCP instance from the package level
from . import mcp

# Import models
from ..models import (
    PlexPlaylist,
    PlaylistCreateRequest,
    PlaylistAnalytics,
    MediaItem
)

@mcp.tool()
async def create_playlist(
    request: PlaylistCreateRequest
) -> PlexPlaylist:
    """
    Create a new playlist (manual or smart) with Austrian efficiency.
    
    Supports both manual playlists (with specific items) and smart playlists
    (with automatic rules). Smart playlists update automatically based on criteria.
    
    Args:
        request: Playlist creation request
        
    Returns:
        Created playlist information
        
    Examples:
        Manual: create_playlist("Movie Night", items=["12345", "67890"])
        Smart: create_playlist("Top Action", smart_rules={"genre": "action", "rating": ">8"})
    """
    # TODO: Implement actual Plex service call
    print(f"Creating playlist: {request.name}")
    
    if request.summary:
        print(f"Description: {request.summary}")
    
    if request.items:
        print(f"Adding {len(request.items)} items to playlist")
    
    if request.smart_rules:
        print(f"Smart playlist rules: {request.smart_rules}")
    
    if request.library_id:
        print(f"Library ID: {request.library_id}")
    
    # Return a mock response
    return PlexPlaylist(
        key="playlist123",
        title=request.name,
        type="video",
        summary=request.summary or "",
        duration=7200,  # 2 hours
        item_count=len(request.items) if request.items else 10,
        smart=bool(request.smart_rules),
        created_at=1625097600,
        updated_at=1625097600,
        owner="current_user"
    )

@mcp.tool()
async def get_playlists(
    playlist_type: Optional[str] = None,
    user_playlists: bool = True
) -> List[PlexPlaylist]:
    """
    Get all playlists from the Plex server.
    
    Args:
        playlist_type: Optional filter by type (video, audio, photo)
        user_playlists: Include user-created playlists (default: True)
        
    Returns:
        List of playlists with metadata
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    playlists = [
        PlexPlaylist(
            key=f"playlist{i}",
            title=f"Sample Playlist {i}",
            type="video",
            summary=f"Sample playlist {i} description",
            duration=3600 * (i + 1),
            item_count=(i + 1) * 5,
            smart=i % 2 == 0,
            created_at=1625097600,
            updated_at=1625184000,
            owner="current_user" if i < 3 else "other_user"
        )
        for i in range(1, 6)
    ]
    
    if playlist_type:
        playlists = [p for p in playlists if p.type == playlist_type]
    
    if not user_playlists:
        playlists = [p for p in playlists if p.owner != "current_user"]
    
    return playlists

@mcp.tool()
async def get_playlist(
    playlist_id: str
) -> PlexPlaylist:
    """
    Get detailed information about a specific playlist.
    
    Args:
        playlist_id: ID of the playlist to retrieve
        
    Returns:
        Playlist details including items
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return PlexPlaylist(
        key=playlist_id,
        title=f"Sample Playlist {playlist_id[-1]}",
        type="video",
        summary=f"Detailed information for playlist {playlist_id}",
        duration=7200,
        item_count=10,
        smart=False,
        created_at=1625097600,
        updated_at=1625184000,
        owner="current_user"
    )

@mcp.tool()
async def get_playlist_items(
    playlist_id: str
) -> List[MediaItem]:
    """
    Get all items in a playlist.
    
    Args:
        playlist_id: ID of the playlist
        
    Returns:
        List of media items in the playlist
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        MediaItem(
            key=f"item{i}",
            title=f"Playlist Item {i}",
            type="movie",
            year=2023 - i,
            summary=f"This is item {i} in the playlist",
            rating=8.0 + (i * 0.1),
            thumb=f"https://example.com/thumb{i}.jpg",
            art=f"https://example.com/art{i}.jpg",
            duration=3600000,  # 1 hour in milliseconds
            added_at=1625097600,
            updated_at=1625184000
        )
        for i in range(1, 6)
    ]

@mcp.tool()
async def analyze_playlist(
    playlist_id: str
) -> PlaylistAnalytics:
    """
    Analyze playlist usage and provide recommendations.
    
    Args:
        playlist_id: ID of the playlist to analyze
        
    Returns:
        Analytics and recommendations for the playlist
    """
    # TODO: Implement actual analysis logic
    return PlaylistAnalytics(
        playlist_id=playlist_id,
        name=f"Sample Playlist {playlist_id[-1]}",
        total_plays=42,
        unique_users=3,
        avg_completion_rate=75.5,
        popular_items=["item1", "item3", "item5"],
        skip_rate=15.2,
        recommendations=[
            "Consider adding more recent content",
            "Try grouping similar items together"
        ],
        last_played=1625184000
    )

# No need to export app - tools are registered with the shared mcp instance

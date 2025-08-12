"""
Core API endpoints for PlexMCP.

This module contains the core API endpoints for Plex server interaction.
"""

import asyncio
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

# Import models
from ..models import (
    PlexServerStatus,
    MediaLibrary,
    MediaItem,
    PlexSession,
    PlexClient,
    UserPermissions
)

# Import services (will be implemented later)
# from ..services.plex_service import PlexService

# Import the shared FastMCP instance from the package level
from . import mcp

@mcp.tool()
async def get_plex_status() -> PlexServerStatus:
    """
    Get Plex server status and identity information.
    
    Returns comprehensive server information including version,
    platform, database size, and MyPlex connection status.
    
    Returns:
        Complete server status and configuration information
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return PlexServerStatus(
        name="Plex Server",
        version="1.0.0",
        platform="Windows",
        updated_at=1625097600,
        size=1024,
        my_plex_username="user@example.com",
        my_plex_mapping_state="mapped",
        connected=True
    )

@mcp.tool()
async def get_libraries() -> List[MediaLibrary]:
    """
    Get all media libraries available on the Plex server.
    
    Returns information about each library including type,
    item count, and metadata agent configuration.
    
    Returns:
        List of all media libraries with detailed information
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        MediaLibrary(
            key="1",
            title="Movies",
            type="movie",
            agent="com.plexapp.agents.imdb",
            scanner="Plex Movie",
            language="en",
            uuid="123e4567-e89b-12d3-a456-426614174000",
            created_at=1625097600,
            updated_at=1625184000,
            count=100
        )
    ]

@mcp.tool()
async def search_media(
    query: str,
    library_id: Optional[str] = None
) -> List[MediaItem]:
    """
    Search for media content across libraries or within specific library.
    
    Args:
        query: Search terms (title, actor, director, etc)
        library_id: Optional library key to search within
        
    Returns:
        List of matching media items with metadata
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        MediaItem(
            key="/library/metadata/12345",
            title=query,
            type="movie",
            year=2023,
            summary=f"Search result for {query}",
            rating=8.5,
            thumb="https://example.com/thumb.jpg",
            art="https://example.com/art.jpg",
            duration=7200000,
            added_at=1625097600,
            updated_at=1625184000
        )
    ]

@mcp.tool()
async def get_recently_added(
    library_id: Optional[str] = None,
    limit: int = 20
) -> List[MediaItem]:
    """
    Get recently added media from all libraries or specific library.
    
    Args:
        library_id: Optional library key to filter by
        limit: Maximum number of items to return (default 20)
        
    Returns:
        List of recently added media items
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return [
        MediaItem(
            key=f"/library/metadata/{i}",
            title=f"Recently Added Item {i}",
            type="movie",
            year=2023,
            summary=f"Recently added item {i}",
            rating=8.0 + (i * 0.1),
            thumb=f"https://example.com/thumb{i}.jpg",
            art=f"https://example.com/art{i}.jpg",
            duration=7200000,
            added_at=1625097600,
            updated_at=1625184000
        )
        for i in range(min(limit, 10))
    ]

@mcp.tool()
async def get_media_info(media_key: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific media item.
    
    Args:
        media_key: Plex media key/ID
        
    Returns:
        Detailed media information including metadata and files
    """
    # TODO: Implement actual Plex service call
    # For now, return a mock response
    return {
        "key": media_key,
        "title": "Sample Media",
        "type": "movie",
        "year": 2023,
        "summary": "This is a sample media item",
        "rating": 8.5,
        "thumb": "https://example.com/thumb.jpg",
        "art": "https://example.com/art.jpg",
        "duration": 7200000,
        "added_at": 1625097600,
        "updated_at": 1625184000,
        "details": {
            "director": "Sample Director",
            "actors": ["Actor 1", "Actor 2"],
            "genres": ["Action", "Adventure"],
            "resolution": "1080p",
            "audio_channels": 5.1,
            "file_size": 2147483648
        }
    }

@mcp.tool()
async def scan_library(library_id: str) -> bool:
    """
    Trigger a library scan to update content.
    
    Forces Plex to scan the specified library for new,
    updated, or removed media files.
    
    Args:
        library_id: Library key to scan
        
    Returns:
        True if scan was triggered successfully
    """
    # TODO: Implement actual Plex service call
    print(f"Scanning library {library_id}...")
    return True

# No need to export app - tools are registered with the shared mcp instance

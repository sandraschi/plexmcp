"""Plex media tools for FastMCP 2.10.1."""
from typing import Any, Dict, List, Optional

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.media import MediaItem
from ..services.plex_service import PlexService

class MediaSearchRequest(BaseModel):
    """Request model for media search."""
    query: str = Field(..., description="Search query string")
    limit: int = Field(10, description="Maximum number of results to return")
    library_id: Optional[str] = Field(None, description="Optional library ID to search within")

@mcp_tool("plex.media.search")
async def search_media(
    plex: PlexService,
    request: MediaSearchRequest
) -> List[MediaItem]:
    """Search for media across all libraries or within a specific library.
    
    Args:
        request: Search parameters including query and optional filters
        
    Returns:
        List of media items matching the search criteria
    """
    return await plex.search_media(
        query=request.query,
        limit=request.limit,
        library_id=request.library_id
    )

class MediaInfoRequest(BaseModel):
    """Request model for getting media information."""
    media_id: str = Field(..., description="ID of the media item")

@mcp_tool("plex.media.get")
async def get_media_info(
    plex: PlexService,
    request: MediaInfoRequest
) -> Optional[MediaItem]:
    """Get detailed information about a specific media item.
    
    Args:
        request: Media information request
        
    Returns:
        Detailed media information or None if not found
    """
    return await plex.get_media_info(request.media_id)

class LibraryItemsRequest(BaseModel):
    """Request model for getting library items."""
    library_id: str = Field(..., description="ID of the library")
    limit: int = Field(100, description="Maximum number of items to return")
    offset: int = Field(0, description="Offset for pagination")

@mcp_tool("plex.library.items")
async def get_library_items(
    plex: PlexService,
    request: LibraryItemsRequest
) -> List[MediaItem]:
    """Get items from a specific library.
    
    Args:
        request: Library items request parameters
        
    Returns:
        List of media items in the specified library
    """
    return await plex.get_library_items(
        library_id=request.library_id,
        limit=request.limit,
        offset=request.offset
    )

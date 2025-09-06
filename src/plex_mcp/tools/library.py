"""Plex library management tools for FastMCP 2.10.1."""
from typing import List, Optional, Dict, Any

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field, HttpUrl

from ..models.media import MediaItem, LibrarySection
from ..services.plex_service import PlexService

class ScanLibraryRequest(BaseModel):
    """Request model for scanning a library."""
    library_id: str = Field(..., description="ID of the library to scan")
    force: bool = Field(False, description="Force a full scan")

@mcp_tool("plex.library.scan")
async def scan_library(plex: PlexService, request: ScanLibraryRequest) -> Dict[str, Any]:
    """Scan a library for new or updated files.
    
    Args:
        request: Scan parameters
        
    Returns:
        Dictionary with scan results
    """
    return await plex.scan_library(
        library_id=request.library_id,
        force=request.force
    )

class RefreshLibraryRequest(BaseModel):
    """Request model for refreshing a library."""
    library_id: str = Field(..., description="ID of the library to refresh")

@mcp_tool("plex.library.refresh")
async def refresh_library(plex: PlexService, request: RefreshLibraryRequest) -> bool:
    """Refresh metadata for a library.
    
    Args:
        request: Refresh parameters
        
    Returns:
        True if refresh was successful, False otherwise
    """
    return await plex.refresh_library_metadata(library_id=request.library_id)

class OptimizeLibraryRequest(BaseModel):
    """Request model for optimizing a library."""
    library_id: str = Field(..., description="ID of the library to optimize")

@mcp_tool("plex.library.optimize")
async def optimize_library(plex: PlexService, request: OptimizeLibraryRequest) -> bool:
    """Optimize a library database.
    
    Args:
        request: Optimization parameters
        
    Returns:
        True if optimization was successful, False otherwise
    """
    return await plex.optimize_library(library_id=request.library_id)

class GetLibraryRequest(BaseModel):
    """Request model for getting library information."""
    library_id: str = Field(..., description="ID of the library to retrieve")

@mcp_tool("plex.library.get")
async def get_library(plex: PlexService, request: GetLibraryRequest) -> Optional[LibrarySection]:
    """Get information about a specific library.
    
    Args:
        request: Library retrieval parameters
        
    Returns:
        Library information if found, None otherwise
    """
    return await plex.get_library(library_id=request.library_id)

@mcp_tool("plex.library.list")
async def list_libraries(plex: PlexService) -> List[LibrarySection]:
    """List all libraries.
    
    Returns:
        List of all libraries
    """
    return await plex.list_libraries()

class AddLibraryRequest(BaseModel):
    """Request model for adding a new library."""
    name: str = Field(..., description="Name of the new library")
    type: str = Field(..., description="Type of library (movie, show, music, photo)")
    agent: str = Field(..., description="Metadata agent to use")
    scanner: str = Field(..., description="Scanner to use")
    language: str = Field("en", description="Language for metadata")
    location: str = Field(..., description="Path to the library content")
    thumb: Optional[str] = Field(None, description="URL to a thumbnail image")

@mcp_tool("plex.library.add")
async def add_library(plex: PlexService, request: AddLibraryRequest) -> Optional[LibrarySection]:
    """Add a new library.
    
    Args:
        request: Library creation parameters
        
    Returns:
        The created library information if successful, None otherwise
    """
    return await plex.add_library(
        name=request.name,
        type=request.type,
        agent=request.agent,
        scanner=request.scanner,
        language=request.language,
        location=request.location,
        thumb=request.thumb
    )

class UpdateLibraryRequest(BaseModel):
    """Request model for updating a library."""
    library_id: str = Field(..., description="ID of the library to update")
    name: Optional[str] = Field(None, description="New name for the library")
    agent: Optional[str] = Field(None, description="New metadata agent")
    scanner: Optional[str] = Field(None, description="New scanner")
    language: Optional[str] = Field(None, description="New language for metadata")
    thumb: Optional[str] = Field(None, description="New thumbnail URL")

@mcp_tool("plex.library.update")
async def update_library(plex: PlexService, request: UpdateLibraryRequest) -> Optional[LibrarySection]:
    """Update a library's settings.
    
    Args:
        request: Library update parameters
        
    Returns:
        The updated library information if successful, None otherwise
    """
    return await plex.update_library(
        library_id=request.library_id,
        name=request.name,
        agent=request.agent,
        scanner=request.scanner,
        language=request.language,
        thumb=request.thumb
    )

class DeleteLibraryRequest(BaseModel):
    """Request model for deleting a library."""
    library_id: str = Field(..., description="ID of the library to delete")

@mcp_tool("plex.library.delete")
async def delete_library(plex: PlexService, request: DeleteLibraryRequest) -> bool:
    """Delete a library.
    
    Args:
        request: Library deletion parameters
        
    Returns:
        True if deletion was successful, False otherwise
    """
    return await plex.delete_library(library_id=request.library_id)

class AddLibraryLocationRequest(BaseModel):
    """Request model for adding a location to a library."""
    library_id: str = Field(..., description="ID of the library")
    path: str = Field(..., description="Path to add to the library")

@mcp_tool("plex.library.add_location")
async def add_library_location(plex: PlexService, request: AddLibraryLocationRequest) -> bool:
    """Add a location to a library.
    
    Args:
        request: Location addition parameters
        
    Returns:
        True if addition was successful, False otherwise
    """
    return await plex.add_library_location(
        library_id=request.library_id,
        path=request.path
    )

class RemoveLibraryLocationRequest(BaseModel):
    """Request model for removing a location from a library."""
    library_id: str = Field(..., description="ID of the library")
    path: str = Field(..., description="Path to remove from the library")

@mcp_tool("plex.library.remove_location")
async def remove_library_location(plex: PlexService, request: RemoveLibraryLocationRequest) -> bool:
    """Remove a location from a library.
    
    Args:
        request: Location removal parameters
        
    Returns:
        True if removal was successful, False otherwise
    """
    return await plex.remove_library_location(
        library_id=request.library_id,
        path=request.path
    )

class GetLibraryItemsRequest(BaseModel):
    """Request model for getting library items."""
    library_id: str = Field(..., description="ID of the library")
    limit: int = Field(100, description="Maximum number of items to return")
    offset: int = Field(0, description="Offset for pagination")
    sort: Optional[str] = Field(None, description="Sort field")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")

@mcp_tool("plex.library.get_items")
async def get_library_items(plex: PlexService, request: GetLibraryItemsRequest) -> List[MediaItem]:
    """Get items from a library.
    
    Args:
        request: Item retrieval parameters
        
    Returns:
        List of media items in the library
    """
    return await plex.get_library_items(
        library_id=request.library_id,
        limit=request.limit,
        offset=request.offset,
        sort=request.sort,
        filter=request.filter
    )

class EmptyTrashRequest(BaseModel):
    """Request model for emptying the trash."""
    library_id: str = Field(..., description="ID of the library")

@mcp_tool("plex.library.empty_trash")
async def empty_trash(plex: PlexService, request: EmptyTrashRequest) -> bool:
    """Empty the trash for a library.
    
    Args:
        request: Empty trash parameters
        
    Returns:
        True if successful, False otherwise
    """
    return await plex.empty_library_trash(library_id=request.library_id)

class CleanBundlesRequest(BaseModel):
    """Request model for cleaning bundles."""
    library_id: Optional[str] = Field(None, description="ID of the library (optional)")

@mcp_tool("plex.library.clean_bundles")
async def clean_bundles(plex: PlexService, request: CleanBundlesRequest) -> Dict[str, Any]:
    """Clean old bundles for a library or all libraries.
    
    Args:
        request: Clean bundles parameters
        
    Returns:
        Dictionary with cleanup results
    """
    return await plex.clean_library_bundles(library_id=request.library_id)

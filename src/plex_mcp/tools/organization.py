"""Plex media organization tools for FastMCP 2.10.1."""
from typing import List, Optional, Dict, Any

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.media import MediaItem, MediaType
from ..services.plex_service import PlexService

class OrganizeRequest(BaseModel):
    """Request model for organizing media."""
    library_id: str = Field(..., description="ID of the library to organize")
    dry_run: bool = Field(False, description="If True, only show what would be changed")
    patterns: Optional[Dict[str, str]] = Field(
        None,
        description="Custom patterns for organization"
    )

@mcp_tool("plex.organize.library")
async def organize_library(plex: PlexService, request: OrganizeRequest) -> Dict[str, Any]:
    """Organize a Plex library according to best practices.
    
    Args:
        request: Organization parameters
        
    Returns:
        Dictionary with organization results
    """
    return await plex.organize_library(
        library_id=request.library_id,
        dry_run=request.dry_run,
        patterns=request.patterns
    )

class AnalyzeLibraryRequest(BaseModel):
    """Request model for analyzing a library."""
    library_id: str = Field(..., description="ID of the library to analyze")

@mcp_tool("plex.organize.analyze")
async def analyze_library(plex: PlexService, request: AnalyzeLibraryRequest) -> Dict[str, Any]:
    """Analyze a library for organization issues.
    
    Args:
        request: Analysis parameters
        
    Returns:
        Dictionary with analysis results
    """
    return await plex.analyze_library(library_id=request.library_id)

class FixMatchRequest(BaseModel):
    """Request model for fixing media matches."""
    item_id: str = Field(..., description="ID of the item to fix")
    match_id: str = Field(..., description="Correct match ID")
    type: MediaType = Field(..., description="Type of media")

@mcp_tool("plex.organize.fix_match")
async def fix_media_match(plex: PlexService, request: FixMatchRequest) -> bool:
    """Fix an incorrect media match.
    
    Args:
        request: Fix match parameters
        
    Returns:
        True if the fix was successful, False otherwise
    """
    return await plex.fix_media_match(
        item_id=request.item_id,
        match_id=request.match_id,
        media_type=request.type
    )

class RefreshMetadataRequest(BaseModel):
    """Request model for refreshing metadata."""
    item_id: Optional[str] = Field(None, description="ID of the item to refresh")
    library_id: Optional[str] = Field(None, description="ID of the library to refresh")
    force: bool = Field(False, description="Force refresh even if not needed")

@mcp_tool("plex.organize.refresh_metadata")
async def refresh_metadata(plex: PlexService, request: RefreshMetadataRequest) -> Dict[str, Any]:
    """Refresh metadata for an item or library.
    
    Args:
        request: Refresh parameters
        
    Returns:
        Dictionary with refresh results
    """
    if request.item_id:
        return await plex.refresh_item_metadata(
            item_id=request.item_id,
            force=request.force
        )
    elif request.library_id:
        return await plex.refresh_library_metadata(
            library_id=request.library_id,
            force=request.force
        )
    else:
        raise ValueError("Either item_id or library_id must be provided")

class CleanBundlesRequest(BaseModel):
    """Request model for cleaning bundles."""
    dry_run: bool = Field(True, description="If True, only show what would be deleted")
    threshold_days: int = Field(30, description="Delete bundles older than this many days")

@mcp_tool("plex.organize.clean_bundles")
async def clean_bundles(plex: PlexService, request: CleanBundlesRequest) -> Dict[str, Any]:
    """Clean up old bundles to free up disk space.
    
    Args:
        request: Cleanup parameters
        
    Returns:
        Dictionary with cleanup results
    """
    return await plex.clean_bundles(
        dry_run=request.dry_run,
        threshold_days=request.threshold_days
    )

class OptimizeDatabaseRequest(BaseModel):
    """Request model for optimizing the database."""
    analyze: bool = Field(True, description="Run ANALYZE on the database")
    vacuum: bool = Field(True, description="Run VACUUM on the database")
    reindex: bool = Field(True, description="Rebuild indexes")

@mcp_tool("plex.organize.optimize_database")
async def optimize_database(plex: PlexService, request: OptimizeDatabaseRequest) -> Dict[str, Any]:
    """Optimize the Plex database.
    
    Args:
        request: Optimization parameters
        
    Returns:
        Dictionary with optimization results
    """
    return await plex.optimize_database(
        analyze=request.analyze,
        vacuum=request.vacuum,
        reindex=request.reindex
    )

"""Plex quality and transcoding tools for FastMCP 2.10.1."""
from typing import List, Optional, Dict, Any

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field

from ..models.quality import QualityProfile, TranscodingStatus, BandwidthAnalysis
from ..services.plex_service import PlexService

class GetTranscodeSettingsRequest(BaseModel):
    """Request model for getting transcode settings."""
    profile_name: Optional[str] = Field(None, description="Name of the quality profile to retrieve")

@mcp_tool("plex.quality.get_transcode_settings")
async def get_transcode_settings(
    plex: PlexService, 
    request: GetTranscodeSettingsRequest
) -> Dict[str, Any]:
    """Get current transcode settings for a quality profile.
    
    Args:
        request: Transcode settings parameters
        
    Returns:
        Dictionary with transcode settings
    """
    return await plex.get_transcode_settings(profile_name=request.profile_name)

class UpdateTranscodeSettingsRequest(BaseModel):
    """Request model for updating transcode settings."""
    profile_name: str = Field(..., description="Name of the quality profile to update")
    settings: Dict[str, Any] = Field(..., description="Dictionary of settings to update")

@mcp_tool("plex.quality.update_transcode_settings")
async def update_transcode_settings(
    plex: PlexService, 
    request: UpdateTranscodeSettingsRequest
) -> bool:
    """Update transcode settings for a quality profile.
    
    Args:
        request: Update parameters
        
    Returns:
        True if update was successful, False otherwise
    """
    return await plex.update_transcode_settings(
        profile_name=request.profile_name,
        settings=request.settings
    )

@mcp_tool("plex.quality.get_transcoding_status")
async def get_transcoding_status(plex: PlexService) -> TranscodingStatus:
    """Get current transcoding status.
    
    Returns:
        Current transcoding status information
    """
    return await plex.get_transcoding_status()

class GetBandwidthUsageRequest(BaseModel):
    """Request model for getting bandwidth usage."""
    time_range: str = Field("day", description="Time range for bandwidth data (hour, day, week, month)")

@mcp_tool("plex.quality.get_bandwidth_usage")
async def get_bandwidth_usage(
    plex: PlexService, 
    request: GetBandwidthUsageRequest
) -> BandwidthAnalysis:
    """Get bandwidth usage statistics.
    
    Args:
        request: Bandwidth query parameters
        
    Returns:
        Bandwidth usage analysis
    """
    return await plex.get_bandwidth_usage(time_range=request.time_range)

class SetStreamQualityRequest(BaseModel):
    """Request model for setting stream quality."""
    profile_name: str = Field(..., description="Name of the quality profile")
    quality: str = Field(..., description="Quality setting (e.g., '1080p', '720p', '480p')")
    bitrate: Optional[int] = Field(None, description="Maximum bitrate in kbps")

@mcp_tool("plex.quality.set_stream_quality")
async def set_stream_quality(
    plex: PlexService, 
    request: SetStreamQualityRequest
) -> bool:
    """Set streaming quality settings for a profile.
    
    Args:
        request: Quality settings
        
    Returns:
        True if update was successful, False otherwise
    """
    return await plex.set_stream_quality(
        profile_name=request.profile_name,
        quality=request.quality,
        bitrate=request.bitrate
    )

class GetThrottlingStatusRequest(BaseModel):
    """Request model for getting throttling status."""
    profile_name: Optional[str] = Field(None, description="Name of the quality profile")

@mcp_tool("plex.quality.get_throttling_status")
async def get_throttling_status(
    plex: PlexService,
    request: GetThrottlingStatusRequest
) -> Dict[str, Any]:
    """Get current throttling status and settings.
    
    Args:
        request: Throttling query parameters
        
    Returns:
        Dictionary with throttling status and settings
    """
    return await plex.get_throttling_status(profile_name=request.profile_name)

class SetThrottlingRequest(BaseModel):
    """Request model for setting throttling."""
    profile_name: str = Field(..., description="Name of the quality profile")
    enabled: bool = Field(..., description="Whether to enable throttling")
    download_limit: Optional[int] = Field(None, description="Download limit in kbps")
    upload_limit: Optional[int] = Field(None, description="Upload limit in kbps")

@mcp_tool("plex.quality.set_throttling")
async def set_throttling(
    plex: PlexService,
    request: SetThrottlingRequest
) -> bool:
    """Configure throttling settings.
    
    Args:
        request: Throttling configuration
        
    Returns:
        True if update was successful, False otherwise
    """
    return await plex.set_throttling(
        profile_name=request.profile_name,
        enabled=request.enabled,
        download_limit=request.download_limit,
        upload_limit=request.upload_limit
    )

@mcp_tool("plex.quality.list_quality_profiles")
async def list_quality_profiles(plex: PlexService) -> List[QualityProfile]:
    """List all available quality profiles.
    
    Returns:
        List of quality profiles
    """
    return await plex.list_quality_profiles()

class CreateQualityProfileRequest(BaseModel):
    """Request model for creating a quality profile."""
    name: str = Field(..., description="Name of the new profile")
    settings: Dict[str, Any] = Field(..., description="Profile settings")
    is_default: bool = Field(False, description="Set as default profile")

@mcp_tool("plex.quality.create_quality_profile")
async def create_quality_profile(
    plex: PlexService,
    request: CreateQualityProfileRequest
) -> bool:
    """Create a new quality profile.
    
    Args:
        request: Profile creation parameters
        
    Returns:
        True if creation was successful, False otherwise
    """
    return await plex.create_quality_profile(
        name=request.name,
        settings=request.settings,
        is_default=request.is_default
    )

class DeleteQualityProfileRequest(BaseModel):
    """Request model for deleting a quality profile."""
    profile_name: str = Field(..., description="Name of the profile to delete")

@mcp_tool("plex.quality.delete_quality_profile")
async def delete_quality_profile(
    plex: PlexService,
    request: DeleteQualityProfileRequest
) -> bool:
    """Delete a quality profile.
    
    Args:
        request: Profile deletion parameters
        
    Returns:
        True if deletion was successful, False otherwise
    """
    return await plex.delete_quality_profile(profile_name=request.profile_name)

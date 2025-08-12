"""
PlexMCP Models Package

This package contains all Pydantic models for the PlexMCP application,
organized into logical modules for better maintainability.
"""

# Core models
from .core import PlexServerStatus, MediaLibrary, MediaItem

# Playback models
from .playback import (
    PlexSession, PlexClient, RemotePlaybackRequest, 
    CastRequest, PlaybackControlResult
)

# Playlist models
from .playlists import PlexPlaylist, PlaylistCreateRequest, PlaylistAnalytics

# Quality models
from .quality import QualityProfile, TranscodingStatus, BandwidthAnalysis

# Admin models
from .admin import UserPermissions, ServerMaintenanceResult

# Vienna/Austrian context models
from .vienna import WienerRecommendation, EuropeanContent, AnimeSeasonInfo

__all__ = [
    # Core
    'PlexServerStatus', 'MediaLibrary', 'MediaItem',
    
    # Playback
    'PlexSession', 'PlexClient', 'RemotePlaybackRequest', 
    'CastRequest', 'PlaybackControlResult',
    
    # Playlists
    'PlexPlaylist', 'PlaylistCreateRequest', 'PlaylistAnalytics',
    
    # Quality
    'QualityProfile', 'TranscodingStatus', 'BandwidthAnalysis',
    
    # Admin
    'UserPermissions', 'ServerMaintenanceResult',
    
    # Vienna/Austrian context
    'WienerRecommendation', 'EuropeanContent', 'AnimeSeasonInfo'
]
"""
PlexMCP Models Package

This package contains all Pydantic models used throughout the PlexMCP application.
"""

# Core models
from .core import PlexServerStatus, MediaLibrary, MediaItem

# Playback models
from .playback import (
    PlexSession,
    PlexClient,
    RemotePlaybackRequest,
    CastRequest,
    PlaybackControlResult,
)

# Playlist models
from .playlists import PlexPlaylist, PlaylistCreateRequest, PlaylistAnalytics

# Quality and performance models
from .quality import QualityProfile, TranscodingStatus, BandwidthAnalysis

# Admin and user management models
from .admin import UserPermissions, ServerMaintenanceResult

# Vienna/Austrian context models
from .vienna import WienerRecommendation, EuropeanContent, AnimeSeasonInfo

__all__ = [
    # Core models
    'PlexServerStatus',
    'MediaLibrary',
    'MediaItem',
    
    # Playback models
    'PlexSession',
    'PlexClient',
    'RemotePlaybackRequest',
    'CastRequest',
    'PlaybackControlResult',
    
    # Playlist models
    'PlexPlaylist',
    'PlaylistCreateRequest',
    'PlaylistAnalytics',
    
    # Quality models
    'QualityProfile',
    'TranscodingStatus',
    'BandwidthAnalysis',
    
    # Admin models
    'UserPermissions',
    'ServerMaintenanceResult',
    
    # Vienna models
    'WienerRecommendation',
    'EuropeanContent',
    'AnimeSeasonInfo',
]
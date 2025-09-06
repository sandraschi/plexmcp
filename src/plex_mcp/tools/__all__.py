"""Plex MCP tools package."""

# Import all tool modules to register the tools
from . import (
    server, 
    media, 
    sessions,
    users,
    playlists,
    organization,
    quality,
    library
)

# Re-export the tools for easy importing
# Server tools
from .server import get_server_status, list_libraries, get_server_info

# Media tools
from .media import search_media, get_media_info, get_library_items

# Session tools
from .sessions import list_sessions, list_clients, control_playback

# User management tools
from .users import (
    create_user, update_user, delete_user, list_users, 
    get_user, update_user_permissions
)

# Playlist management tools
from .playlists import (
    create_playlist, get_playlist, list_playlists, update_playlist,
    delete_playlist, add_to_playlist, remove_from_playlist, get_playlist_analytics
)

# Media organization tools
from .organization import (
    organize_library, analyze_library, fix_media_match,
    refresh_metadata, clean_bundles, optimize_database
)

# Quality and transcoding tools
from .quality import (
    get_transcode_settings, update_transcode_settings,
    get_transcoding_status, get_bandwidth_usage, set_stream_quality,
    get_throttling_status, set_throttling, list_quality_profiles,
    create_quality_profile, delete_quality_profile
)

# Library management tools
from .library import (
    scan_library, refresh_library, optimize_library, get_library,
    list_libraries, add_library, update_library, delete_library,
    add_library_location, remove_library_location, get_library_items,
    empty_trash, clean_bundles as clean_library_bundles
)

__all__ = [
    # Server tools
    'get_server_status',
    'list_libraries',
    'get_server_info',
    
    # Media tools
    'search_media',
    'get_media_info',
    'get_library_items',
    
    # Session tools
    'list_sessions',
    'list_clients',
    'control_playback',
    
    # User management
    'create_user',
    'update_user',
    'delete_user',
    'list_users',
    'get_user',
    'update_user_permissions',
    
    # Playlist management
    'create_playlist',
    'get_playlist',
    'list_playlists',
    'update_playlist',
    'delete_playlist',
    'add_to_playlist',
    'remove_from_playlist',
    'get_playlist_analytics',
    
    # Media organization
    'organize_library',
    'analyze_library',
    'fix_media_match',
    'refresh_metadata',
    'clean_bundles',
    'optimize_database',
    
    # Quality and transcoding
    'get_transcode_settings',
    'update_transcode_settings',
    'get_transcoding_status',
    'get_bandwidth_usage',
    'set_stream_quality',
    'get_throttling_status',
    'set_throttling',
    'list_quality_profiles',
    'create_quality_profile',
    'delete_quality_profile',
    
    # Library management
    'scan_library',
    'refresh_library',
    'optimize_library',
    'get_library',
    'list_libraries',
    'add_library',
    'update_library',
    'delete_library',
    'add_library_location',
    'remove_library_location',
    'get_library_items',
    'empty_trash',
    'clean_library_bundles'
]

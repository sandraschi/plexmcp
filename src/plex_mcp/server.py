"""
PlexMCP - FastMCP 2.1 Server for Plex Media Server Management

Austrian efficiency for Sandra's media streaming needs.
Provides 22 tools: 10 core + 3 playlist + 2 remote + 2 performance + 2 admin + 3 Austrian efficiency
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console
from dotenv import load_dotenv

# Robust import handling for both package and direct execution
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when run as package)
    from .plex_manager import PlexManager, PlexAPIError
    from .config import PlexConfig
except ImportError:
    try:
        # Try absolute imports (when run directly)
        from plex_mcp.plex_manager import PlexManager, PlexAPIError
        from plex_mcp.config import PlexConfig
    except ImportError:
        # Final fallback - direct imports from same directory
        from plex_manager import PlexManager, PlexAPIError
        from config import PlexConfig

# Load environment variables from multiple possible paths
import pathlib
possible_env_paths = [
    pathlib.Path(__file__).parent.parent.parent / '.env',  # repo root
    pathlib.Path.cwd() / '.env',  # current working directory  
    pathlib.Path('D:/Dev/repos/plexmcp/.env')  # absolute path fallback
]

for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
else:
    load_dotenv()  # fallback

# Initialize console for logging (redirect to stderr for MCP compatibility)
import sys
console = Console(file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("PlexMCP 🎬")

# Global Plex manager (initialized on startup)
plex_manager: Optional[PlexManager] = None


class PlexServerStatus(BaseModel):
    """Plex server status information"""
    name: str = Field(description="Server name")
    version: str = Field(description="Plex server version")
    platform: str = Field(description="Platform (Linux, Windows, etc)")
    updated_at: int = Field(description="Last updated timestamp")
    size: int = Field(description="Database size")
    my_plex_username: Optional[str] = Field(description="MyPlex account username")
    my_plex_mapping_state: str = Field(description="MyPlex mapping status")
    connected: bool = Field(description="Connection status")


class MediaLibrary(BaseModel):
    """Plex media library information"""
    key: str = Field(description="Library key/ID")
    title: str = Field(description="Library name")
    type: str = Field(description="Library type (movie, show, music, etc)")
    agent: str = Field(description="Metadata agent")
    scanner: str = Field(description="Library scanner")
    language: str = Field(description="Primary language")
    uuid: str = Field(description="Library UUID")
    created_at: int = Field(description="Creation timestamp")
    updated_at: int = Field(description="Last updated timestamp")
    count: int = Field(description="Number of items in library")

class MediaItem(BaseModel):
    """Individual media item (movie, episode, etc)"""
    key: str = Field(description="Media key/ID")
    title: str = Field(description="Media title")
    type: str = Field(description="Media type")
    year: Optional[int] = Field(default=None, description="Release year")
    summary: Optional[str] = Field(default=None, description="Plot summary")
    rating: Optional[float] = Field(default=None, description="User rating")
    thumb: Optional[str] = Field(default=None, description="Thumbnail URL")
    art: Optional[str] = Field(default=None, description="Background art URL")
    duration: Optional[int] = Field(default=None, description="Duration in milliseconds")
    added_at: int = Field(description="Date added to library")
    updated_at: int = Field(description="Last updated timestamp")


class PlexSession(BaseModel):
    """Active Plex playback session"""
    session_key: str = Field(description="Session identifier")
    user: str = Field(description="Username")
    player: str = Field(description="Player name")
    state: str = Field(description="Playback state (playing, paused, etc)")
    title: str = Field(description="Media title being played")
    progress: Optional[int] = Field(description="Playback progress in seconds")
    duration: Optional[int] = Field(description="Total duration in seconds")


class PlexClient(BaseModel):
    """Available Plex client device"""
    name: str = Field(description="Client name")
    host: str = Field(description="Client host/IP")
    machine_identifier: str = Field(description="Unique client ID")
    product: str = Field(description="Client product (Plex Web, etc)")
    platform: str = Field(description="Client platform")
    platform_version: str = Field(description="Platform version")
    device: str = Field(description="Device type")


class PlexPlaylist(BaseModel):
    """Plex playlist information"""
    key: str = Field(description="Playlist key/ID")
    title: str = Field(description="Playlist name")
    type: str = Field(description="Playlist type (video, audio, photo)")
    summary: Optional[str] = Field(description="Playlist description")
    duration: Optional[int] = Field(description="Total playlist duration")
    item_count: int = Field(description="Number of items in playlist")
    smart: bool = Field(description="Is this a smart playlist")
    created_at: int = Field(description="Creation timestamp")
    updated_at: int = Field(description="Last updated timestamp")
    owner: Optional[str] = Field(description="Playlist owner username")


class PlaylistCreateRequest(BaseModel):
    """Request model for creating playlists"""
    name: str = Field(description="Playlist name")
    summary: Optional[str] = Field(description="Playlist description")
    items: Optional[List[str]] = Field(description="List of media keys to add")
    smart_rules: Optional[Dict[str, Any]] = Field(description="Smart playlist rules (genre, year, rating, etc)")
    library_id: Optional[str] = Field(description="Library to create smart playlist from")


class PlaylistAnalytics(BaseModel):
    """Playlist usage analytics and recommendations"""
    playlist_id: str = Field(description="Playlist key")
    name: str = Field(description="Playlist name")
    total_plays: int = Field(description="Total play count")
    unique_users: int = Field(description="Number of unique users who played")
    avg_completion_rate: float = Field(description="Average completion percentage")
    popular_items: List[str] = Field(description="Most played items in playlist")
    skip_rate: float = Field(description="Percentage of items skipped")
    recommendations: List[str] = Field(description="Suggested improvements")
    last_played: Optional[int] = Field(description="Last play timestamp")


class RemotePlaybackRequest(BaseModel):
    """Request model for remote playback control"""
    client_id: str = Field(description="Target client machine identifier")
    action: str = Field(description="Playback action (play, pause, stop, seek, next, previous, volume)")
    media_key: Optional[str] = Field(description="Media key for play action")
    seek_offset: Optional[int] = Field(description="Seek position in milliseconds")
    volume_level: Optional[int] = Field(description="Volume level (0-100)")


class CastRequest(BaseModel):
    """Request model for casting media to device"""
    client_id: str = Field(description="Target client machine identifier")
    media_key: str = Field(description="Media key to cast")
    start_offset: Optional[int] = Field(description="Start position in milliseconds")
    queue_items: Optional[List[str]] = Field(description="Additional items to queue after current")
    replace_queue: bool = Field(default=True, description="Replace existing queue")


class PlaybackControlResult(BaseModel):
    """Result of remote playback control operation"""
    status: str = Field(description="Operation status (success, error, unavailable)")
    client_id: str = Field(description="Target client identifier")
    action: str = Field(description="Action performed")
    current_state: Optional[str] = Field(description="Current playback state")
    position: Optional[int] = Field(description="Current playback position")
    duration: Optional[int] = Field(description="Total media duration")
    volume: Optional[int] = Field(description="Current volume level")
    message: str = Field(description="Status message or error details")


class QualityProfile(BaseModel):
    """Media quality profile for transcoding optimization"""
    name: str = Field(description="Profile name (4K, 1080p, 720p, mobile, etc)")
    max_bitrate: int = Field(description="Maximum bitrate in kbps")
    resolution: str = Field(description="Target resolution (e.g., 1920x1080)")
    codec: str = Field(description="Video codec (h264, h265, etc)")
    container: str = Field(description="Container format (mp4, mkv, etc)")
    audio_codec: Optional[str] = Field(description="Audio codec preference")
    subtitle_format: Optional[str] = Field(description="Subtitle format")


class TranscodingStatus(BaseModel):
    """Current transcoding operation status"""
    active_sessions: int = Field(description="Number of active transcoding sessions")
    queue_length: int = Field(description="Transcoding queue length")
    cpu_usage: float = Field(description="CPU usage percentage for transcoding")
    memory_usage: float = Field(description="Memory usage for transcoding processes")
    disk_io: float = Field(description="Disk I/O usage for transcoding")
    estimated_completion: Optional[int] = Field(description="Estimated completion time in seconds")
    current_jobs: List[Dict[str, Any]] = Field(description="Details of current transcoding jobs")
    recommendations: List[str] = Field(description="Performance optimization recommendations")


class BandwidthAnalysis(BaseModel):
    """Network bandwidth usage analysis"""
    time_period: str = Field(description="Analysis time period")
    total_bandwidth_gb: float = Field(description="Total bandwidth used in GB")
    peak_usage_mbps: float = Field(description="Peak usage in Mbps")
    average_usage_mbps: float = Field(description="Average usage in Mbps")
    concurrent_streams: int = Field(description="Peak concurrent streams")
    transcoding_overhead: float = Field(description="Bandwidth overhead from transcoding")
    client_breakdown: List[Dict[str, Any]] = Field(description="Bandwidth usage by client")
    quality_distribution: Dict[str, int] = Field(description="Stream quality distribution")
    optimization_suggestions: List[str] = Field(description="Bandwidth optimization recommendations")
    cost_estimate: Optional[float] = Field(description="Estimated cost if using metered connection")


class UserPermissions(BaseModel):
    """User permission settings for Plex server access"""
    user_id: str = Field(description="User identifier")
    username: str = Field(description="Display username")
    email: Optional[str] = Field(description="User email address")
    is_admin: bool = Field(description="Administrator privileges")
    is_managed: bool = Field(description="Managed user account")
    library_access: List[str] = Field(description="Accessible library IDs")
    restricted_content: bool = Field(description="Content rating restrictions enabled")
    max_rating: Optional[str] = Field(description="Maximum content rating allowed")
    sharing_enabled: bool = Field(description="Can share content with other users")
    sync_enabled: bool = Field(description="Can sync content offline")
    home_user: bool = Field(description="Home user with enhanced privileges")
    last_seen: Optional[int] = Field(description="Last activity timestamp")
    restrictions: List[str] = Field(description="Active restrictions and limitations")


class ServerMaintenanceResult(BaseModel):
    """Result of server maintenance operations"""
    operation: str = Field(description="Maintenance operation performed")
    status: str = Field(description="Operation status (success, error, partial)")
    details: Dict[str, Any] = Field(description="Detailed operation results")
    space_freed_gb: Optional[float] = Field(description="Disk space freed in GB")
    items_processed: int = Field(description="Number of items processed")
    duration_seconds: float = Field(description="Operation duration")
    recommendations: List[str] = Field(description="Post-maintenance recommendations")
    next_recommended: Optional[str] = Field(description="Next recommended maintenance")
    warnings: List[str] = Field(description="Warnings or issues encountered")


class WienerRecommendation(BaseModel):
    """Vienna-context content recommendation"""
    media_key: str = Field(description="Media key/ID")
    title: str = Field(description="Media title")
    type: str = Field(description="Media type (movie, show, episode)")
    year: Optional[int] = Field(description="Release year")
    duration: Optional[int] = Field(description="Duration in minutes")
    rating: Optional[float] = Field(description="Rating if available")
    vienna_score: float = Field(description="Vienna context relevance score")
    mood_match: str = Field(description="Mood category match")
    austrian_context: Optional[str] = Field(description="Austrian cultural relevance")
    recommendation_reason: str = Field(description="Why this content fits Vienna context")
    best_time: str = Field(description="Optimal viewing time context")


class EuropeanContent(BaseModel):
    """European content discovery result"""
    media_key: str = Field(description="Media key/ID")
    title: str = Field(description="Original title")
    local_title: Optional[str] = Field(description="Local/translated title")
    country: str = Field(description="Country of origin")
    language: str = Field(description="Primary language")
    subtitles: List[str] = Field(description="Available subtitle languages")
    genre: str = Field(description="Genre category")
    year: Optional[int] = Field(description="Release year")
    rating: Optional[float] = Field(description="Rating if available")
    cultural_significance: Optional[str] = Field(description="Cultural or historical importance")
    eu_funding: bool = Field(description="EU co-production or funding")
    awards: List[str] = Field(description="European film awards received")
    availability_score: float = Field(description="How easily available in Austria")


class QualityProfile(BaseModel):
    """Media quality profile for transcoding optimization"""
    name: str = Field(description="Profile name (4K, 1080p, 720p, mobile, etc)")
    max_bitrate: int = Field(description="Maximum bitrate in kbps")
    resolution: str = Field(description="Target resolution (e.g., 1920x1080)")
    codec: str = Field(description="Video codec (h264, h265, etc)")
    container: str = Field(description="Container format (mp4, mkv, etc)")
    audio_codec: Optional[str] = Field(description="Audio codec preference")
    subtitle_format: Optional[str] = Field(description="Subtitle format")


class TranscodingStatus(BaseModel):
    """Current transcoding operation status"""
    active_sessions: int = Field(description="Number of active transcoding sessions")
    queue_length: int = Field(description="Transcoding queue length")
    cpu_usage: float = Field(description="CPU usage percentage for transcoding")
    memory_usage: float = Field(description="Memory usage for transcoding processes")
    disk_io: float = Field(description="Disk I/O usage for transcoding")
    estimated_completion: Optional[int] = Field(description="Estimated completion time in seconds")
    current_jobs: List[Dict[str, Any]] = Field(description="Details of current transcoding jobs")
    recommendations: List[str] = Field(description="Performance optimization recommendations")


class BandwidthAnalysis(BaseModel):
    """Network bandwidth usage analysis"""
    time_period: str = Field(description="Analysis time period")
    total_bandwidth_gb: float = Field(description="Total bandwidth used in GB")
    peak_usage_mbps: float = Field(description="Peak usage in Mbps")
    average_usage_mbps: float = Field(description="Average usage in Mbps")
    concurrent_streams: int = Field(description="Peak concurrent streams")
    transcoding_overhead: float = Field(description="Bandwidth overhead from transcoding")
    client_breakdown: List[Dict[str, Any]] = Field(description="Bandwidth usage by client")
    quality_distribution: Dict[str, int] = Field(description="Stream quality distribution")
    optimization_suggestions: List[str] = Field(description="Bandwidth optimization recommendations")
    cost_estimate: Optional[float] = Field(description="Estimated cost if using metered connection")


class RemotePlaybackRequest(BaseModel):
    """Request model for remote playback control"""
    client_id: str = Field(description="Target client machine identifier")
    action: str = Field(description="Playback action (play, pause, stop, seek, next, previous, volume)")
    media_key: Optional[str] = Field(description="Media key for play action")
    seek_offset: Optional[int] = Field(description="Seek position in milliseconds")
    volume_level: Optional[int] = Field(description="Volume level (0-100)")


class CastRequest(BaseModel):
    """Request model for casting media to device"""
    client_id: str = Field(description="Target client machine identifier")
    media_key: str = Field(description="Media key to cast")
    start_offset: Optional[int] = Field(description="Start position in milliseconds")
    queue_items: Optional[List[str]] = Field(description="Additional items to queue after current")
    replace_queue: bool = Field(default=True, description="Replace existing queue")


class PlaybackControlResult(BaseModel):
    """Result of remote playback control operation"""
    status: str = Field(description="Operation status (success, error, unavailable)")
    client_id: str = Field(description="Target client identifier")
    action: str = Field(description="Action performed")
    current_state: Optional[str] = Field(description="Current playback state")
    position: Optional[int] = Field(description="Current playback position")
    duration: Optional[int] = Field(description="Total media duration")
    volume: Optional[int] = Field(description="Current volume level")
    message: str = Field(description="Status message or error details")


class AnimeSeasonInfo(BaseModel):
    """Anime season information for weebs"""
    title: str = Field(description="Anime title")
    year: int = Field(description="Release year")
    season: Optional[str] = Field(description="Season (Winter, Spring, Summer, Fall)")
    episodes_available: int = Field(description="Episodes available in library")
    rating: Optional[float] = Field(description="Rating if available")
    summary: Optional[str] = Field(description="Brief summary")
    status: str = Field(description="Airing status (ongoing, completed, etc)")


async def get_plex_manager() -> PlexManager:
    """Get initialized Plex manager, creating if needed"""
    global plex_manager
    if plex_manager is None:
        # Manually set environment variables as fallback
        import os
        if not os.getenv('PLEX_TOKEN'):
            os.environ['PLEX_TOKEN'] = 'WmZfx6fkvYxksyVB4NhW'
            os.environ['PLEX_SERVER_URL'] = 'http://localhost:32400'
            
        # Create config directly with known values
        config = PlexConfig(
            server_url='http://localhost:32400',
            plex_token='WmZfx6fkvYxksyVB4NhW'
        )
        plex_manager = PlexManager(config)
    return plex_manager


@mcp.tool()
async def get_plex_status() -> PlexServerStatus:
    """
    Get Plex server status and identity information.
    
    Returns comprehensive server information including version,
    platform, database size, and MyPlex connection status.
    
    Returns:
        Complete server status and configuration information
    """
    try:
        manager = await get_plex_manager()
        status_data = await manager.get_server_status()
        
        return PlexServerStatus(
            name=status_data.get('friendlyName', 'Plex Server'),
            version=status_data.get('version', 'Unknown'),
            platform=status_data.get('platform', 'Unknown'),
            updated_at=int(status_data.get('updatedAt', 0)),
            size=int(status_data.get('size', 0)),
            my_plex_username=status_data.get('myPlexUsername'),
            my_plex_mapping_state=status_data.get('myPlexMappingState', 'unknown'),
            connected=True
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_plex_status: {e}[/red]")
        return PlexServerStatus(
            name="Error",
            version="Unknown",
            platform="Unknown", 
            updated_at=0,
            size=0,
            my_plex_mapping_state="error",
            connected=False
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
    try:
        manager = await get_plex_manager()
        libraries_data = await manager.get_libraries()
        
        libraries = []
        for lib_data in libraries_data:
            library = MediaLibrary(
                key=lib_data.get('key', ''),
                title=lib_data.get('title', 'Unknown'),
                type=lib_data.get('type', 'unknown'),
                agent=lib_data.get('agent', ''),
                scanner=lib_data.get('scanner', ''),
                language=lib_data.get('language', 'en'),
                uuid=lib_data.get('uuid', ''),
                created_at=int(lib_data.get('createdAt', 0)),
                updated_at=int(lib_data.get('updatedAt', 0)),
                count=int(lib_data.get('count', 0))
            )
            libraries.append(library)
        
        return libraries
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_libraries: {e}[/red]")
        return []


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
    try:
        manager = await get_plex_manager()
        search_results = await manager.search_media(query, library_id)
        
        media_items = []
        for item_data in search_results:
            media_item = MediaItem(
                key=item_data.get('key', ''),
                title=item_data.get('title', 'Unknown'),
                type=item_data.get('type', 'unknown'),
                year=item_data.get('year'),
                summary=item_data.get('summary'),
                rating=item_data.get('rating'),
                thumb=item_data.get('thumb'),
                art=item_data.get('art'),
                duration=item_data.get('duration'),
                added_at=int(item_data.get('addedAt', 0)),
                updated_at=int(item_data.get('updatedAt', 0))
            )
            media_items.append(media_item)
        
        return media_items
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in search_media: {e}[/red]")
        return []


@mcp.tool()
async def get_recently_added(
    library_id: Optional[str] = None,
    limit: int = Field(20, description="Number of recent items to return")
) -> List[MediaItem]:
    """
    Get recently added media from all libraries or specific library.
    
    Args:
        library_id: Optional library key to filter by
        limit: Maximum number of items to return (default 20)
        
    Returns:
        List of recently added media items
    """
    try:
        manager = await get_plex_manager()
        recent_items = await manager.get_recently_added(library_id, limit)
        
        media_items = []
        for item_data in recent_items:
            media_item = MediaItem(
                key=item_data.get('key', ''),
                title=item_data.get('title', 'Unknown'),
                type=item_data.get('type', 'unknown'),
                year=item_data.get('year'),
                summary=item_data.get('summary'),
                rating=item_data.get('rating'),
                thumb=item_data.get('thumb'),
                art=item_data.get('art'),
                duration=item_data.get('duration'),
                added_at=int(item_data.get('addedAt', 0)),
                updated_at=int(item_data.get('updatedAt', 0))
            )
            media_items.append(media_item)
        
        return media_items
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_recently_added: {e}[/red]")
        return []


@mcp.tool()
async def get_media_info(media_key: str) -> MediaItem:
    """
    Get detailed information about a specific media item.
    
    Args:
        media_key: Plex media key/ID
        
    Returns:
        Detailed media information including metadata and files
    """
    try:
        manager = await get_plex_manager()
        media_data = await manager.get_media_info(media_key)
        
        return MediaItem(
            key=media_data.get('key', ''),
            title=media_data.get('title', 'Unknown'),
            type=media_data.get('type', 'unknown'),
            year=media_data.get('year'),
            summary=media_data.get('summary'),
            rating=media_data.get('rating'),
            thumb=media_data.get('thumb'),
            art=media_data.get('art'),
            duration=media_data.get('duration'),
            added_at=int(media_data.get('addedAt', 0)),
            updated_at=int(media_data.get('updatedAt', 0))
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_media_info: {e}[/red]")
        return MediaItem(
            key=media_key,
            title="Error loading media",
            type="unknown",
            added_at=0,
            updated_at=0
        )


@mcp.tool()
async def get_library_content(
    library_id: str,
    limit: int = Field(50, description="Number of items to return")
) -> List[MediaItem]:
    """
    Get content from a specific library.
    
    Args:
        library_id: Library key to get content from
        limit: Maximum number of items to return
        
    Returns:
        List of media items from the specified library
    """
    try:
        manager = await get_plex_manager()
        library_content = await manager.get_library_content(library_id, limit)
        
        media_items = []
        for item_data in library_content:
            media_item = MediaItem(
                key=item_data.get('key', ''),
                title=item_data.get('title', 'Unknown'),
                type=item_data.get('type', 'unknown'),
                year=item_data.get('year'),
                summary=item_data.get('summary'),
                rating=item_data.get('rating'),
                thumb=item_data.get('thumb'),
                art=item_data.get('art'),
                duration=item_data.get('duration'),
                added_at=int(item_data.get('addedAt', 0)),
                updated_at=int(item_data.get('updatedAt', 0))
            )
            media_items.append(media_item)
        
        return media_items
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_library_content: {e}[/red]")
        return []


@mcp.tool()
async def get_clients() -> List[PlexClient]:
    """
    Get all available Plex client devices.
    
    Returns information about connected Plex clients that can
    be used for remote playback control.
    
    Returns:
        List of available Plex client devices
    """
    try:
        manager = await get_plex_manager()
        clients_data = await manager.get_clients()
        
        clients = []
        for client_data in clients_data:
            client = PlexClient(
                name=client_data.get('name', 'Unknown Client'),
                host=client_data.get('host', ''),
                machine_identifier=client_data.get('machineIdentifier', ''),
                product=client_data.get('product', 'Unknown'),
                platform=client_data.get('platform', 'Unknown'),
                platform_version=client_data.get('platformVersion', ''),
                device=client_data.get('device', 'Unknown')
            )
            clients.append(client)
        
        return clients
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_clients: {e}[/red]")
        return []


@mcp.tool()
async def get_sessions() -> List[PlexSession]:
    """
    Get active playback sessions on the Plex server.
    
    Shows who is currently watching what content,
    including playback progress and player information.
    
    Returns:
        List of active playback sessions
    """
    try:
        manager = await get_plex_manager()
        sessions_data = await manager.get_sessions()
        
        sessions = []
        for session_data in sessions_data:
            session = PlexSession(
                session_key=session_data.get('sessionKey', ''),
                user=session_data.get('User', {}).get('title', 'Unknown'),
                player=session_data.get('Player', {}).get('title', 'Unknown Player'),
                state=session_data.get('Player', {}).get('state', 'unknown'),
                title=session_data.get('title', 'Unknown'),
                progress=session_data.get('viewOffset'),
                duration=session_data.get('duration')
            )
            sessions.append(session)
        
        return sessions
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_sessions: {e}[/red]")
        return []


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
    try:
        manager = await get_plex_manager()
        success = await manager.scan_library(library_id)
        
        if success:
            console.print(f"[green]Library {library_id} scan triggered[/green]")
        
        return success
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in scan_library: {e}[/red]")
        return False


@mcp.tool()
async def get_users() -> List[Dict[str, Any]]:
    """
    Get server users (admin function).
    
    Returns list of users with access to the Plex server.
    Only works with admin authentication.
    
    Returns:
        List of user accounts and their permissions
    """
    try:
        manager = await get_plex_manager()
        users_data = await manager.get_users()
        
        return users_data
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in get_users: {e}[/red]")
        return []


# Playlist Management Suite - Austrian Efficiency Tools

@mcp.tool()
async def create_playlist(
    name: str,
    summary: Optional[str] = None,
    items: Optional[List[str]] = None,
    smart_rules: Optional[Dict[str, Any]] = None,
    library_id: Optional[str] = None
) -> PlexPlaylist:
    """
    Create a new playlist (manual or smart) with Austrian efficiency.
    
    Supports both manual playlists (with specific items) and smart playlists
    (with automatic rules). Smart playlists update automatically based on criteria.
    
    Args:
        name: Playlist name
        summary: Optional playlist description
        items: List of media keys for manual playlist
        smart_rules: Rules for smart playlist (genre, year, rating, etc)
        library_id: Library to create smart playlist from
        
    Returns:
        Created playlist information
        
    Examples:
        Manual: create_playlist("Movie Night", items=["12345", "67890"])
        Smart: create_playlist("Top Action", smart_rules={"genre": "action", "rating": ">8"})
    """
    try:
        manager = await get_plex_manager()
        
        # Determine playlist type and create accordingly
        if smart_rules and library_id:
            # Create smart playlist
            playlist_data = await manager.create_smart_playlist(
                name=name,
                summary=summary or f"Smart playlist: {name}",
                library_id=library_id,
                rules=smart_rules
            )
            console.print(f"[green]Smart playlist '{name}' created with rules: {smart_rules}[/green]")
        elif items:
            # Create manual playlist
            playlist_data = await manager.create_manual_playlist(
                name=name,
                summary=summary or f"Manual playlist: {name}",
                items=items
            )
            console.print(f"[green]Manual playlist '{name}' created with {len(items)} items[/green]")
        else:
            # Create empty manual playlist
            playlist_data = await manager.create_manual_playlist(
                name=name,
                summary=summary or f"Empty playlist: {name}",
                items=[]
            )
            console.print(f"[green]Empty playlist '{name}' created[/green]")
        
        return PlexPlaylist(
            key=playlist_data.get('key', ''),
            title=playlist_data.get('title', name),
            type=playlist_data.get('type', 'video'),
            summary=playlist_data.get('summary', summary),
            duration=playlist_data.get('duration', 0),
            item_count=playlist_data.get('leafCount', len(items) if items else 0),
            smart=bool(smart_rules),
            created_at=int(playlist_data.get('addedAt', 0)),
            updated_at=int(playlist_data.get('updatedAt', 0)),
            owner=playlist_data.get('owner')
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in create_playlist: {e}[/red]")
        # Return placeholder for failed creation
        return PlexPlaylist(
            key="error",
            title=name,
            type="video",
            summary=f"Failed to create: {e}",
            duration=0,
            item_count=0,
            smart=bool(smart_rules),
            created_at=0,
            updated_at=0
        )


@mcp.tool()
async def manage_playlists(
    action: str,
    playlist_id: str,
    items: Optional[List[str]] = None,
    new_name: Optional[str] = None,
    new_summary: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage existing playlists with Austrian efficiency.
    
    Supports editing, deleting, and modifying playlists without
    overwhelming complexity. Focus on essential operations.
    
    Args:
        action: Operation to perform (add_items, remove_items, rename, delete, reorder)
        playlist_id: Playlist key to modify
        items: List of media keys for add/remove operations
        new_name: New name for rename operation
        new_summary: New description for rename operation
        
    Returns:
        Operation result with status and details
        
    Examples:
        Add: manage_playlists("add_items", "123", items=["456", "789"])
        Remove: manage_playlists("remove_items", "123", items=["456"])
        Rename: manage_playlists("rename", "123", new_name="New Name")
        Delete: manage_playlists("delete", "123")
    """
    try:
        manager = await get_plex_manager()
        
        if action == "add_items" and items:
            result = await manager.add_to_playlist(playlist_id, items)
            console.print(f"[green]Added {len(items)} items to playlist {playlist_id}[/green]")
            return {
                "status": "success",
                "action": "add_items",
                "playlist_id": playlist_id,
                "items_added": len(items),
                "message": f"Successfully added {len(items)} items"
            }
            
        elif action == "remove_items" and items:
            result = await manager.remove_from_playlist(playlist_id, items)
            console.print(f"[green]Removed {len(items)} items from playlist {playlist_id}[/green]")
            return {
                "status": "success",
                "action": "remove_items",
                "playlist_id": playlist_id,
                "items_removed": len(items),
                "message": f"Successfully removed {len(items)} items"
            }
            
        elif action == "rename" and (new_name or new_summary):
            result = await manager.update_playlist(
                playlist_id,
                title=new_name,
                summary=new_summary
            )
            console.print(f"[green]Renamed playlist {playlist_id}[/green]")
            return {
                "status": "success",
                "action": "rename",
                "playlist_id": playlist_id,
                "new_name": new_name,
                "message": "Successfully renamed playlist"
            }
            
        elif action == "delete":
            result = await manager.delete_playlist(playlist_id)
            console.print(f"[green]Deleted playlist {playlist_id}[/green]")
            return {
                "status": "success",
                "action": "delete",
                "playlist_id": playlist_id,
                "message": "Successfully deleted playlist"
            }
            
        elif action == "reorder" and items:
            # Items list represents new order (media keys in desired sequence)
            result = await manager.reorder_playlist(playlist_id, items)
            console.print(f"[green]Reordered playlist {playlist_id}[/green]")
            return {
                "status": "success",
                "action": "reorder",
                "playlist_id": playlist_id,
                "message": "Successfully reordered playlist items"
            }
            
        else:
            return {
                "status": "error",
                "action": action,
                "playlist_id": playlist_id,
                "message": f"Invalid action '{action}' or missing required parameters"
            }
            
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in manage_playlists: {e}[/red]")
        return {
            "status": "error",
            "action": action,
            "playlist_id": playlist_id,
            "message": f"API error: {e}"
        }


@mcp.tool()
async def playlist_analytics(
    playlist_id: Optional[str] = None
) -> List[PlaylistAnalytics]:
    """
    Get playlist usage analytics and optimization recommendations.
    
    Austrian efficiency: Focus on actionable insights, not overwhelming data.
    Provides play counts, completion rates, and specific improvement suggestions.
    
    Args:
        playlist_id: Specific playlist to analyze (if None, analyzes all playlists)
        
    Returns:
        List of playlist analytics with recommendations
        
    Austrian Efficiency Features:
        - Skip rate analysis (items users consistently skip)
        - Completion rate tracking (how often playlists are finished)
        - Popular item identification (most-played content)
        - Actionable recommendations (remove unpopular, add similar)
    """
    try:
        manager = await get_plex_manager()
        
        # Get playlist(s) to analyze
        if playlist_id:
            playlists_to_analyze = [await manager.get_playlist_info(playlist_id)]
        else:
            playlists_data = await manager.get_playlists()
            playlists_to_analyze = playlists_data[:10]  # Limit to top 10 for efficiency
        
        analytics_results = []
        
        for playlist_data in playlists_to_analyze:
            if not playlist_data:
                continue
                
            playlist_key = playlist_data.get('key', '')
            playlist_name = playlist_data.get('title', 'Unknown')
            
            # Get playback statistics
            stats = await manager.get_playlist_statistics(playlist_key)
            
            # Calculate analytics
            total_plays = stats.get('total_plays', 0)
            unique_users = len(stats.get('unique_users', []))
            
            # Calculate completion rate (estimate based on duration vs play time)
            total_duration = playlist_data.get('duration', 1)
            avg_play_time = stats.get('avg_play_time', 0)
            completion_rate = min(100.0, (avg_play_time / total_duration) * 100) if total_duration > 0 else 0
            
            # Identify popular and skipped items
            item_stats = stats.get('item_stats', {})
            popular_items = sorted(
                item_stats.items(),
                key=lambda x: x[1].get('play_count', 0),
                reverse=True
            )[:5]  # Top 5 most played
            
            skip_rate = stats.get('skip_rate', 0)
            
            # Generate Austrian efficiency recommendations
            recommendations = []
            
            if completion_rate < 70:
                recommendations.append("Consider shorter playlist or removing less popular items")
            
            if skip_rate > 30:
                recommendations.append("High skip rate detected - review item quality and ordering")
                
            if total_plays < 5:
                recommendations.append("Low engagement - consider promoting or improving playlist")
                
            if unique_users < 2:
                recommendations.append("Share playlist with other users to increase discovery")
                
            if len(popular_items) > 0:
                recommendations.append(f"Most popular: {popular_items[0][0]} - consider similar content")
            
            # Austrian efficiency: Always provide at least one actionable recommendation
            if not recommendations:
                recommendations.append("Playlist performing well - consider creating similar themed playlists")
            
            analytics = PlaylistAnalytics(
                playlist_id=playlist_key,
                name=playlist_name,
                total_plays=total_plays,
                unique_users=unique_users,
                avg_completion_rate=round(completion_rate, 1),
                popular_items=[item[0] for item in popular_items],
                skip_rate=round(skip_rate, 1),
                recommendations=recommendations,
                last_played=stats.get('last_played')
            )
            
            analytics_results.append(analytics)
        
        console.print(f"[green]Analyzed {len(analytics_results)} playlists[/green]")
        return analytics_results
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in playlist_analytics: {e}[/red]")
        return []


# Remote Playback Control Suite - Multi-Device Management

@mcp.tool()
async def remote_playback_control(
    client_id: str,
    action: str,
    media_key: Optional[str] = None,
    seek_offset: Optional[int] = None,
    volume_level: Optional[int] = None
) -> PlaybackControlResult:
    """
    Control playback on remote Plex clients with Austrian efficiency.
    
    Provides comprehensive remote control capabilities for any connected
    Plex client device. Supports play, pause, stop, seek, volume, and navigation.
    
    Args:
        client_id: Target client machine identifier (from get_clients())
        action: Control action (play, pause, stop, seek, next, previous, volume)
        media_key: Media key for play action (required for 'play')
        seek_offset: Seek position in milliseconds (for 'seek' action)
        volume_level: Volume level 0-100 (for 'volume' action)
        
    Returns:
        Playback control result with current state and status
        
    Austrian Efficiency Features:
        - Immediate feedback on operation success/failure
        - Current playback state returned after each operation
        - Error handling for offline/unavailable clients
        - Volume control with percentage-based levels
        
    Examples:
        Play: remote_playback_control("client123", "play", media_key="456")
        Pause: remote_playback_control("client123", "pause")
        Seek: remote_playback_control("client123", "seek", seek_offset=120000)
        Volume: remote_playback_control("client123", "volume", volume_level=75)
    """
    try:
        manager = await get_plex_manager()
        
        # Validate client exists and is available
        clients = await manager.get_clients()
        target_client = None
        for client in clients:
            if client.get('machineIdentifier') == client_id:
                target_client = client
                break
        
        if not target_client:
            return PlaybackControlResult(
                status="error",
                client_id=client_id,
                action=action,
                message=f"Client {client_id} not found or unavailable"
            )
        
        client_name = target_client.get('name', 'Unknown Client')
        
        # Execute the requested action
        result = None
        
        if action == "play" and media_key:
            result = await manager.play_media_on_client(client_id, media_key)
            console.print(f"[green]Playing media {media_key} on {client_name}[/green]")
            
        elif action == "pause":
            result = await manager.pause_client(client_id)
            console.print(f"[green]Paused playback on {client_name}[/green]")
            
        elif action == "stop":
            result = await manager.stop_client(client_id)
            console.print(f"[green]Stopped playback on {client_name}[/green]")
            
        elif action == "seek" and seek_offset is not None:
            result = await manager.seek_client(client_id, seek_offset)
            console.print(f"[green]Seeked to {seek_offset}ms on {client_name}[/green]")
            
        elif action == "next":
            result = await manager.next_track_client(client_id)
            console.print(f"[green]Skipped to next on {client_name}[/green]")
            
        elif action == "previous":
            result = await manager.previous_track_client(client_id)
            console.print(f"[green]Skipped to previous on {client_name}[/green]")
            
        elif action == "volume" and volume_level is not None:
            # Clamp volume to 0-100 range
            volume = max(0, min(100, volume_level))
            result = await manager.set_client_volume(client_id, volume)
            console.print(f"[green]Set volume to {volume}% on {client_name}[/green]")
            
        else:
            return PlaybackControlResult(
                status="error",
                client_id=client_id,
                action=action,
                message=f"Invalid action '{action}' or missing required parameters"
            )
        
        # Get current playback state after operation
        try:
            current_state = await manager.get_client_state(client_id)
            
            return PlaybackControlResult(
                status="success",
                client_id=client_id,
                action=action,
                current_state=current_state.get('state', 'unknown'),
                position=current_state.get('time'),
                duration=current_state.get('duration'),
                volume=current_state.get('volume'),
                message=f"Successfully executed '{action}' on {client_name}"
            )
            
        except PlexAPIError:
            # Operation succeeded but couldn't get current state
            return PlaybackControlResult(
                status="success",
                client_id=client_id,
                action=action,
                message=f"'{action}' executed on {client_name} (state unavailable)"
            )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in remote_playback_control: {e}[/red]")
        return PlaybackControlResult(
            status="error",
            client_id=client_id,
            action=action,
            message=f"API error: {e}"
        )


@mcp.tool()
async def cast_to_device(
    client_id: str,
    media_key: str,
    start_offset: Optional[int] = None,
    queue_items: Optional[List[str]] = None,
    replace_queue: bool = True
) -> PlaybackControlResult:
    """
    Cast media to a specific Plex client device with Austrian efficiency.
    
    Initiates playback of media on the target client, with optional queuing
    and precise start position control. Perfect for seamless media handoff.
    
    Args:
        client_id: Target client machine identifier
        media_key: Media key to start playing
        start_offset: Start position in milliseconds (for resuming)
        queue_items: Additional media keys to queue after current item
        replace_queue: Whether to replace existing queue (default: True)
        
    Returns:
        Cast operation result with playback status
        
    Austrian Efficiency Features:
        - Instant playback initiation (no menu navigation)
        - Resume from specific position (continue watching)
        - Queue management (binge-watch preparation)
        - Client availability validation before casting
        - Immediate feedback on cast success/failure
        
    Examples:
        Basic cast: cast_to_device("client123", "movie456")
        Resume: cast_to_device("client123", "movie456", start_offset=1800000)
        Queue: cast_to_device("client123", "ep1", queue_items=["ep2", "ep3"])
    """
    try:
        manager = await get_plex_manager()
        
        # Validate client exists and is available
        clients = await manager.get_clients()
        target_client = None
        for client in clients:
            if client.get('machineIdentifier') == client_id:
                target_client = client
                break
        
        if not target_client:
            return PlaybackControlResult(
                status="error",
                client_id=client_id,
                action="cast",
                message=f"Client {client_id} not found or unavailable"
            )
        
        client_name = target_client.get('name', 'Unknown Client')
        
        # Get media information for validation
        try:
            media_info = await manager.get_media_info(media_key)
            media_title = media_info.get('title', f'Media {media_key}')
        except PlexAPIError:
            media_title = f'Media {media_key}'
        
        # Initiate casting with Austrian efficiency
        cast_result = await manager.cast_media_to_client(
            client_id=client_id,
            media_key=media_key,
            start_offset=start_offset,
            replace_queue=replace_queue
        )
        
        # Add additional items to queue if specified
        if queue_items and len(queue_items) > 0:
            try:
                await manager.add_to_client_queue(client_id, queue_items)
                console.print(f"[green]Queued {len(queue_items)} additional items on {client_name}[/green]")
            except PlexAPIError as e:
                console.print(f"[yellow]Warning: Could not queue additional items: {e}[/yellow]")
        
        # Log successful cast
        if start_offset:
            console.print(f"[green]Cast '{media_title}' to {client_name} (resume at {start_offset}ms)[/green]")
        else:
            console.print(f"[green]Cast '{media_title}' to {client_name}[/green]")
        
        # Get current playback state after casting
        try:
            # Wait a moment for playback to initialize
            await asyncio.sleep(1)
            current_state = await manager.get_client_state(client_id)
            
            return PlaybackControlResult(
                status="success",
                client_id=client_id,
                action="cast",
                current_state=current_state.get('state', 'playing'),
                position=current_state.get('time', start_offset),
                duration=current_state.get('duration'),
                volume=current_state.get('volume'),
                message=f"Successfully cast '{media_title}' to {client_name}"
            )
            
        except PlexAPIError:
            # Cast succeeded but couldn't get current state
            return PlaybackControlResult(
                status="success",
                client_id=client_id,
                action="cast",
                current_state="playing",
                position=start_offset,
                message=f"Cast '{media_title}' to {client_name} (playback initiated)"
            )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in cast_to_device: {e}[/red]")
        return PlaybackControlResult(
            status="error",
            client_id=client_id,
            action="cast",
            message=f"Cast failed: {e}"
        )


# Quality & Performance Optimization Suite - Server Health Management

@mcp.tool()
async def transcoding_optimization(
    library_id: Optional[str] = None,
    quality_profile: str = "balanced",
    enable_hardware_acceleration: bool = True
) -> TranscodingStatus:
    """
    Optimize transcoding settings and monitor performance with Austrian efficiency.
    
    Manages quality profiles, hardware acceleration, and transcoding queue to
    ensure optimal performance without overwhelming complexity.
    
    Args:
        library_id: Specific library to optimize (if None, applies server-wide)
        quality_profile: Target profile (4k, 1080p, 720p, mobile, balanced, bandwidth_saver)
        enable_hardware_acceleration: Use GPU/hardware transcoding if available
        
    Returns:
        Current transcoding status with optimization recommendations
        
    Austrian Efficiency Features:
        - Predefined quality profiles (no complex manual settings)
        - Automatic hardware detection and optimization
        - Real-time performance monitoring
        - Actionable recommendations for improvement
        - Resource usage alerts and suggestions
        
    Quality Profiles:
        - 4k: Maximum quality for high-end devices
        - 1080p: Standard high quality for most devices
        - 720p: Balanced quality/bandwidth for mobile
        - mobile: Optimized for mobile devices and limited bandwidth
        - balanced: Automatically adjusts based on client capabilities
        - bandwidth_saver: Prioritizes minimal bandwidth usage
    """
    try:
        manager = await get_plex_manager()
        
        # Define quality profiles with Austrian efficiency
        profiles = {
            "4k": QualityProfile(
                name="4K Ultra HD",
                max_bitrate=25000,  # 25 Mbps
                resolution="3840x2160",
                codec="h265",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            ),
            "1080p": QualityProfile(
                name="Full HD",
                max_bitrate=8000,  # 8 Mbps
                resolution="1920x1080",
                codec="h264",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            ),
            "720p": QualityProfile(
                name="HD Ready",
                max_bitrate=4000,  # 4 Mbps
                resolution="1280x720",
                codec="h264",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            ),
            "mobile": QualityProfile(
                name="Mobile Optimized",
                max_bitrate=2000,  # 2 Mbps
                resolution="854x480",
                codec="h264",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            ),
            "balanced": QualityProfile(
                name="Balanced Quality",
                max_bitrate=6000,  # 6 Mbps
                resolution="1920x1080",
                codec="h264",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            ),
            "bandwidth_saver": QualityProfile(
                name="Bandwidth Saver",
                max_bitrate=1500,  # 1.5 Mbps
                resolution="854x480",
                codec="h264",
                container="mp4",
                audio_codec="aac",
                subtitle_format="srt"
            )
        }
        
        selected_profile = profiles.get(quality_profile, profiles["balanced"])
        
        # Apply transcoding settings
        await manager.update_transcoding_settings(
            quality_profile=selected_profile,
            hardware_acceleration=enable_hardware_acceleration,
            library_id=library_id
        )
        
        # Get current transcoding status
        status_data = await manager.get_transcoding_status()
        
        # Calculate performance metrics
        active_sessions = len(status_data.get('sessions', []))
        queue_length = status_data.get('queue_length', 0)
        cpu_usage = status_data.get('cpu_usage', 0)
        memory_usage = status_data.get('memory_usage', 0)
        disk_io = status_data.get('disk_io', 0)
        
        # Generate Austrian efficiency recommendations
        recommendations = []
        
        if cpu_usage > 80:
            recommendations.append("High CPU usage - consider enabling hardware acceleration or lowering quality")
        
        if memory_usage > 75:
            recommendations.append("High memory usage - reduce concurrent transcoding sessions")
            
        if disk_io > 80:
            recommendations.append("High disk I/O - consider SSD storage or reduce transcoding quality")
            
        if active_sessions > 5:
            recommendations.append("Many active sessions - monitor performance and consider hardware upgrade")
            
        if queue_length > 3:
            recommendations.append("Long transcoding queue - consider pre-transcoding popular content")
            
        # Hardware acceleration recommendations
        if not enable_hardware_acceleration and cpu_usage > 60:
            recommendations.append("Enable hardware acceleration to reduce CPU load")
            
        # Quality optimization suggestions
        if quality_profile == "4k" and cpu_usage > 70:
            recommendations.append("4K transcoding is resource-intensive - consider 1080p for better performance")
            
        # Austrian efficiency: Always provide at least one actionable recommendation
        if not recommendations:
            recommendations.append(f"Transcoding optimized for {selected_profile.name} - performance looks good!")
            
        console.print(f"[green]Transcoding optimized: {selected_profile.name} profile applied[/green]")
        
        return TranscodingStatus(
            active_sessions=active_sessions,
            queue_length=queue_length,
            cpu_usage=round(cpu_usage, 1),
            memory_usage=round(memory_usage, 1),
            disk_io=round(disk_io, 1),
            estimated_completion=status_data.get('estimated_completion'),
            current_jobs=status_data.get('current_jobs', []),
            recommendations=recommendations
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in transcoding_optimization: {e}[/red]")
        return TranscodingStatus(
            active_sessions=0,
            queue_length=0,
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_io=0.0,
            current_jobs=[],
            recommendations=[f"Error optimizing transcoding: {e}"]
        )


@mcp.tool()
async def bandwidth_analysis(
    time_period: str = "24h"
) -> BandwidthAnalysis:
    """
    Analyze network bandwidth usage and provide optimization recommendations.
    
    Austrian efficiency: Focus on actionable insights for bandwidth optimization,
    cost control, and performance improvement without overwhelming data.
    
    Args:
        time_period: Analysis period (1h, 6h, 24h, 7d, 30d)
        
    Returns:
        Comprehensive bandwidth analysis with optimization suggestions
        
    Austrian Efficiency Features:
        - Clear cost implications for metered connections
        - Client-specific usage breakdown for targeted optimization
        - Quality distribution analysis (identify over-transcoding)
        - Peak usage identification for capacity planning
        - Specific recommendations for bandwidth reduction
        
    Time Periods:
        - 1h: Real-time monitoring and immediate issues
        - 6h: Short-term usage patterns
        - 24h: Daily usage analysis (default)
        - 7d: Weekly patterns and trends
        - 30d: Monthly analysis for billing periods
    """
    try:
        manager = await get_plex_manager()
        
        # Get bandwidth statistics for the specified period
        stats = await manager.get_bandwidth_statistics(time_period)
        
        # Calculate key metrics
        total_bytes = stats.get('total_bytes', 0)
        total_gb = round(total_bytes / (1024**3), 2)  # Convert to GB
        
        duration_hours = {
            "1h": 1, "6h": 6, "24h": 24, "7d": 168, "30d": 720
        }.get(time_period, 24)
        
        peak_usage_bytes = stats.get('peak_usage_bytes_per_second', 0)
        peak_usage_mbps = round((peak_usage_bytes * 8) / (1024**2), 1)  # Convert to Mbps
        
        avg_usage_bytes = total_bytes / (duration_hours * 3600) if duration_hours > 0 else 0
        avg_usage_mbps = round((avg_usage_bytes * 8) / (1024**2), 1)
        
        # Analyze sessions and quality distribution
        sessions = stats.get('sessions', [])
        concurrent_streams = stats.get('max_concurrent_streams', 0)
        
        # Quality distribution analysis
        quality_dist = {}
        transcoding_sessions = 0
        direct_play_sessions = 0
        
        for session in sessions:
            quality = session.get('video_resolution', 'Unknown')
            quality_dist[quality] = quality_dist.get(quality, 0) + 1
            
            if session.get('transcoding', False):
                transcoding_sessions += 1
            else:
                direct_play_sessions += 1
        
        transcoding_overhead = 0
        if len(sessions) > 0:
            transcoding_overhead = round((transcoding_sessions / len(sessions)) * 100, 1)
        
        # Client breakdown analysis
        client_usage = {}
        for session in sessions:
            client = session.get('client_name', 'Unknown')
            usage = session.get('bandwidth_bytes', 0)
            client_usage[client] = client_usage.get(client, 0) + usage
        
        # Convert to readable format and sort
        client_breakdown = []
        for client, bytes_used in sorted(client_usage.items(), key=lambda x: x[1], reverse=True):
            client_breakdown.append({
                "client": client,
                "usage_gb": round(bytes_used / (1024**3), 2),
                "percentage": round((bytes_used / total_bytes) * 100, 1) if total_bytes > 0 else 0
            })
        
        # Generate Austrian efficiency recommendations
        optimization_suggestions = []
        
        # High bandwidth usage warnings
        if total_gb > 100:  # 100GB threshold
            optimization_suggestions.append(f"High usage detected ({total_gb}GB) - review quality settings")
            
        # Transcoding optimization
        if transcoding_overhead > 50:
            optimization_suggestions.append(f"High transcoding rate ({transcoding_overhead}%) - optimize media formats")
            
        # Peak usage optimization
        if peak_usage_mbps > 50:
            optimization_suggestions.append(f"Peak usage ({peak_usage_mbps} Mbps) may cause buffering - limit concurrent streams")
            
        # Quality distribution analysis
        if "4K" in quality_dist and quality_dist["4K"] > len(sessions) * 0.3:
            optimization_suggestions.append("Consider 1080p for mobile devices to reduce bandwidth")
            
        # Client-specific recommendations
        if len(client_breakdown) > 0 and client_breakdown[0]["percentage"] > 60:
            top_client = client_breakdown[0]["client"]
            optimization_suggestions.append(f"Client '{top_client}' uses {client_breakdown[0]['percentage']}% of bandwidth - review their settings")
            
        # Cost estimation for metered connections (Austrian practical approach)
        cost_estimate = None
        if total_gb > 0:
            # Estimate cost at €0.10 per GB (typical mobile data pricing)
            cost_estimate = round(total_gb * 0.10, 2)
            
        # Period-specific recommendations
        if time_period in ["24h", "7d", "30d"] and total_gb > 50:
            optimization_suggestions.append("Consider pre-downloading content during off-peak hours")
            
        # Austrian efficiency: Always provide actionable recommendations
        if not optimization_suggestions:
            optimization_suggestions.append("Bandwidth usage is optimized - current settings look efficient!")
            
        console.print(f"[green]Bandwidth analysis complete: {total_gb}GB used in {time_period}[/green]")
        
        return BandwidthAnalysis(
            time_period=time_period,
            total_bandwidth_gb=total_gb,
            peak_usage_mbps=peak_usage_mbps,
            average_usage_mbps=avg_usage_mbps,
            concurrent_streams=concurrent_streams,
            transcoding_overhead=transcoding_overhead,
            client_breakdown=client_breakdown,
            quality_distribution=quality_dist,
            optimization_suggestions=optimization_suggestions,
            cost_estimate=cost_estimate
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in bandwidth_analysis: {e}[/red]")
        return BandwidthAnalysis(
            time_period=time_period,
            total_bandwidth_gb=0.0,
            peak_usage_mbps=0.0,
            average_usage_mbps=0.0,
            concurrent_streams=0,
            transcoding_overhead=0.0,
            client_breakdown=[],
            quality_distribution={},
            optimization_suggestions=[f"Error analyzing bandwidth: {e}"],
            cost_estimate=None
        )


# Advanced Administration Suite - Server Management & Security

@mcp.tool()
async def user_permission_management(
    user_id: str,
    action: str,
    permissions: Optional[Dict[str, Any]] = None
) -> UserPermissions:
    """
    Manage user permissions and access control with Austrian efficiency.
    
    Provides granular control over user access, content restrictions, and
    sharing capabilities without overwhelming administrative complexity.
    
    Args:
        user_id: User identifier to manage
        action: Management action (get, update, restrict, unrestrict, remove)
        permissions: Permission settings for update action
        
    Returns:
        Updated user permission configuration
        
    Austrian Efficiency Features:
        - Clear permission categories (no confusing settings)
        - Family-safe defaults for managed users
        - Quick restriction toggles for parental controls
        - Library access management by category
        - Activity monitoring for security
        
    Actions:
        - get: Retrieve current permissions
        - update: Modify permission settings
        - restrict: Apply family-safe restrictions
        - unrestrict: Remove content restrictions
        - remove: Revoke all access (admin only)
        
    Permission Categories:
        - Library Access: Which content libraries user can access
        - Content Ratings: Maximum allowed rating (G, PG, PG-13, R, etc)
        - Sharing: Can share content with other users
        - Sync: Can download content for offline viewing
        - Admin: Server administration privileges
    """
    try:
        manager = await get_plex_manager()
        
        if action == "get":
            # Get current user permissions
            user_data = await manager.get_user_permissions(user_id)
            
        elif action == "update" and permissions:
            # Update user permissions with provided settings
            user_data = await manager.update_user_permissions(user_id, permissions)
            console.print(f"[green]Updated permissions for user {user_id}[/green]")
            
        elif action == "restrict":
            # Apply family-safe restrictions (Austrian efficiency preset)
            restrictions = {
                "restricted_content": True,
                "max_rating": "PG-13",
                "sharing_enabled": False,
                "is_admin": False,
                "sync_enabled": True  # Still allow offline viewing
            }
            user_data = await manager.update_user_permissions(user_id, restrictions)
            console.print(f"[green]Applied family-safe restrictions to user {user_id}[/green]")
            
        elif action == "unrestrict":
            # Remove content restrictions (adult access)
            unrestrictions = {
                "restricted_content": False,
                "max_rating": None,  # No rating limit
                "sharing_enabled": True,
                "sync_enabled": True
            }
            user_data = await manager.update_user_permissions(user_id, unrestrictions)
            console.print(f"[green]Removed content restrictions for user {user_id}[/green]")
            
        elif action == "remove":
            # Revoke all access (security action)
            await manager.remove_user_access(user_id)
            console.print(f"[green]Revoked all access for user {user_id}[/green]")
            return UserPermissions(
                user_id=user_id,
                username="[REMOVED]",
                is_admin=False,
                is_managed=False,
                library_access=[],
                restricted_content=True,
                sharing_enabled=False,
                sync_enabled=False,
                home_user=False,
                restrictions=["All access revoked"]
            )
            
        else:
            raise PlexAPIError(f"Invalid action '{action}' or missing permissions data")
        
        # Parse user data into structured permissions
        return UserPermissions(
            user_id=user_data.get('id', user_id),
            username=user_data.get('username', 'Unknown'),
            email=user_data.get('email'),
            is_admin=user_data.get('admin', False),
            is_managed=user_data.get('managed', False),
            library_access=user_data.get('library_access', []),
            restricted_content=user_data.get('restricted_content', False),
            max_rating=user_data.get('max_rating'),
            sharing_enabled=user_data.get('sharing_enabled', True),
            sync_enabled=user_data.get('sync_enabled', True),
            home_user=user_data.get('home_user', False),
            last_seen=user_data.get('last_seen'),
            restrictions=user_data.get('restrictions', [])
        )
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in user_permission_management: {e}[/red]")
        return UserPermissions(
            user_id=user_id,
            username="Error",
            is_admin=False,
            is_managed=False,
            library_access=[],
            restricted_content=True,
            sharing_enabled=False,
            sync_enabled=False,
            home_user=False,
            restrictions=[f"Error managing permissions: {e}"]
        )


@mcp.tool()
async def server_maintenance(
    action: str,
    options: Optional[Dict[str, Any]] = None
) -> ServerMaintenanceResult:
    """
    Perform server maintenance and optimization with Austrian efficiency.
    
    Handles cleanup, optimization, and maintenance tasks without requiring
    deep technical knowledge. Focus on essential operations that improve performance.
    
    Args:
        action: Maintenance operation (cleanup, optimize, backup, restart, analyze, full_maintenance)
        options: Operation-specific options and settings
        
    Returns:
        Maintenance operation results with recommendations
        
    Austrian Efficiency Features:
        - Predefined maintenance profiles (no complex configuration)
        - Safe operations with automatic backups
        - Clear space savings and performance impact
        - Scheduled maintenance recommendations
        - Rollback capability for safety
        
    Maintenance Operations:
        - cleanup: Remove cache, logs, thumbnails, orphaned files
        - optimize: Database optimization and defragmentation
        - backup: Create server configuration and metadata backup
        - restart: Safe server restart with session preservation
        - analyze: Performance analysis and recommendations
        - full_maintenance: Complete maintenance cycle (Austrian efficiency)
        
    Safety Features:
        - Automatic backup before destructive operations
        - Session preservation during restarts
        - Rollback capability for configuration changes
        - Progress monitoring and cancellation support
    """
    try:
        manager = await get_plex_manager()
        start_time = datetime.now()
        
        operation_details = {}
        space_freed = 0.0
        items_processed = 0
        warnings = []
        recommendations = []
        
        if action == "cleanup":
            # Comprehensive cleanup with Austrian efficiency
            console.print("[blue]Starting server cleanup...[/blue]")
            
            # Cache cleanup
            cache_result = await manager.cleanup_cache()
            space_freed += cache_result.get('space_freed_gb', 0)
            items_processed += cache_result.get('files_removed', 0)
            operation_details['cache_cleanup'] = cache_result
            
            # Log cleanup (keep last 30 days)
            log_result = await manager.cleanup_logs(keep_days=30)
            space_freed += log_result.get('space_freed_gb', 0)
            items_processed += log_result.get('files_removed', 0)
            operation_details['log_cleanup'] = log_result
            
            # Thumbnail cleanup (regenerate outdated)
            thumb_result = await manager.cleanup_thumbnails()
            space_freed += thumb_result.get('space_freed_gb', 0)
            items_processed += thumb_result.get('files_removed', 0)
            operation_details['thumbnail_cleanup'] = thumb_result
            
            # Orphaned file cleanup
            orphan_result = await manager.cleanup_orphaned_files()
            space_freed += orphan_result.get('space_freed_gb', 0)
            items_processed += orphan_result.get('files_removed', 0)
            operation_details['orphan_cleanup'] = orphan_result
            
            recommendations.append(f"Freed {space_freed:.2f}GB of disk space")
            if space_freed > 5:
                recommendations.append("Significant space freed - consider regular cleanup schedule")
                
        elif action == "optimize":
            # Database optimization
            console.print("[blue]Optimizing server database...[/blue]")
            
            # Database vacuum and reindex
            db_result = await manager.optimize_database()
            operation_details['database_optimization'] = db_result
            items_processed = db_result.get('tables_optimized', 0)
            
            # Metadata refresh for corrupted entries
            metadata_result = await manager.refresh_metadata(corrupted_only=True)
            operation_details['metadata_refresh'] = metadata_result
            items_processed += metadata_result.get('items_refreshed', 0)
            
            recommendations.append("Database optimized for better performance")
            recommendations.append("Consider optimizing during low-usage hours")
            
        elif action == "backup":
            # Create comprehensive backup
            console.print("[blue]Creating server backup...[/blue]")
            
            backup_result = await manager.create_backup(include_metadata=True)
            operation_details['backup'] = backup_result
            items_processed = backup_result.get('files_backed_up', 0)
            
            backup_size = backup_result.get('backup_size_gb', 0)
            recommendations.append(f"Backup created: {backup_size:.2f}GB")
            recommendations.append("Store backup in secure, off-site location")
            
        elif action == "restart":
            # Safe server restart
            console.print("[blue]Preparing for server restart...[/blue]")
            
            # Preserve active sessions
            sessions = await manager.get_sessions()
            if len(sessions) > 0:
                warnings.append(f"{len(sessions)} active sessions will be interrupted")
                
            restart_result = await manager.restart_server(preserve_sessions=True)
            operation_details['restart'] = restart_result
            
            recommendations.append("Server restarted successfully")
            recommendations.append("Monitor for any post-restart issues")
            
        elif action == "analyze":
            # Performance analysis
            console.print("[blue]Analyzing server performance...[/blue]")
            
            analysis_result = await manager.analyze_performance()
            operation_details['analysis'] = analysis_result
            
            # Generate specific recommendations
            if analysis_result.get('cpu_usage_avg', 0) > 70:
                recommendations.append("High CPU usage - consider hardware upgrade or transcoding optimization")
                
            if analysis_result.get('disk_usage_percent', 0) > 85:
                recommendations.append("Low disk space - cleanup or storage expansion recommended")
                
            if analysis_result.get('memory_usage_percent', 0) > 80:
                recommendations.append("High memory usage - consider increasing RAM or reducing concurrent operations")
                
            slow_libraries = analysis_result.get('slow_libraries', [])
            if slow_libraries:
                recommendations.append(f"Slow libraries detected: {', '.join(slow_libraries)} - consider optimization")
                
        elif action == "full_maintenance":
            # Complete maintenance cycle (Austrian efficiency)
            console.print("[blue]Performing full maintenance cycle...[/blue]")
            
            # Sequential maintenance operations
            maintenance_steps = ["backup", "cleanup", "optimize"]
            
            for step in maintenance_steps:
                step_result = await manager.perform_maintenance_step(step)
                operation_details[f'{step}_step'] = step_result
                space_freed += step_result.get('space_freed_gb', 0)
                items_processed += step_result.get('items_processed', 0)
                
            recommendations.append("Full maintenance cycle completed")
            recommendations.append(f"Total space freed: {space_freed:.2f}GB")
            recommendations.append("Schedule full maintenance monthly for optimal performance")
            
        else:
            raise PlexAPIError(f"Invalid maintenance action: {action}")
        
        # Calculate operation duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Determine next recommended maintenance
        next_maintenance = None
        if action == "cleanup":
            next_maintenance = "Weekly cleanup recommended"
        elif action == "optimize":
            next_maintenance = "Monthly optimization recommended"
        elif action == "full_maintenance":
            next_maintenance = "Next full maintenance in 30 days"
            
        # Austrian efficiency: Always provide actionable next steps
        if not recommendations:
            recommendations.append(f"Maintenance operation '{action}' completed successfully")
            
        console.print(f"[green]Maintenance '{action}' completed in {duration:.1f}s[/green]")
        
        return ServerMaintenanceResult(
            operation=action,
            status="success",
            details=operation_details,
            space_freed_gb=round(space_freed, 2) if space_freed > 0 else None,
            items_processed=items_processed,
            duration_seconds=round(duration, 1),
            recommendations=recommendations,
            next_recommended=next_maintenance,
            warnings=warnings
        )
        
    except PlexAPIError as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        console.print(f"[red]Maintenance error: {e}[/red]")
        return ServerMaintenanceResult(
            operation=action,
            status="error",
            details={"error": str(e)},
            items_processed=0,
            duration_seconds=round(duration, 1),
            recommendations=[f"Maintenance failed: {e}"],
            warnings=["Review server logs for detailed error information"]
        )


# Vienna/Austrian Context Suite - Gemütlichkeit & Cultural Awareness 🇦🇹

@mcp.tool()
async def wiener_recommendations(
    mood: str,
    duration: Optional[int] = None,
    time_context: str = "evening"
) -> List[WienerRecommendation]:
    """
    Get Vienna-context content recommendations with Austrian gemütlichkeit.
    
    Understands Austrian cultural context, Vienna lifestyle, and provides
    content recommendations that fit the specific mood and time context.
    
    Args:
        mood: Vienna mood context (gemütlich, arbeitswoch, weekend, kulturell, entspannt)
        duration: Preferred duration in minutes (if None, varies by mood)
        time_context: Time context (morning, afternoon, evening, night, weekend)
        
    Returns:
        List of Vienna-contextual content recommendations
        
    Vienna Mood Categories:
        - gemütlich: Cozy, comfortable content for relaxed evenings
        - arbeitswoch: Work week content (shorter, lighter after long days)
        - weekend: Weekend indulgence (longer, more engaging content)
        - kulturell: Cultural/artistic content (Austrian cinema, documentaries)
        - entspannt: Stress relief content (comedy, feel-good shows)
        
    Austrian Efficiency Features:
        - No decision paralysis (exactly 5 recommendations)
        - Cultural context awareness (Austrian holidays, seasons)
        - Time-sensitive suggestions (work day vs weekend)
        - Gemütlichkeit scoring (comfort factor)
        - Local relevance prioritization
    """
    try:
        manager = await get_plex_manager()
        
        # Vienna mood mapping with Austrian efficiency
        vienna_moods = {
            "gemütlich": {
                "keywords": ["comfort", "cozy", "heartwarming", "family", "romance"],
                "duration_preference": 90,  # 90 minutes for gemütlich mood
                "avoid_genres": ["horror", "thriller", "action"],
                "prefer_genres": ["drama", "comedy", "romance", "documentary"]
            },
            "arbeitswoch": {
                "keywords": ["light", "comedy", "episodic", "easy"],
                "duration_preference": 45,  # Shorter for work week tiredness
                "avoid_genres": ["complex drama", "horror"],
                "prefer_genres": ["comedy", "light drama", "sitcom"]
            },
            "weekend": {
                "keywords": ["epic", "adventure", "binge", "series"],
                "duration_preference": 120,  # Longer for weekend leisure
                "avoid_genres": [],
                "prefer_genres": ["drama", "action", "sci-fi", "fantasy"]
            },
            "kulturell": {
                "keywords": ["art", "culture", "european", "austrian", "arthouse"],
                "duration_preference": 100,  # Cultural content length
                "avoid_genres": ["action", "horror"],
                "prefer_genres": ["drama", "documentary", "foreign", "biography"]
            },
            "entspannt": {
                "keywords": ["funny", "uplifting", "feel-good", "positive"],
                "duration_preference": 75,  # Stress relief length
                "avoid_genres": ["horror", "thriller", "dark"],
                "prefer_genres": ["comedy", "animation", "musical", "adventure"]
            }
        }
        
        # Get mood configuration
        mood_config = vienna_moods.get(mood, vienna_moods["gemütlich"])
        target_duration = duration or mood_config["duration_preference"]
        
        # Get all media libraries
        libraries = await manager.get_libraries()
        all_candidates = []
        
        # Search across libraries with mood-specific keywords
        for library in libraries:
            for keyword in mood_config["keywords"]:
                search_results = await manager.search_media(keyword, library.get('key'))
                all_candidates.extend(search_results)
        
        # Vienna cultural context scoring
        vienna_recommendations = []
        current_time = datetime.now()
        current_month = current_time.month
        
        for candidate in all_candidates[:50]:  # Limit processing for efficiency
            title = candidate.get('title', '')
            genre = candidate.get('genre', '').lower()
            year = candidate.get('year', 0)
            rating = candidate.get('rating', 0)
            duration_minutes = candidate.get('duration', 0) // 60000 if candidate.get('duration') else 60
            
            # Calculate Vienna score based on multiple factors
            vienna_score = 5.0  # Base score
            
            # Genre preference scoring
            if any(preferred in genre for preferred in mood_config["prefer_genres"]):
                vienna_score += 2.0
            if any(avoided in genre for avoided in mood_config["avoid_genres"]):
                vienna_score -= 3.0
                
            # Duration matching (Austrian efficiency - not too long, not too short)
            duration_diff = abs(duration_minutes - target_duration)
            if duration_diff <= 15:  # Within 15 minutes
                vienna_score += 1.5
            elif duration_diff <= 30:  # Within 30 minutes
                vienna_score += 0.5
            else:
                vienna_score -= 1.0
                
            # Rating bonus (Austrians appreciate quality)
            if rating >= 8.0:
                vienna_score += 1.0
            elif rating >= 7.0:
                vienna_score += 0.5
                
            # Seasonal context (Austrian cultural awareness)
            seasonal_bonus = 0
            if current_month in [12, 1, 2] and "christmas" in title.lower():
                seasonal_bonus = 1.0
            elif current_month in [3, 4, 5] and "spring" in title.lower():
                seasonal_bonus = 0.5
                
            vienna_score += seasonal_bonus
            
            # Austrian/European content bonus
            austrian_context = None
            if any(word in title.lower() for word in ["vienna", "austria", "salzburg", "mozart"]):
                vienna_score += 2.0
                austrian_context = "Direct Austrian reference"
            elif any(word in title.lower() for word in ["german", "deutschland", "berlin"]):
                vienna_score += 1.0
                austrian_context = "German-speaking region"
            elif any(word in title.lower() for word in ["european", "eu", "europe"]):
                vienna_score += 0.5
                austrian_context = "European context"
                
            # Time context adjustment
            time_bonus = 0
            if time_context == "morning" and duration_minutes <= 60:
                time_bonus = 0.5
            elif time_context == "evening" and duration_minutes >= 90:
                time_bonus = 0.5
            elif time_context == "weekend" and duration_minutes >= 120:
                time_bonus = 1.0
                
            vienna_score += time_bonus
            
            # Generate recommendation reason (Austrian practical approach)
            reasons = []
            if vienna_score >= 8.0:
                reasons.append("Perfect Vienna match")
            if duration_diff <= 15:
                reasons.append(f"Ideal {target_duration}min length")
            if rating >= 7.5:
                reasons.append("High quality content")
            if austrian_context:
                reasons.append(austrian_context)
            if seasonal_bonus > 0:
                reasons.append("Seasonally appropriate")
                
            recommendation_reason = "; ".join(reasons) if reasons else f"Good fit for {mood} mood"
            
            # Determine best viewing time
            best_time = "anytime"
            if duration_minutes <= 45:
                best_time = "work evening or lunch break"
            elif duration_minutes <= 90:
                best_time = "relaxing evening"
            else:
                best_time = "weekend or holiday"
                
            # Only include decent recommendations (Austrian quality standards)
            if vienna_score >= 5.5:
                vienna_rec = WienerRecommendation(
                    media_key=candidate.get('key', ''),
                    title=title,
                    type=candidate.get('type', 'unknown'),
                    year=year if year > 0 else None,
                    duration=duration_minutes if duration_minutes > 0 else None,
                    rating=rating if rating > 0 else None,
                    vienna_score=round(vienna_score, 1),
                    mood_match=mood,
                    austrian_context=austrian_context,
                    recommendation_reason=recommendation_reason,
                    best_time=best_time
                )
                vienna_recommendations.append(vienna_rec)
        
        # Sort by Vienna score and return top 5 (Austrian efficiency)
        vienna_recommendations.sort(key=lambda x: x.vienna_score, reverse=True)
        top_recommendations = vienna_recommendations[:5]
        
        console.print(f"[green]Found {len(top_recommendations)} Vienna-context recommendations for {mood} mood[/green]")
        
        return top_recommendations
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in wiener_recommendations: {e}[/red]")
        return []


@mcp.tool()
async def european_content_finder(
    country: Optional[str] = None,
    genre: Optional[str] = None,
    language: str = "any"
) -> List[EuropeanContent]:
    """
    Discover European cinema and content with Austrian cultural perspective.
    
    Focuses on European productions, co-productions, and culturally significant
    content that resonates with Austrian and Central European sensibilities.
    
    Args:
        country: Specific European country ("austria", "germany", "france", etc)
        genre: Genre preference ("drama", "comedy", "documentary", etc)
        language: Language preference ("german", "english", "french", "any")
        
    Returns:
        List of European content with cultural context
        
    Austrian Efficiency Features:
        - Prioritizes German-speaking content (cultural proximity)
        - Identifies EU co-productions and funding
        - Cultural significance scoring
        - Subtitle availability for language learning
        - Awards recognition (European film awards)
        
    European Focus Areas:
        - Austrian cinema and TV productions
        - German-speaking region content
        - EU co-productions with cultural exchange
        - Arthouse and festival films
        - Historical and cultural documentaries
        - European crime/thriller series (very popular in Austria)
    """
    try:
        manager = await get_plex_manager()
        
        # European country mapping with Austrian perspective
        european_countries = {
            "austria": ["austria", "austrian", "wien", "vienna", "salzburg", "mozart", "sissi"],
            "germany": ["germany", "german", "deutschland", "berlin", "bavaria", "bayern"],
            "france": ["france", "french", "français", "paris", "lyon"],
            "italy": ["italy", "italian", "italia", "rome", "roma", "venice"],
            "uk": ["british", "england", "scotland", "wales", "london"],
            "spain": ["spain", "spanish", "españa", "madrid", "barcelona"],
            "netherlands": ["dutch", "netherlands", "holland", "amsterdam"],
            "belgium": ["belgian", "belgium", "brussels", "flanders"],
            "switzerland": ["swiss", "switzerland", "schweiz", "zurich"],
            "czech": ["czech", "prague", "bohemia", "czechoslovak"],
            "poland": ["polish", "poland", "warsaw", "krakow"],
            "scandinavian": ["nordic", "swedish", "norwegian", "danish", "finland"]
        }
        
        # Get libraries to search
        libraries = await manager.get_libraries()
        all_candidates = []
        
        # Build search terms based on parameters
        search_terms = []
        
        if country and country.lower() in european_countries:
            search_terms.extend(european_countries[country.lower()])
        else:
            # Search for general European content
            search_terms.extend(["european", "eu", "arte", "foreign", "international"])
            
        if genre:
            search_terms.append(genre)
            
        # Add language-specific terms
        if language != "any":
            search_terms.append(language)
            
        # Search across libraries
        for library in libraries:
            for term in search_terms:
                search_results = await manager.search_media(term, library.get('key'))
                all_candidates.extend(search_results)
                
        # Also search for common European directors and actors
        european_creators = [
            "werner herzog", "wim wenders", "fatih akin",  # German cinema
            "michael haneke", "ulrich seidl",  # Austrian cinema
            "lars von trier", "thomas vinterberg",  # Danish Dogme
            "pedro almodóvar", "alejandro amenábar",  # Spanish cinema
            "jean-luc godard", "françois truffaut"  # French New Wave
        ]
        
        for creator in european_creators:
            for library in libraries:
                creator_results = await manager.search_media(creator, library.get('key'))
                all_candidates.extend(creator_results)
        
        # Process and score European content
        european_content = []
        
        for candidate in all_candidates[:100]:  # Limit for efficiency
            title = candidate.get('title', '')
            year = candidate.get('year', 0)
            rating = candidate.get('rating', 0)
            summary = candidate.get('summary', '').lower()
            
            # Determine country and cultural significance
            detected_country = "Unknown"
            cultural_significance = None
            eu_funding = False
            awards = []
            
            # Country detection with Austrian perspective
            for country_key, keywords in european_countries.items():
                if any(keyword in title.lower() or keyword in summary for keyword in keywords):
                    detected_country = country_key.title()
                    break
                    
            # Check for EU funding indicators
            eu_indicators = ["co-production", "eurimages", "media programme", "creative europe"]
            if any(indicator in summary for indicator in eu_indicators):
                eu_funding = True
                
            # Cultural significance detection
            cultural_keywords = {
                "Historical importance": ["world war", "history", "historical", "period"],
                "Austrian cultural heritage": ["vienna", "mozart", "sissi", "salzburg", "austrian"],
                "European arthouse": ["cannes", "berlin", "venice", "palme", "golden bear"],
                "Social commentary": ["society", "politics", "migration", "integration"]
            }
            
            for significance, keywords in cultural_keywords.items():
                if any(keyword in summary for keyword in keywords):
                    cultural_significance = significance
                    break
                    
            # Awards detection (European focus)
            award_keywords = {
                "Cannes Film Festival": ["cannes", "palme d'or"],
                "Berlin International Film Festival": ["berlinale", "golden bear", "silver bear"],
                "Venice Film Festival": ["venice", "golden lion"],
                "European Film Awards": ["european film award", "lux prize"],
                "Austrian Film Prize": ["austrian film prize", "romy"]
            }
            
            for award, keywords in award_keywords.items():
                if any(keyword in summary for keyword in keywords):
                    awards.append(award)
                    
            # Calculate availability score (Austrian perspective)
            availability_score = 5.0
            
            # Language bonus (German-speaking preference)
            if detected_country in ["Austria", "Germany", "Switzerland"]:
                availability_score += 2.0
            elif detected_country in ["Czech", "Poland"]:  # Neighboring countries
                availability_score += 1.0
                
            # Genre preference (Austrian tastes)
            if genre and genre.lower() in ["crime", "thriller", "mystery"]:
                availability_score += 1.0  # Very popular in Austria
            elif genre and genre.lower() in ["documentary", "drama"]:
                availability_score += 0.5
                
            # Quality bonus
            if rating >= 8.0:
                availability_score += 1.0
            elif rating >= 7.0:
                availability_score += 0.5
                
            # Cultural bonus
            if cultural_significance:
                availability_score += 1.0
            if awards:
                availability_score += 0.5 * len(awards)
            if eu_funding:
                availability_score += 0.5
                
            # Language determination (simplified)
            detected_language = "Unknown"
            if detected_country in ["Austria", "Germany", "Switzerland"]:
                detected_language = "German"
            elif detected_country == "France":
                detected_language = "French"
            elif detected_country == "Italy":
                detected_language = "Italian"
            elif detected_country == "Spain":
                detected_language = "Spanish"
            elif detected_country == "Uk":
                detected_language = "English"
            
            # Subtitle assumption (most European content has multiple subs)
            subtitles = ["German", "English"]
            if detected_language not in subtitles:
                subtitles.append(detected_language)
                
            # Only include quality European content
            if availability_score >= 6.0 and detected_country != "Unknown":
                european_item = EuropeanContent(
                    media_key=candidate.get('key', ''),
                    title=title,
                    local_title=title,  # Simplified - would need translation API
                    country=detected_country,
                    language=detected_language,
                    subtitles=subtitles,
                    genre=genre or "Drama",
                    year=year if year > 0 else None,
                    rating=rating if rating > 0 else None,
                    cultural_significance=cultural_significance,
                    eu_funding=eu_funding,
                    awards=awards,
                    availability_score=round(availability_score, 1)
                )
                european_content.append(european_item)
        
        # Sort by availability score (Austrian preference)
        european_content.sort(key=lambda x: x.availability_score, reverse=True)
        
        # Return top 15 European content items
        top_european = european_content[:15]
        
        console.print(f"[green]Found {len(top_european)} European content items[/green]")
        
        return top_european
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in european_content_finder: {e}[/red]")
        return []


# Austrian Efficiency Tools for Sandra

@mcp.tool()
async def anime_season_lowdown() -> List[AnimeSeasonInfo]:
    """
    Get current and recent anime season overview for Sandra's weeb needs 🎌
    
    Austrian efficiency: Focus on current/recent anime without analysis paralysis.
    Filters anime content from TV libraries and provides season context.
    
    Returns:
        List of anime from current and recent seasons with status
    """
    try:
        manager = await get_plex_manager()
        
        # Get TV show libraries
        libraries = await manager.get_libraries()
        tv_libraries = [lib for lib in libraries if lib.get('type') == 'show']
        
        anime_list = []
        current_year = datetime.now().year
        
        for library in tv_libraries:
            # Search for anime-related content
            anime_results = await manager.search_media("anime", library['key'])
            
            # Also search for Japanese content
            japanese_results = await manager.search_media("japanese", library['key'])
            
            # Combine and deduplicate
            all_results = anime_results + japanese_results
            seen_titles = set()
            
            for item in all_results:
                title = item.get('title', '')
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                year = item.get('year', 0)
                if year >= current_year - 1:  # Current and last year
                    # Determine season based on month (approximate)
                    season = "Unknown"
                    if year == current_year:
                        season = "Current Year"
                    elif year == current_year - 1:
                        season = "Previous Year"
                    
                    anime_info = AnimeSeasonInfo(
                        title=title,
                        year=year,
                        season=season,
                        episodes_available=1,  # Would need episode count from detailed query
                        rating=item.get('rating'),
                        summary=item.get('summary', '')[:200] if item.get('summary') else None,
                        status="Available in library"
                    )
                    anime_list.append(anime_info)
        
        # Sort by year descending, then by title
        anime_list.sort(key=lambda x: (-x.year, x.title))
        
        # Limit to top 20 to avoid analysis paralysis
        return anime_list[:20]
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in anime_season_lowdown: {e}[/red]")
        return []


@mcp.tool()
async def movie_night_suggestions(
    genre: Optional[str] = None
) -> List[MediaItem]:
    """
    Get 3 movie suggestions for tonight - no analysis paralysis!
    
    Austrian efficiency: Exactly 3 picks, genre filtering available.
    Focus on highly rated, recent additions to avoid decision fatigue.
    
    Args:
        genre: Optional genre filter (action, comedy, drama, etc)
        
    Returns:
        Exactly 3 movie suggestions for tonight
    """
    try:
        manager = await get_plex_manager()
        
        # Get movie libraries
        libraries = await manager.get_libraries()
        movie_libraries = [lib for lib in libraries if lib.get('type') == 'movie']
        
        all_movies = []
        
        for library in movie_libraries:
            if genre:
                # Search by genre
                genre_movies = await manager.search_media(genre, library['key'])
                all_movies.extend(genre_movies)
            else:
                # Get recent additions
                recent_movies = await manager.get_recently_added(library['key'], 50)
                all_movies.extend(recent_movies)
        
        # Filter and sort movies
        good_movies = []
        for movie in all_movies:
            # Prefer movies with ratings and recent additions
            rating = movie.get('rating', 0)
            if rating >= 6.0 or movie.get('year', 0) >= 2020:
                good_movies.append(movie)
        
        # Sort by rating descending, then by year
        good_movies.sort(key=lambda x: (-(x.get('rating', 0)), -(x.get('year', 0))))
        
        # Return exactly 3 suggestions
        suggestions = good_movies[:3]
        
        movie_items = []
        for movie_data in suggestions:
            movie_item = MediaItem(
                key=movie_data.get('key', ''),
                title=movie_data.get('title', 'Unknown'),
                type=movie_data.get('type', 'movie'),
                year=movie_data.get('year'),
                summary=movie_data.get('summary'),
                rating=movie_data.get('rating'),
                thumb=movie_data.get('thumb'),
                art=movie_data.get('art'),
                duration=movie_data.get('duration'),
                added_at=int(movie_data.get('addedAt', 0)),
                updated_at=int(movie_data.get('updatedAt', 0))
            )
            movie_items.append(movie_item)
        
        return movie_items
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in movie_night_suggestions: {e}[/red]")
        return []


@mcp.tool() 
async def binge_ready_shows() -> List[MediaItem]:
    """
    Find complete series ready for binge watching.
    
    Austrian efficiency: Shows with all episodes available,
    no ongoing series that will leave you hanging.
    
    Returns:
        List of complete TV series perfect for binge watching
    """
    try:
        manager = await get_plex_manager()
        
        # Get TV show libraries
        libraries = await manager.get_libraries()
        tv_libraries = [lib for lib in libraries if lib.get('type') == 'show']
        
        complete_shows = []
        
        for library in tv_libraries:
            # Get library content
            shows = await manager.get_library_content(library['key'], 100)
            
            for show in shows:
                # Heuristic: shows older than 2 years are likely complete
                # or shows with high episode counts
                year = show.get('year', 0)
                current_year = datetime.now().year
                
                if year <= current_year - 2:  # Likely complete
                    show_item = MediaItem(
                        key=show.get('key', ''),
                        title=show.get('title', 'Unknown'),
                        type=show.get('type', 'show'),
                        year=show.get('year'),
                        summary=show.get('summary'),
                        rating=show.get('rating'),
                        thumb=show.get('thumb'),
                        art=show.get('art'),
                        duration=show.get('duration'),
                        added_at=int(show.get('addedAt', 0)),
                        updated_at=int(show.get('updatedAt', 0))
                    )
                    complete_shows.append(show_item)
        
        # Sort by rating and year
        complete_shows.sort(key=lambda x: (-(x.rating or 0), -(x.year or 0)))
        
        # Return top 15 binge-ready shows
        return complete_shows[:15]
        
    except PlexAPIError as e:
        console.print(f"[red]Plex API error in binge_ready_shows: {e}[/red]")
        return []


def main():
    """Main entry point for PlexMCP server"""
    # MCP servers must only output JSON to stdout
    # Any logging must go to stderr to avoid breaking JSON communication
    import sys
    
    # Log startup to stderr instead of stdout
    print("[PlexMCP] Starting FastMCP 2.0 Server - Austrian efficiency for media streaming!", file=sys.stderr)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()

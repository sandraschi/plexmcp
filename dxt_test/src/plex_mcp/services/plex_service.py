"""
Plex service implementation for PlexMCP.

This module contains the PlexService class which handles all interactions
with the Plex Media Server.
"""

from typing import Any, Dict, List, Optional, Union

import plexapi
from plexapi.server import PlexServer
from plexapi.exceptions import PlexApiException

from ..utils import get_logger, async_retry, run_in_executor, ValidationError

from ..models import (
    PlexServerStatus,
    MediaLibrary,
    MediaItem,
    PlexSession,
    PlexClient,
    PlexPlaylist,
    PlaylistCreateRequest,
    PlaylistAnalytics,
    RemotePlaybackRequest,
    CastRequest,
    PlaybackControlResult,
    UserPermissions,
    ServerMaintenanceResult,
    WienerRecommendation,
    EuropeanContent,
    AnimeSeasonInfo
)
from .base import BaseService, ServiceError

logger = logging.getLogger(__name__)

class PlexService(BaseService):
    """Service for interacting with Plex Media Server."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 30
    ):
        """Initialize the Plex service.
        
        Args:
            base_url: Base URL of the Plex server
            token: Plex authentication token
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.base_url = base_url
        self.token = token
        self.timeout = timeout
        self.plex: Optional[PlexServer] = None
    
    async def _initialize(self) -> None:
        """Initialize the Plex server connection."""
        if not self.base_url or not self.token:
            raise ServiceError(
                "Plex server URL and token must be provided",
                code="config_missing"
            )
        
        try:
            # Note: plexapi is synchronous, so we run it in a thread
            self.plex = PlexServer(self.base_url, self.token, timeout=self.timeout)
            logger.info(f"Connected to Plex server: {self.plex.friendlyName}")
        except Exception as e:
            error_msg = f"Failed to connect to Plex server: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="connection_failed") from e
    
    async def get_server_status(self) -> PlexServerStatus:
        """Get the current status of the Plex server."""
        await self.initialize()
        
        try:
            # Get server preferences
            prefs = self.plex.preferences()
            
            # Get MyPlex account info if available
            my_plex_account = None
            if self.plex.myPlexUsername:
                my_plex_account = self.plex.myPlexAccount()
            
            return PlexServerStatus(
                name=self.plex.friendlyName,
                version=self.plex.version,
                platform=self.plex.platform,
                updated_at=int(self.plex.updatedAt.timestamp()),
                size=self.plex.library.totalSize,
                my_plex_username=my_plex_account.username if my_plex_account else None,
                my_plex_mapping_state=self.plex.myPlexMappingState,
                connected=self.plex.myPlex is not None
            )
        except Exception as e:
            error_msg = f"Failed to get server status: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="server_status_failed") from e
    
    async def get_libraries(self) -> List[MediaLibrary]:
        """Get all libraries from the Plex server."""
        await self.initialize()
        
        try:
            libraries = []
            for section in self.plex.library.sections():
                libraries.append(MediaLibrary(
                    key=section.key,
                    title=section.title,
                    type=section.type,
                    agent=section.agent,
                    scanner=section.scanner,
                    language=section.language,
                    uuid=section.uuid,
                    created_at=int(section.addedAt.timestamp()) if section.addedAt else 0,
                    updated_at=int(section.updatedAt.timestamp()) if section.updatedAt else 0,
                    count=section.totalSize
                ))
            return libraries
        except Exception as e:
            error_msg = f"Failed to get libraries: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="get_libraries_failed") from e
    
    async def search_media(
        self,
        query: str,
        library_id: Optional[str] = None
    ) -> List[MediaItem]:
        """Search for media across all libraries or within a specific library."""
        await self.initialize()
        
        try:
            results = []
            
            if library_id:
                # Search in specific library
                section = self.plex.library.sectionByID(int(library_id))
                search_results = section.search(query)
            else:
                # Search across all libraries
                search_results = self.plex.search(query)
            
            for item in search_results:
                if hasattr(item, 'type') and item.type in ('movie', 'episode', 'show', 'artist', 'album', 'track'):
                    results.append(self._convert_to_media_item(item))
            
            return results
        except Exception as e:
            error_msg = f"Failed to search media: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="search_media_failed") from e
    
    async def get_clients(self) -> List[PlexClient]:
        """Get all available Plex clients."""
        await self.initialize()
        
        try:
            clients = []
            for client in self.plex.clients():
                clients.append(PlexClient(
                    name=client.title,
                    host=client.address,
                    machine_identifier=client.machineIdentifier,
                    product=client.product,
                    platform=client.platform,
                    platform_version=client.platformVersion,
                    device=client.device
                ))
            return clients
        except Exception as e:
            error_msg = f"Failed to get clients: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="get_clients_failed") from e
    
    async def get_sessions(self) -> List[PlexSession]:
        """Get all active playback sessions."""
        await self.initialize()
        
        try:
            sessions = []
            for session in self.plex.sessions():
                sessions.append(PlexSession(
                    session_key=session.sessionKey,
                    user=session.user.title if hasattr(session, 'user') else 'Unknown',
                    player=session.player.machineIdentifier,
                    state=session.player.state,
                    title=session.title,
                    progress=session.viewOffset // 1000 if hasattr(session, 'viewOffset') else 0,
                    duration=session.duration // 1000 if hasattr(session, 'duration') else 0
                ))
            return sessions
        except Exception as e:
            error_msg = f"Failed to get sessions: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="get_sessions_failed") from e
    
    async def control_playback(self, request: RemotePlaybackRequest) -> PlaybackControlResult:
        """Control playback on a remote client."""
        await self.initialize()
        
        try:
            # Find the client
            client = self.plex.client(request.client_id)
            if not client:
                raise ServiceError(f"Client {request.client_id} not found", code="client_not_found")
            
            # Execute the requested action
            if request.action == "play":
                if not request.media_key:
                    client.play()
                else:
                    media = self.plex.fetchItem(request.media_key)
                    client.playMedia(media)
            elif request.action == "pause":
                client.pause()
            elif request.action == "stop":
                client.stop()
            elif request.action == "seek" and request.seek_offset is not None:
                client.seekTo(request.seek_offset)
            elif request.action == "volume" and request.volume_level is not None:
                client.setVolume(request.volume_level)
            elif request.action == "stepForward":
                client.stepForward()
            elif request.action == "stepBack":
                client.stepBack()
            elif request.action == "skipNext":
                client.skipNext()
            elif request.action == "skipPrevious":
                client.skipPrevious()
            else:
                raise ServiceError(f"Unsupported action: {request.action}", code="unsupported_action")
            
            return PlaybackControlResult(
                status="success",
                client_id=request.client_id,
                action=request.action,
                current_state=client.state,
                position=client.viewOffset,
                duration=client.duration,
                volume=client.volume,
                message=f"Successfully executed {request.action} on {client.title}"
            )
            
        except Exception as e:
            error_msg = f"Failed to control playback: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="playback_control_failed") from e
    
    # Helper methods
    def _convert_to_media_item(self, item) -> MediaItem:
        """Convert a Plex API media item to our MediaItem model."""
        return MediaItem(
            key=item.ratingKey,
            title=item.title,
            type=item.type,
            year=item.year if hasattr(item, 'year') else None,
            summary=item.summary if hasattr(item, 'summary') else None,
            rating=item.rating if hasattr(item, 'rating') else None,
            thumb=item.thumb if hasattr(item, 'thumb') else None,
            art=item.art if hasattr(item, 'art') else None,
            duration=item.duration if hasattr(item, 'duration') else None,
            added_at=int(item.addedAt.timestamp()) if hasattr(item, 'addedAt') else 0,
            updated_at=int(item.updatedAt.timestamp()) if hasattr(item, 'updatedAt') else 0
        )
    
    async def _close(self) -> None:
        """Clean up resources."""
        # PlexAPI doesn't have an explicit close method
        self.plex = None

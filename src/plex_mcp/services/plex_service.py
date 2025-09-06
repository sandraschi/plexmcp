"""Plex service implementation for FastMCP 2.10."""
import logging
from typing import Any, Dict, List, Optional

from plexapi.exceptions import PlexApiException
from plexapi.server import PlexServer
import aiohttp

from ..models.media import MediaItem
from ..models.server import PlexServerStatus
from ..models.session import Session, SessionList
from ..models.user import User, UserList

logger = logging.getLogger(__name__)

class PlexService:
    """Service for interacting with Plex Media Server."""
    
    def __init__(self, base_url: str, token: str, timeout: int = 30):
        """Initialize Plex service.
        
        Args:
            base_url: Base URL of the Plex server (e.g., http://localhost:32400)
            token: Plex authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.server: Optional[PlexServer] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
    
    async def connect(self) -> None:
        """Establish connection to Plex server."""
        if self._initialized:
            return
            
        self._session = aiohttp.ClientSession()
        
        try:
            self.server = await self._run_in_executor(
                PlexServer,
                self.base_url,
                self.token,
                session=self._session,
                timeout=self.timeout
            )
            self._initialized = True
            logger.info(f"Connected to Plex server: {self.server.friendlyName}")
            
        except PlexApiException as e:
            logger.error(f"Failed to connect to Plex server: {str(e)}")
            raise
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous PlexAPI calls in executor."""
        import asyncio
        from functools import partial
        
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, partial(func, *args, **kwargs)
        )
    
    async def get_server_status(self) -> PlexServerStatus:
        """Get Plex server status and information."""
        if not self._initialized:
            await self.connect()
            
        try:
            status = await self._run_in_executor(
                self._get_server_status_sync
            )
            return PlexServerStatus(**status)
            
        except PlexApiException as e:
            logger.error(f"Failed to get server status: {str(e)}")
            raise
    
    def _get_server_status_sync(self) -> Dict[str, Any]:
        """Synchronous helper to get server status."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
            
        return {
            'name': self.server.friendlyName,
            'version': self.server.version,
            'platform': self.server.platform,
            'active_sessions': len(self.server.sessions()),
            'libraries': [s.title for s in self.server.library.sections()],
            'updated_at': self.server.updated_at.timestamp() if hasattr(self.server, 'updated_at') else 0
        }
    
    async def get_libraries(self) -> List[Dict[str, Any]]:
        """Get list of libraries from Plex server."""
        if not self._initialized:
            await self.connect()
            
        try:
            libraries = await self._run_in_executor(
                self._get_libraries_sync
            )
            return libraries
            
        except PlexApiException as e:
            logger.error(f"Failed to get libraries: {str(e)}")
            raise
    
    def _get_libraries_sync(self) -> List[Dict[str, Any]]:
        """Synchronous helper to get libraries."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
            
        return [{
            'id': section.key,
            'title': section.title,
            'type': section.type,
            'agent': section.agent,
            'updated_at': section.updatedAt.timestamp() if hasattr(section, 'updatedAt') else 0,
            'count': section.totalSize if hasattr(section, 'totalSize') else 0
        } for section in self.server.library.sections()]
    
    async def search_media(self, query: str, limit: int = 10, library_id: Optional[str] = None) -> List[MediaItem]:
        """Search for media across all libraries or within a specific library."""
        if not self._initialized:
            await self.connect()
            
        try:
            results = await self._run_in_executor(
                self._search_media_sync,
                query,
                limit,
                library_id
            )
            return [MediaItem(**item) for item in results]
            
        except PlexApiException as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    def _search_media_sync(self, query: str, limit: int, library_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Synchronous helper to search for media."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
            
        if library_id:
            section = self.server.library.sectionByID(int(library_id))
            results = section.search(query, maxresults=limit)
        else:
            results = self.server.search(query, limit=limit)
            
        return [{
            'id': item.ratingKey,
            'title': item.title,
            'type': item.type,
            'year': getattr(item, 'year', None),
            'thumb': getattr(item, 'thumb', ''),
            'summary': getattr(item, 'summary', '')
        } for item in results]
    
    async def close(self) -> None:
        """Close the Plex service and release resources."""
        if self._session:
            await self._session.close()
            self._session = None
        self.server = None
        self._initialized = False
        logger.info("Plex service closed")
    
    # Context manager support
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

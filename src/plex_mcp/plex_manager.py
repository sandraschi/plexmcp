"""
Plex Manager - Core Plex Media Server API Client

Handles authentication, XML parsing, and provides high-level
methods for all Plex server operations.
"""

import asyncio
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET

import requests
from requests.auth import HTTPBasicAuth
from rich.console import Console

# Robust import handling for both package and direct execution
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when run as package)
    from .config import PlexConfig
except ImportError:
    try:
        # Try absolute imports (when run directly)
        from plex_mcp.config import PlexConfig
    except ImportError:
        # Final fallback - direct imports from same directory
        from config import PlexConfig


console = Console()


class PlexAPIError(Exception):
    """Custom exception for Plex API errors"""
    pass


class PlexManager:
    """
    Plex Media Server API client.
    
    Handles authentication with X-Plex-Token, XML response parsing,
    and provides high-level methods for common Plex operations.
    """
    
    def __init__(self, config: PlexConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-Plex-Token': config.plex_token,
            'Accept': 'application/xml',
            'X-Plex-Client-Identifier': 'PlexMCP-FastMCP-2.0'
        })
        
        # Add basic auth if configured
        if config.username and config.password:
            self.session.auth = HTTPBasicAuth(config.username, config.password)
    
    def _xml_to_dict(self, xml_element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary recursively.
        
        Args:
            xml_element: ElementTree element
            
        Returns:
            Dictionary representation of XML data
        """
        result = {}
        
        # Add attributes
        if xml_element.attrib:
            result.update(xml_element.attrib)
        
        # Add text content if present
        if xml_element.text and xml_element.text.strip():
            result['text'] = xml_element.text.strip()
        
        # Add child elements
        for child in xml_element:
            child_dict = self._xml_to_dict(child)
            
            if child.tag in result:
                # Handle multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        
        return result
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Plex server with error handling.
        
        Args:
            endpoint: API endpoint relative to server URL
            params: Optional query parameters
            
        Returns:
            Parsed XML response as dictionary
            
        Raises:
            PlexAPIError: On API or network errors
        """
        url = f"{self.config.server_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            # Run request in thread pool since requests is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, params=params, timeout=self.config.timeout)
            )
            
            # Check for HTTP errors
            if response.status_code == 401:
                raise PlexAPIError("Authentication failed - check Plex token")
            elif response.status_code == 404:
                raise PlexAPIError("Plex server endpoint not found")
            elif response.status_code >= 400:
                raise PlexAPIError(f"HTTP error {response.status_code}: {response.text}")
            
            # Parse XML response
            try:
                root = ET.fromstring(response.content)
                return self._xml_to_dict(root)
            except ET.ParseError as e:
                raise PlexAPIError(f"Invalid XML response: {e}")
                
        except requests.exceptions.ConnectTimeout:
            raise PlexAPIError(f"Connection timeout after {self.config.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise PlexAPIError(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise PlexAPIError(f"Request error: {str(e)}")
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get server status and identity information"""
        return await self._make_request("/")
    
    async def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all media libraries"""
        response = await self._make_request("/library/sections")
        
        # Extract Directory elements (libraries)
        directories = response.get('Directory', [])
        if not isinstance(directories, list):
            directories = [directories]
        
        return directories
    
    async def search_media(self, query: str, library_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for media content"""
        if library_id:
            endpoint = f"/library/sections/{library_id}/search"
        else:
            endpoint = "/search"
        
        params = {'query': query}
        response = await self._make_request(endpoint, params)
        
        # Extract various media types from response
        results = []
        for media_type in ['Video', 'Directory', 'Track']:
            items = response.get(media_type, [])
            if not isinstance(items, list):
                items = [items]
            results.extend(items)
        
        return results
    
    async def get_recently_added(self, library_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently added media"""
        if library_id:
            endpoint = f"/library/sections/{library_id}/recentlyAdded"
        else:
            endpoint = "/library/recentlyAdded"
        
        params = {'X-Plex-Container-Size': str(limit)}
        response = await self._make_request(endpoint, params)
        
        # Extract Video elements
        videos = response.get('Video', [])
        if not isinstance(videos, list):
            videos = [videos] if videos else []
        
        return videos
    
    async def get_media_info(self, media_key: str) -> Dict[str, Any]:
        """Get detailed information about specific media"""
        return await self._make_request(f"/library/metadata/{media_key}")
    
    async def get_library_content(self, library_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get content from specific library"""
        endpoint = f"/library/sections/{library_id}/all"
        params = {'X-Plex-Container-Size': str(limit)}
        
        response = await self._make_request(endpoint, params)
        
        # Extract content based on library type
        content = []
        for content_type in ['Video', 'Directory', 'Artist', 'Album', 'Track']:
            items = response.get(content_type, [])
            if not isinstance(items, list):
                items = [items] if items else []
            content.extend(items)
        
        return content
    
    async def get_clients(self) -> List[Dict[str, Any]]:
        """Get available Plex clients"""
        response = await self._make_request("/clients")
        
        servers = response.get('Server', [])
        if not isinstance(servers, list):
            servers = [servers] if servers else []
        
        return servers
    
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """Get active playback sessions"""
        response = await self._make_request("/status/sessions")
        
        videos = response.get('Video', [])
        if not isinstance(videos, list):
            videos = [videos] if videos else []
        
        return videos
    
    async def scan_library(self, library_id: str) -> bool:
        """Trigger library scan"""
        try:
            endpoint = f"/library/sections/{library_id}/refresh"
            await self._make_request(endpoint)
            return True
        except PlexAPIError:
            return False
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get server users (admin function)"""
        response = await self._make_request("/accounts")
        
        users = response.get('Account', [])
        if not isinstance(users, list):
            users = [users] if users else []
        
        return users

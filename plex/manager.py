"""
Plex Manager - Core Plex server management
Austrian dev efficiency for media server operations
"""

import logging
import requests
from typing import Dict, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class PlexManagerError(Exception):
    """Base exception for Plex manager operations"""

    pass


class PlexManager:
    """Core Plex server management"""

    def __init__(self, server_url: str, token: str):
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"X-Plex-Token": token, "Accept": "application/json"})

    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request to Plex API"""
        try:
            url = urljoin(self.server_url, endpoint)
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise PlexManagerError(f"GET request failed: {e}")

    def post(self, endpoint: str, data: Dict = None) -> Dict:
        """Make POST request to Plex API"""
        try:
            url = urljoin(self.server_url, endpoint)
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            raise PlexManagerError(f"POST request failed: {e}")

    def get_server_info(self) -> Dict[str, Any]:
        """Get Plex server information"""
        return self.get("/")

    def test_connection(self) -> bool:
        """Test connection to Plex server"""
        try:
            self.get_server_info()
            return True
        except Exception:
            return False

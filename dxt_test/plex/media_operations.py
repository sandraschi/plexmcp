"""
Media Operations - Plex media search and management
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MediaOperations:
    """Plex media operations"""
    
    def __init__(self, plex_manager):
        self.plex = plex_manager
    
    def search_media(self, query: str) -> List[Dict[str, Any]]:
        """Search media across libraries"""
        try:
            data = self.plex.get("/search", {"query": query})
            results = []
            for hub in data.get("MediaContainer", {}).get("Hub", []):
                results.extend(hub.get("Metadata", []))
            return results
        except Exception as e:
            logger.error(f"Failed to search media: {e}")
            return []

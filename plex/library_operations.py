"""
Library Operations - Plex library management
Austrian dev efficiency for media library operations
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LibraryOperations:
    """Plex library management operations"""

    def __init__(self, plex_manager):
        self.plex = plex_manager

    def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all Plex libraries"""
        try:
            data = self.plex.get("/library/sections")
            sections = data.get("MediaContainer", {}).get("Directory", [])
            return sections
        except Exception as e:
            logger.error(f"Failed to get libraries: {e}")
            return []

    def scan_library(self, library_id: str) -> bool:
        """Scan specific library for new content"""
        try:
            self.plex.get(f"/library/sections/{library_id}/refresh")
            return True
        except Exception as e:
            logger.error(f"Failed to scan library {library_id}: {e}")
            return False

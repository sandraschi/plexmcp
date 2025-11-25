"""
User Manager - Plex user and sharing management
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class UserManager:
    """Plex user management"""

    def __init__(self, plex_manager):
        self.plex = plex_manager

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all Plex users"""
        try:
            # This would require admin access
            data = self.plex.get("/accounts")
            return data.get("MediaContainer", {}).get("Account", [])
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []

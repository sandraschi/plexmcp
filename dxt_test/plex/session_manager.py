"""
Session Manager - Plex session and playback management
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SessionManager:
    """Plex session management"""
    
    def __init__(self, plex_manager):
        self.plex = plex_manager
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get current active sessions"""
        try:
            data = self.plex.get("/status/sessions")
            return data.get("MediaContainer", {}).get("Metadata", [])
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []

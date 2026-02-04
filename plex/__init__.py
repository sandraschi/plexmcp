"""
Plex Media Server Management Module
Austrian dev efficiency for comprehensive Plex operations
"""

from .library_operations import LibraryOperations
from .manager import PlexManager, PlexManagerError
from .media_operations import MediaOperations
from .session_manager import SessionManager
from .user_manager import UserManager

__all__ = [
    "PlexManager",
    "PlexManagerError",
    "LibraryOperations",
    "SessionManager",
    "MediaOperations",
    "UserManager",
]

__version__ = "1.0.0"

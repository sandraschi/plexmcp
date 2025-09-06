"""
PlexMCP API Package

This package contains all API endpoints for the PlexMCP application,
organized into logical modules for better maintainability.

Note: The FastMCP instance is created in the parent server module.
API modules import it from there to register their tools.
"""

# Re-export API modules for convenience
from . import core
from . import playback
from . import playlists
from . import admin
from . import vienna

__all__ = ['core', 'playback', 'playlists', 'admin', 'vienna']
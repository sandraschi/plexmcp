"""
PlexMCP API Package

This package contains all API endpoints for the PlexMCP application,
organized into logical modules for better maintainability.
"""

from fastmcp import FastMCP

# Import all API modules to register their routes
from . import core, playback, playlists, admin, vienna

# Create the main FastMCP instance
app = FastMCP("PlexMCP")

# Register all sub-apps
app.mount("/core", core.app)
app.mount("/playback", playback.app)
app.mount("/playlists", playlists.app)
app.mount("/admin", admin.app)
app.mount("/vienna", vienna.app)

# Re-export the main app instance
__all__ = ['app']
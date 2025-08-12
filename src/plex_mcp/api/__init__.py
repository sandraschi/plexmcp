"""
PlexMCP API Package

This package contains all API endpoints for the PlexMCP application,
organized into logical modules for better maintainability.
"""

from fastmcp import FastMCP

# Create the shared FastMCP instance
mcp = FastMCP("PlexMCP")

# Import all API modules to register their tools with the shared mcp instance
# The import order matters if there are dependencies between modules
from . import core
from . import playback
from . import playlists
from . import admin
from . import vienna

# Re-export the main FastMCP instance
__all__ = ['mcp']
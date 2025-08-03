"""
PlexMCP - FastMCP 2.0 Server for Plex Media Server Management

Austrian efficiency package for Sandra's media streaming workflow.
Provides 13 tools: 10 core Plex operations + 3 Austrian efficiency tools.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.0 server for Plex Media Server management"

# Core exports - handle both package and direct execution
try:
    from .server import mcp
    from .config import PlexConfig  
    from .plex_manager import PlexManager, PlexAPIError
except ImportError:
    # For direct execution, these imports may not be available
    pass

__all__ = [
    "mcp",
    "PlexConfig",
    "PlexManager", 
    "PlexAPIError"
]

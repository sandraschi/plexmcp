"""
PlexMCP - FastMCP 2.14.3 Server for Plex Media Server Management

FastMCP 2.14.3 compliant with conversational tool returns and sampling capabilities.
Austrian efficiency for Sandra's media streaming needs.
"""

# Import the shared FastMCP instance
from .app import mcp

# Set up logger
from .utils import get_logger

logger = get_logger(__name__)

# Import portmanteau tools to register them with the MCP server
# The @mcp.tool() decorators execute when modules are imported
from .tools import portmanteau  # noqa: F401, E402

# Import and register agentic workflow tools (FastMCP 2.14.3 sampling features)
from .tools.agentic import register_agentic_tools  # noqa: E402

register_agentic_tools()

# NOTE: Old individual tools (server, media, sessions, users, playlists, organization, quality, library)
# are deprecated and will be removed in a future version.
# Use portmanteau tools instead:
# - plex_library (replaces library.py)
# - plex_media (replaces media.py)
# - plex_user (replaces users.py)
# - plex_playlist (replaces playlists.py)
# - plex_streaming (replaces sessions.py)
# - plex_performance (replaces quality.py, server.py)
# - plex_metadata (replaces organization.py)
# - plex_organization (replaces organization.py)
# - plex_server (replaces server.py)
# - plex_integration (replaces api/vienna.py)
# - plex_search (new advanced search)
# - plex_reporting (new reporting/analytics)
# - plex_collections (new collections management)
# - plex_quality (replaces quality profile tools)
# - plex_help (new help/discovery)


def main():
    """
    Main entry point for PlexMCP server with unified transport (FastMCP 2.14.4+).

    Supports STDIO (default), HTTP, and SSE transport modes.
    """
    from .transport import run_server

    logger.info("Starting FastMCP 2.14.4+ Server - Austrian efficiency for media streaming!")
    run_server(mcp, server_name="plex-mcp")


if __name__ == "__main__":
    main()

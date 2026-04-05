"""
PlexMCP - FastMCP 3.1 Server for Plex Media Server Management

FastMCP 3.1 with sampling, agentic workflows, skills and prompts.
"""

# CRITICAL: Load .env file before any other imports
import os
from dotenv import load_dotenv
load_dotenv()

# Import the shared FastMCP instance
from .app import mcp

# Set up logger
from .utils import get_logger

logger = get_logger(__name__)

# Import portmanteau tools to register them with the MCP server
# The @mcp.tool() decorators execute when modules are imported
from .tools import portmanteau  # noqa: F401, E402

# SEP-1577 agentic tools (sample_step + sample); requires FastMCP 3.1 sampling
try:
    from .tools.agentic import register_agentic_plex_tools  # noqa: E402

    register_agentic_plex_tools(mcp)
except ImportError as e:
    logger.warning("Agentic tools not registered: %s", e)

# ASGI app for uvicorn (webapp/start.ps1): plex_mcp.server:app
app = mcp.http_app()

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
    Main entry point for PlexMCP server (FastMCP 3.1).

    Supports STDIO (default), HTTP, and SSE transport modes.
    """
    from .transport import run_server

    logger.info("Starting PlexMCP (FastMCP 3.1)")
    run_server(mcp, server_name="plex-mcp")


if __name__ == "__main__":
    main()

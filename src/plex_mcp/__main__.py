"""
PlexMCP - FastMCP 3.2 Server Main Entry Point

Entry point for module execution: python -m plex_mcp
Production-ready FastMCP 3.2 server for Plex Media Server.
"""

from plex_mcp.app import mcp
from plex_mcp.utils import get_logger

logger = get_logger(__name__)

def main():
    """Main entry point for PlexMCP server (FastMCP 3.2)."""
    from .transport import run_server

    logger.info("Starting PlexMCP (FastMCP 3.2)")
    run_server(mcp, server_name="plex-mcp")

# Export the mcp object for FastMCP discovery
__all__ = ["mcp", "main"]

if __name__ == "__main__":
    main()

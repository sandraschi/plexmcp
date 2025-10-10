#!/usr/bin/env python3
"""
PlexMCP Main Entry Point
Proper MCP stdio protocol implementation
"""

import asyncio
import logging
import sys
from typing import Any, Sequence
from fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# Import all tool modules
from .api import core, playlists, playback, admin
from .config import get_settings, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def main() -> None:
    """Main entry point for MCP stdio server."""
    settings = get_settings()
    
    # Create FastMCP app
    app = FastMCP("PlexMCP", 
                 description="Production Plex Media Server MCP integration")
    
    # Register all tools from modules
    # Tools are auto-registered via @app.tool() decorators
    
    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

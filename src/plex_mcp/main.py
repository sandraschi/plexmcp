#!/usr/bin/env python3
"""
PlexMCP Main Entry Point
Proper MCP stdio protocol implementation
"""

import asyncio
import logging

from fastmcp import FastMCP
from mcp.server.stdio import stdio_server

from .config import get_settings, setup_logging

# Import all tool modules
from .transport import run_server_async

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for MCP stdio server."""
    # Settings loaded via environment variables, no need to store
    get_settings()

    # Create FastMCP app
    app = FastMCP("PlexMCP")

    # Register all tools from modules
    # Tools are auto-registered via @app.tool() decorators

    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await run_server_async(app, server_name="PlexMCP")


if __name__ == "__main__":
    asyncio.run(main())

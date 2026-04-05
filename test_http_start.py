#!/usr/bin/env python3
"""
Test HTTP mode startup to isolate the hanging issue.
"""

import os
import sys
import asyncio
import logging

# Set environment to allow logging
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"
# Force HTTP mode to avoid stdio complexity
os.environ["MCP_TRANSPORT"] = "http"
os.environ["MCP_PORT"] = "10742"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting PlexMCP HTTP test...")

try:
    from plex_mcp.app import mcp
    from plex_mcp.transport import run_server_async
    print("✓ Imports successful")
    
    # Start server with timeout
    async def test_start():
        try:
            print("Starting server...")
            await run_server_async(mcp, server_name="plex-mcp-test")
        except Exception as e:
            print(f"Server start failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run with timeout
    try:
        asyncio.run(test_start())
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

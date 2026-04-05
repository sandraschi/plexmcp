#!/usr/bin/env python3
"""
Simple startup that bypasses complex logging and sampling.
"""

import os
import sys
import asyncio

# Force client-side sampling to avoid HTTP connection attempts
os.environ["PLEX_SAMPLING_USE_CLIENT_LLM"] = "1"
# Disable complex stdout redirection
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting PlexMCP simple...")

# Import and start in stdio mode directly
from plex_mcp.app import mcp

async def main():
    print("Starting stdio server...")
    try:
        await mcp.run_stdio_async()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

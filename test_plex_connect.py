#!/usr/bin/env python3
"""
Test Plex connection directly to isolate hanging.
"""

import os
import sys
import asyncio

# Set environment
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"
os.environ["PLEX_SAMPLING_USE_CLIENT_LLM"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_plex_service():
    print("Testing PlexService connection...")
    try:
        from plex_mcp.services.plex_service import PlexService
        print("✓ PlexService imported")
        
        service = PlexService()
        print("✓ PlexService instantiated")
        
        # Try connection with timeout
        print("Attempting connection...")
        try:
            await asyncio.wait_for(service.connect(), timeout=5.0)
            print("✓ Connected successfully")
        except asyncio.TimeoutError:
            print("✗ Connection timeout")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            
    except Exception as e:
        print(f"✗ PlexService test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_plex_service())

#!/usr/bin/env python3
"""
Minimal startup without sampling to isolate hanging.
"""

import os
import sys

# Disable sampling to avoid connection hangs
os.environ["PLEX_SAMPLING_USE_CLIENT_LLM"] = "1"
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting minimal PlexMCP...")

try:
    from plex_mcp.app import mcp
    print("✓ App imported")
    
    # Try to create the server instance without starting it
    print("Creating server instance...")
    import argparse
    args = argparse.Namespace()
    args.stdio = True
    args.http = False
    args.sse = False
    args.host = None
    args.port = None
    args.path = None
    args.debug = True
    
    from plex_mcp.transport import resolve_config
    config = resolve_config(args)
    print(f"✓ Config resolved: {config}")
    
    print("Ready to start. If this prints, the hang is in the actual server run.")
    
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Debug startup script for PlexMCP to identify hanging point.
"""

import os
import sys
import logging

# Set environment to allow logging
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting PlexMCP debug...")

try:
    print("Importing app...")
    from plex_mcp.app import mcp
    print("✓ App imported")
except Exception as e:
    print(f"✗ App import failed: {e}")
    sys.exit(1)

try:
    print("Importing transport...")
    from plex_mcp.transport import run_server
    print("✓ Transport imported")
except Exception as e:
    print(f"✗ Transport import failed: {e}")
    sys.exit(1)

try:
    print("Importing portmanteau tools...")
    from plex_mcp.tools import portmanteau
    print("✓ Portmanteau tools imported")
except Exception as e:
    print(f"✗ Portmanteau import failed: {e}")
    sys.exit(1)

try:
    print("Creating HTTP app...")
    app = mcp.http_app()
    print("✓ HTTP app created")
except Exception as e:
    print(f"✗ HTTP app creation failed: {e}")
    sys.exit(1)

print("All imports successful. Ready to start server.")

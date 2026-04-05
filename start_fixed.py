#!/usr/bin/env python3
"""
Fixed startup that loads .env file properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

# Set environment variables
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"
os.environ["PLEX_SAMPLING_USE_CLIENT_LLM"] = "1"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Starting PlexMCP with .env loaded...")

# Check if token is loaded
token = os.getenv("PLEX_TOKEN")
if token:
    print(f"✓ PLEX_TOKEN loaded: {token[:10]}...")
else:
    print("✗ PLEX_TOKEN not found")

# Import and start
from plex_mcp.app import mcp
from plex_mcp.transport import run_server

def main():
    print("Starting server...")
    run_server(mcp, server_name="plex-mcp")

if __name__ == "__main__":
    main()

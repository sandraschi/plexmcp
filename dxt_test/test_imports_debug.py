#!/usr/bin/env python3
"""Simple test to check PlexMCP server imports"""

import sys
import os
import traceback

print("=== PlexMCP Import Test ===")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("\n1. Testing basic imports...")
    import requests
    print("✅ requests imported")
    
    import fastmcp  
    print("✅ fastmcp imported")
    
    from pydantic import BaseModel
    print("✅ pydantic imported")
    
    print("\n2. Testing PlexMCP config...")
    from config import PlexConfig
    print("✅ config imported")
    
    print("\n3. Testing PlexMCP manager...")
    from plex_manager import PlexManager, PlexAPIError
    print("✅ plex_manager imported")
    
    print("\n4. Testing full server import...")
    import server
    print("✅ server imported")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

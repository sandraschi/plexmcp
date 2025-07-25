#!/usr/bin/env python3
"""
Test script to verify PlexMCP import fix
"""

print("Testing PlexMCP imports...")

try:
    import sys
    import os
    print(f"Python path: {sys.path[0]}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test the fixed imports
    from plex_manager import PlexManager, PlexAPIError
    print("✅ plex_manager imports successfully")
    
    from config import PlexConfig
    print("✅ config imports successfully")
    
    # Test server import
    print("Testing server.py imports...")
    import server
    print("✅ server.py imports successfully")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL - PlexMCP FIX WORKS!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

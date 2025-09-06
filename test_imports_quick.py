"""
Simple test to check PlexMCP imports
"""
import sys
import os

# Add the PlexMCP source to path
plex_path = r"D:\Dev\repos\plexmcp\src"
sys.path.insert(0, plex_path)

print("🔍 Testing PlexMCP imports...")

try:
    print("  1. Testing plex_mcp package import...")
    import plex_mcp
    print("  ✅ plex_mcp package imported successfully")
    
    print("  2. Testing utils imports...")
    from plex_mcp.utils import ValidationError, validate_plex_url, validate_media_item, validate_playlist
    print("  ✅ utils validation functions imported successfully")
    
    print("  3. Testing api imports...")
    from plex_mcp.api import core, playback, playlists, admin, vienna
    print("  ✅ api modules imported successfully")
    
    print("  4. Testing server import...")
    from plex_mcp.server import main
    print("  ✅ server main function imported successfully")
    
    print("\n🚀 ALL IMPORTS SUCCESSFUL! PlexMCP is ready to run!")
    
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"  ❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

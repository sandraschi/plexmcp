"""
Test script to verify PlexMCP imports are working
"""
import sys
import os

# Add the source directory to Python path
sys.path.insert(0, "D:/Dev/repos/plexmcp/src")

try:
    print("🔍 Testing PlexMCP imports...")
    
    # Test validation imports
    from plex_mcp.utils.validation import validate_plex_url, validate_media_item, validate_playlist
    from plex_mcp.utils import ValidationError
    print("✅ All validation imports successful!")
    
    # Test server import
    from plex_mcp.server import main
    print("✅ Server import successful!")
    
    # Test main module import
    from plex_mcp import __main__
    print("✅ Main module import successful!")
    
    print("🎉 ALL IMPORTS SUCCESSFUL - PlexMCP should start now!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Other error: {e}")
    sys.exit(1)

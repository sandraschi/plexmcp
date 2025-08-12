
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, 'D:/Dev/repos/plexmcp/src')

print("Python version:", sys.version)
print("Python path:", sys.path[0:3])

try:
    print("Testing FastMCP import...")
    import fastmcp
    print("✅ FastMCP imported successfully, version:", getattr(fastmcp, '__version__', 'unknown'))
except ImportError as e:
    print("❌ FastMCP import failed:", e)

try:
    print("Testing PlexAPI import...")
    import plexapi
    print("✅ PlexAPI imported successfully")
except ImportError as e:
    print("❌ PlexAPI import failed:", e)

try:
    print("Testing Pydantic import...")
    import pydantic
    print("✅ Pydantic imported successfully")
except ImportError as e:
    print("❌ Pydantic import failed:", e)

try:
    print("Testing plex_mcp module import...")
    import plex_mcp
    print("✅ plex_mcp module imported successfully")
    print("Module file:", plex_mcp.__file__ if hasattr(plex_mcp, '__file__') else 'unknown')
except ImportError as e:
    print("❌ plex_mcp import failed:", e)

print("\nDiagnostic complete.")

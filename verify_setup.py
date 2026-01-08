#!/usr/bin/env python3
"""Quick verification script to test Plex MCP server setup."""

import sys
import traceback

def test_imports():
    """Test that all critical imports work."""
    print("Testing imports...")
    
    try:
        sys.path.insert(0, "src")
        
        # Test 1: Import FastMCP instance
        print("  [1] Importing FastMCP instance...")
        from plex_mcp.app import mcp
        print(f"      [OK] FastMCP instance: {mcp}")

        # Test 2: Import portmanteau tools
        print("  [2] Importing portmanteau tools...")
        from plex_mcp.tools import portmanteau
        print("      [OK] Portmanteau tools imported")

        # Test 3: Check tool registration
        print("  [3] Checking tool registration...")
        # Tools are registered via decorators, so we check if mcp has tools
        if hasattr(mcp, "_tools"):
            tool_count = len(mcp._tools)
            print(f"      [OK] Tools registered: {tool_count}")
            if tool_count > 0:
                tool_names = list(mcp._tools.keys())[:5]
                print(f"      Sample tools: {tool_names}...")
        else:
            print("      [INFO] Could not determine tool count (may be normal for FastMCP 2.14+)")

        # Test 4: Import server main
        print("  [4] Importing server main...")
        from plex_mcp.server import main
        print(f"      [OK] Server main function: {main}")

        # Test 5: Import config
        print("  [5] Testing configuration...")
        from plex_mcp.config import get_settings
        try:
            settings = get_settings()
            print(f"      [OK] Config loaded (token: {'SET' if settings.plex_token else 'NOT SET'})")
        except Exception as e:
            print(f"      [WARN] Config error (expected if PLEX_TOKEN not set): {type(e).__name__}")

        print("\n[SUCCESS] All imports successful!")
        print("\nServer is ready to run:")
        print("  python -m plex_mcp.server")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

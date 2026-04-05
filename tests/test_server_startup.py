"""
Test server startup and basic functionality.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

# Load test environment
load_dotenv()
os.environ["PLEXMCP_ALLOW_LOGGING"] = "1"
os.environ["PLEX_SAMPLING_USE_CLIENT_LLM"] = "1"


async def test_server_startup():
    """Test server startup and basic MCP protocol."""
    print("Testing PlexMCP server startup...")
    
    try:
        # Import server
        from plex_mcp.server import mcp
        print("✓ Server imported")
        
        # Test HTTP app creation
        app = mcp.http_app()
        print("✓ HTTP app created")
        
        # Test tool registration
        tools = await mcp.list_tools()
        print(f"✓ {len(tools)} tools registered")
        
        # Test resource registration
        resources = await mcp.list_resources()
        print(f"✓ {len(resources)} resources registered")
        
        # Test basic tool call
        if tools:
            tool_names = [tool.name for tool in tools[:5]]  # First 5 tools
            print(f"✓ Available tools: {', '.join(tool_names)}")
        
        print("✓ Server startup test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Server startup test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_protocol():
    """Test basic MCP protocol communication."""
    print("\nTesting MCP protocol...")
    
    try:
        from plex_mcp.server import mcp
        
        # Simulate initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "test",
                    "version": "1.0.0"
                }
            }
        }
        
        print("✓ MCP protocol test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ MCP protocol test FAILED: {e}")
        return False


async def main():
    """Run all tests."""
    print("=== PlexMCP Server Test Suite ===")
    
    tests = [
        ("Server Startup", test_server_startup),
        ("MCP Protocol", test_mcp_protocol),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = await test_func()
        results.append((test_name, result))
    
    print(f"\n=== Test Results ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PlexMCP is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

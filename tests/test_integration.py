"""
Integration tests for PlexMCP with actual Plex server.
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


async def test_plex_connection():
    """Test actual Plex server connection."""
    print("Testing Plex server connection...")
    
    try:
        from plex_mcp.services.plex_service import PlexService
        
        service = PlexService()
        await service.connect()
        
        # Test basic server info
        if service.server:
            print(f"✓ Connected to: {service.server.friendlyName}")
            print(f"✓ Server version: {service.server.version}")
            print(f"✓ Machine ID: {service.server.machineIdentifier}")
            return True
        else:
            print("✗ No server connection established")
            return False
            
    except Exception as e:
        print(f"✗ Plex connection failed: {e}")
        return False


async def test_library_access():
    """Test library access and basic operations."""
    print("\nTesting library access...")
    
    try:
        from plex_mcp.services.plex_service import PlexService
        
        service = PlexService()
        await service.connect()
        
        # Get libraries
        libraries = service.server.library.sections()
        print(f"✓ Found {len(libraries)} libraries:")
        
        for lib in libraries[:3]:  # Show first 3
            print(f"  - {lib.title} ({lib.type}) - {len(lib.all())} items")
        
        return True
        
    except Exception as e:
        print(f"✗ Library access failed: {e}")
        return False


async def test_tool_operations():
    """Test actual tool operations."""
    print("\nTesting tool operations...")
    
    try:
        from plex_mcp.server import mcp
        
        # Test plex_library tool
        tools = await mcp.list_tools()
        plex_library_tool = next((t for t in tools if t.name == "plex_library"), None)
        
        if not plex_library_tool:
            print("✗ plex_library tool not found")
            return False
        
        print("✓ plex_library tool found")
        
        # Test tool call
        result = await mcp.call_tool("plex_library", {"operation": "list"})
        
        if hasattr(result, 'content') and result.content:
            print("✓ plex_library operation successful")
            return True
        else:
            print("✗ plex_library operation failed")
            return False
            
    except Exception as e:
        print(f"✗ Tool operation failed: {e}")
        return False


async def test_resource_access():
    """Test resource access."""
    print("\nTesting resource access...")
    
    try:
        from plex_mcp.server import mcp
        
        # List all available resources
        resources = await mcp.list_resources()
        print(f"✓ Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource.uri}")
        
        # Test health resource
        health_resource = next((r for r in resources if "health" in str(r.uri)), None)
        
        if health_resource:
            print("✓ Health resource found")
            
            # Access health resource
            result = await mcp.read_resource(health_resource.uri)
            print(f"✓ Resource accessed successfully: {type(result)}")
            
            # Try to get the content - FastMCP 3.2 returns a list
            try:
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].text
                elif hasattr(result, 'contents'):
                    content = result.contents.text
                elif hasattr(result, 'text'):
                    content = result.text
                else:
                    content = str(result)
                
                health_data = json.loads(content)
                print(f"✓ Health status: {health_data.get('status', 'unknown')}")
                print(f"✓ Version: {health_data.get('version', 'unknown')}")
                return True
            except Exception as parse_error:
                print(f"✗ Failed to parse resource content: {parse_error}")
                print(f"✗ Result type: {type(result)}")
                if isinstance(result, list):
                    print(f"✗ List length: {len(result)}")
                    if len(result) > 0:
                        print(f"✗ First item type: {type(result[0])}")
                return False
        else:
            print("✗ Health resource not found")
            return False
            
    except Exception as e:
        print(f"✗ Resource access failed: {e}")
        return False


async def test_error_handling():
    """Test error handling with invalid operations."""
    print("\nTesting error handling...")
    
    try:
        from plex_mcp.server import mcp
        
        # Test invalid tool call
        try:
            result = await mcp.call_tool("plex_library", {"operation": "invalid_operation"})
            print("✗ Should have failed with invalid operation")
            return False
        except Exception:
            print("✓ Invalid operation properly handled")
        
        # Test invalid resource
        try:
            result = await mcp.read_resource("resource://plex/nonexistent")
            print("✗ Should have failed with invalid resource")
            return False
        except Exception:
            print("✓ Invalid resource properly handled")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("=== PlexMCP Integration Test Suite ===")
    
    # Check prerequisites
    if not os.getenv("PLEX_TOKEN"):
        print("❌ PLEX_TOKEN environment variable required")
        return 1
    
    tests = [
        ("Plex Connection", test_plex_connection),
        ("Library Access", test_library_access),
        ("Tool Operations", test_tool_operations),
        ("Resource Access", test_resource_access),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = await test_func()
        results.append((test_name, result))
        
        # Don't continue if basic connection fails
        if test_name == "Plex Connection" and not result:
            break
    
    print(f"\n=== Integration Test Results ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! PlexMCP is fully functional.")
        return 0
    else:
        print("❌ Some integration tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

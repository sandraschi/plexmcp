#!/usr/bin/env python3
"""Test script to call plex_streaming list_clients operation."""

import asyncio
import sys


async def test_list_clients():
    """Test the list_clients operation."""
    try:
        # Add src to path
        sys.path.insert(0, "src")

        # Import the underlying function directly by accessing the module
        import plex_mcp.tools.portmanteau.streaming as streaming_module

        print("Testing plex_streaming list_clients operation...")
        print("=" * 60)

        # Get the function from the module (before MCP decoration)
        actual_func = getattr(streaming_module, "_plex_streaming_impl", None)
        if not actual_func:
            # Fallback: try to find it by looking at module attributes
            for attr_name in dir(streaming_module):
                attr = getattr(streaming_module, attr_name)
                if (
                    callable(attr)
                    and hasattr(attr, "__name__")
                    and "plex_streaming" in attr.__name__
                ):
                    actual_func = attr
                    break

        if not actual_func:
            raise RuntimeError("Could not find plex_streaming function")

        # Call the function
        result = await actual_func(operation="list_clients")

        print("Result:")
        print(f"Success: {result.get('success', False)}")
        print(f"Operation: {result.get('operation', 'unknown')}")
        print(f"Count: {result.get('count', 0)}")

        if result.get("success"):
            clients = result.get("data", [])
            print("\nClients found:")
            for i, client in enumerate(clients, 1):
                print(
                    f"  {i}. {client.get('name', 'Unknown')} ({client.get('product', 'Unknown')})"
                )
                print(f"     Platform: {client.get('platform', 'Unknown')}")
                print(f"     Address: {client.get('address', 'Unknown')}")
                print()
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            if "suggestions" in result:
                print("Suggestions:")
                for suggestion in result["suggestions"]:
                    print(f"  - {suggestion}")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_list_clients())

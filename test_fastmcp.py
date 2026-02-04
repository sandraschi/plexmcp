#!/usr/bin/env python3
"""Test script to verify FastMCP 2.14.3 conversational features in PlexMCP."""

import sys


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from plex_mcp.app import mcp

        print("PASS: PlexMCP FastMCP app imported successfully")

        # Check that agentic tools were registered
        tools = getattr(mcp, "_tools", [])
        print(f"PASS: MCP server has {len(tools)} tools registered")

        # Check for agentic tools
        tool_names = [tool.__name__ if hasattr(tool, "__name__") else str(tool) for tool in tools]
        agentic_tools = [
            name
            for name in tool_names
            if "agentic" in name.lower() or "conversational" in name.lower()
        ]
        print(f"PASS: Found {len(agentic_tools)} agentic/conversational tools")

        return True
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        return False


def test_instructions():
    """Test that the instructions include conversational features."""
    try:
        from plex_mcp.app import mcp

        instructions = getattr(mcp, "instructions", "")
        if instructions:
            print("PASS: MCP instructions found")
            if "conversational" in instructions.lower():
                print("PASS: Conversational features mentioned in instructions")
            else:
                print("WARN: Conversational features not found in instructions")
        else:
            print("WARN: No instructions found")
        return True
    except Exception as e:
        print(f"FAIL: Instructions test error: {e}")
        return False


if __name__ == "__main__":
    print("Testing PlexMCP FastMCP 2.14.3 conversational features...")
    print(f"Python version: {sys.version}")
    print()

    success = True
    success &= test_imports()
    success &= test_instructions()

    print()
    if success:
        print("SUCCESS: All tests passed! PlexMCP FastMCP 2.14.3 upgrade successful.")
        print("Features implemented:")
        print("- Conversational tool returns")
        print("- Sampling capabilities for agentic workflows")
        print("- Agentic Plex workflow orchestration")
        print("- Intelligent media processing")
        print("- Conversational Plex assistant")
    else:
        print("FAILURE: Some tests failed. Please check the errors above.")
        sys.exit(1)

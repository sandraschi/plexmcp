
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Mock settings/env
os.environ["PLEX_TOKEN"] = "oGA9iEfVYh8ATXmzYrU8"
os.environ["PLEX_URL"] = "http://127.0.0.1:32400"

from app.mcp.client import _get_tool_function

def test():
    tool_name = "plex_server"
    print(f"Testing loading tool: {tool_name}")
    func = _get_tool_function(tool_name)
    if func:
        print(f"SUCCESS: Loaded {tool_name}: {func}")
        # Try calling it
        import asyncio
        try:
            result = asyncio.run(func())
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error calling tool: {e}")
    else:
        print(f"FAILED to load {tool_name}")

if __name__ == "__main__":
    test()

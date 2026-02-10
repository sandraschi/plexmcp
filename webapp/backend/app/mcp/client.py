"""MCP client wrapper for calling PlexMCP tools via direct import."""

import json
import os
import sys
from pathlib import Path
from typing import Any

_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

if src_path.exists():
    src_str = str(src_path)
    os.environ["PYTHONPATH"] = src_str
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

_tool_cache: dict[str, Any] = {}


def _preload_tools() -> None:
    """Preload PlexMCP portmanteau tools for webapp."""
    tool_map = {
        "plex_library": "plex_mcp.tools.portmanteau.library",
        "plex_server": "plex_mcp.tools.portmanteau.server",
        "plex_search": "plex_mcp.tools.portmanteau.search",
        "plex_media": "plex_mcp.tools.portmanteau.media",
        "plex_streaming": "plex_mcp.tools.portmanteau.streaming",
    }
    for tool_name, module_path in tool_map.items():
        try:
            import importlib
            module = importlib.import_module(module_path)
            tool_obj = getattr(module, tool_name)
            if hasattr(tool_obj, "fn"):
                _tool_cache[tool_name] = tool_obj.fn
            elif callable(tool_obj):
                _tool_cache[tool_name] = tool_obj
        except Exception:
            pass


try:
    _preload_tools()
except Exception:
    pass


class MCPClient:
    """Wrapper for calling PlexMCP tools via direct import."""

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a PlexMCP tool."""
        func = _tool_cache.get(tool_name)
        if func and callable(func):
            result = await func(**arguments)
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"result": result}
            if isinstance(result, dict):
                return result
            return {"result": result}
        raise RuntimeError(f"Tool {tool_name} not available")


mcp_client = MCPClient()

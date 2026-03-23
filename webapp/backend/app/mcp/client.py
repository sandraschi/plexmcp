"""MCP client wrapper for calling PlexMCP tools via direct import."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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

_tool_map = {
    "arr_stack": ("plex_mcp.tools.portmanteau.arr_stack", "arr_stack"),
    "plex_library": ("plex_mcp.tools.portmanteau.library", "plex_library"),
    "plex_server": ("plex_mcp.tools.portmanteau.server", "plex_server"),
    "plex_search": ("plex_mcp.tools.portmanteau.search", "plex_search"),
    "plex_media": ("plex_mcp.tools.portmanteau.media", "plex_media"),
    "plex_streaming": ("plex_mcp.tools.portmanteau.streaming", "plex_streaming"),
    "plex_rag": ("plex_mcp.tools.portmanteau.rag", "plex_rag"),
}


def _get_tool_function(tool_name: str) -> Any:
    """Load tool on demand (after env vars are set at startup)."""
    if tool_name not in _tool_map:
        return None

    module_path, func_name = _tool_map[tool_name]
    try:
        import importlib

        module = importlib.import_module(module_path)
        # Force reload to pick up changes
        importlib.reload(module)
        tool_obj = getattr(module, func_name)
        if hasattr(tool_obj, "fn"):
            return tool_obj.fn
        elif callable(tool_obj):
            return tool_obj
    except Exception as e:
        logger.error("Failed to load tool %s: %s", tool_name, e)

    return None


class MCPClient:
    """Wrapper for calling PlexMCP tools via direct import."""

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a PlexMCP tool (load on demand after startup)."""
        func = _get_tool_function(tool_name)
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

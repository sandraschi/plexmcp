"""MCP client wrapper for calling PlexMCP tools via direct import."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _json_safe_media_item(obj: Any) -> Any:
    """Convert Pydantic models / objects in tool payloads to JSON-serializable dicts."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    md = getattr(obj, "model_dump", None)
    if callable(md):
        return md()
    d = getattr(obj, "dict", None)
    if callable(d):
        return d()
    return obj


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
    "plex_ffmpeg_mgr": ("plex_mcp.tools.portmanteau.ffmpeg_mgr", "plex_ffmpeg_mgr"),
    "plex_user": ("plex_mcp.tools.portmanteau.user", "plex_user"),
    "plex_playlist": ("plex_mcp.tools.portmanteau.playlist", "plex_playlist"),
    "plex_collections": ("plex_mcp.tools.portmanteau.collections", "plex_collections"),
    "plex_metadata": ("plex_mcp.tools.portmanteau.metadata", "plex_metadata"),
    "plex_organization": ("plex_mcp.tools.portmanteau.organization", "plex_organization"),
    "plex_performance": ("plex_mcp.tools.portmanteau.performance", "plex_performance"),
    "plex_quality": ("plex_mcp.tools.portmanteau.quality", "plex_quality"),
    "plex_reporting": ("plex_mcp.tools.portmanteau.reporting", "plex_reporting"),
    "plex_help": ("plex_mcp.tools.portmanteau.help", "plex_help"),
    "plex_shutdown": ("plex_mcp.tools.portmanteau.shutdown", "plex_shutdown"),
    "plex_integration": ("plex_mcp.tools.portmanteau.integration", "plex_integration"),
    "plex_media_enrichment": ("plex_mcp.tools.portmanteau.enrichment", "plex_media_enrichment"),
    "plex_audio_mgr": ("plex_mcp.tools.portmanteau.audio_mgr", "plex_audio_mgr"),
    "plex_taste": ("plex_mcp.tools.portmanteau.taste", "plex_taste"),
    "plex_completeness": ("plex_mcp.tools.portmanteau.completeness", "plex_completeness"),
    "plex_canon": ("plex_mcp.tools.portmanteau.canon", "plex_canon"),
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
        if callable(tool_obj):
            return tool_obj
    except Exception:
        logger.exception("Failed to load tool %s", tool_name)

    return None


class MCPClient:
    """Wrapper for calling PlexMCP tools via direct import."""

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a PlexMCP tool (load on demand after startup)."""
        func = _get_tool_function(tool_name)
        if func and callable(func):
            result = await func(**arguments)

            # Handle FastMCP 3.2+ ToolResult objects
            if hasattr(result, "content") and hasattr(result, "meta"):
                # Extract content
                out: dict[str, Any] = {}
                if isinstance(result.content, dict):
                    out = dict(result.content)
                    raw_data = out.get("data")
                    if isinstance(raw_data, list):
                        out["data"] = [_json_safe_media_item(x) for x in raw_data]
                elif hasattr(result, "content") and isinstance(result.content, list):
                    for item in result.content:
                        # Extract text content (most common for tools returning dicts)
                        if hasattr(item, "text") and isinstance(item.text, str):
                            try:
                                # Try to parse as JSON if it looks like it
                                if item.text.strip().startswith(("{", "[")):
                                    data = json.loads(item.text)
                                    if isinstance(data, dict):
                                        out.update(data)
                                    else:
                                        out["data"] = data
                                else:
                                    out["message"] = item.text
                            except json.JSONDecodeError:
                                out["message"] = item.text

                # Merge metadata (prefabs, etc)
                if result.meta:
                    out["_meta"] = result.meta
                    # Tools whose human-readable content is a text summary (not a
                    # dict) have nowhere else to carry the raw list/dict for REST
                    # consumers — they put it in meta["data"]. Promote it to the
                    # top level unless something already claimed "data".
                    if "data" not in out and isinstance(result.meta, dict) and "data" in result.meta:
                        raw_meta_data = result.meta["data"]
                        if isinstance(raw_meta_data, list):
                            out["data"] = [_json_safe_media_item(x) for x in raw_meta_data]
                        else:
                            out["data"] = _json_safe_media_item(raw_meta_data)

                # Extract structured content (Prefab wire JSON for interactive cards)
                if hasattr(result, "structured_content") and result.structured_content:
                    out["_prefab"] = result.structured_content

                # Ensure success flag if present in tool design but lost in ToolResult wrapping
                if "success" not in out and not any(k in out for k in ["error", "error_code"]):
                    out["success"] = True

                return out

            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"result": result}
            if isinstance(result, dict):
                return result
            # Fallback for other types or unhandled ToolResult structure
            return {"result": result}
        raise RuntimeError(tool_name)


mcp_client = MCPClient()

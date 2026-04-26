"""Build system preprompt for chat LLM: MCP server, webapp, libraries, integrations."""

import logging
from typing import Any

from .mcp.client import mcp_client

logger = logging.getLogger(__name__)

MCP_TOOLS = (
    "plex_server (status, info, health, restart, update), "
    "plex_library (list, get, scan, refresh), "
    "plex_search (keyword search), "
    "plex_media (item details, metadata), "
    "plex_streaming (sessions, playback), "
    "plex_rag (sync_metadata to index, semantic_search for natural-language search), "
    "arr_stack (status: optional Radarr/Sonarr/Lidarr HTTP snapshot when RADARR_* / SONARR_* / LIDARR_* env set)"
)
WEBAPP_PAGES = (
    "Overview, Libraries, Movies, Search (keyword), Semantic search (RAG; run Sync/Index metadata first), "
    "Chat (this), Server, Settings. Fleet launch and v1 API available from the webapp backend."
)
INTEGRATIONS = (
    "Plex Media Server (PLEX_URL, PLEX_TOKEN), "
    "optional RAG (LanceDB via mcp-central-docs source on path; index from Semantic search page or plex_rag sync_metadata), "
    "LLM (Ollama/LM Studio via Settings), "
    "optional *arr read-only status (Docker/media stack URLs + API keys in Settings or .env; arr_stack tool, Overview card)."
)


async def _safe_tool(name: str, args: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return await mcp_client.call_tool(name, args)
    except Exception as e:
        logger.debug("chat_context %s: %s", name, e)
        return None


async def build_chat_preprompt() -> str:
    """
    Build a system preprompt string with live context: MCP server, webapp, libraries, integrations.
    Used to give the chat LLM accurate context about the environment.
    """
    parts = [
        "You are the assistant for the PlexMCP webapp. Be concise and accurate.",
        "",
        "## MCP server (PlexMCP)",
        "Tools available to agents and the backend: " + MCP_TOOLS + ".",
        "",
        "## Webapp",
        "Pages: " + WEBAPP_PAGES,
        "",
        "## Integrations",
        INTEGRATIONS,
    ]

    server_result = await _safe_tool("plex_server", {"operation": "info"})
    lib_items: list[Any] = []
    if server_result and server_result.get("success"):
        data = server_result.get("data") or server_result
        if isinstance(data, dict):
            status = data.get("status") or data
            libs = data.get("libraries")
            if isinstance(libs, list):
                lib_items = libs
            name = "Plex"
            version = ""
            if isinstance(status, dict):
                name = status.get("name") or status.get("friendlyName") or name
                version = status.get("version") or version
            parts.append("")
            parts.append("## Plex server (current)")
            parts.append(f"Name: {name}. Version: {version}.")
        elif isinstance(data, str):
            parts.append("")
            parts.append("## Plex server")
            parts.append(data[:500])
    if not (server_result and server_result.get("success")):
        parts.append("")
        parts.append("## Plex server")
        parts.append("Server info not available (check PLEX_TOKEN and PLEX_URL in Settings).")

    if not lib_items:
        lib_result = await _safe_tool("plex_library", {"operation": "list"})
        if lib_result and lib_result.get("success"):
            lib_items = lib_result.get("data") or lib_result.get("libraries") or lib_result.get("results") or []
    if isinstance(lib_items, list) and lib_items:
        lines = []
        for lib in lib_items[:25]:
            if isinstance(lib, dict):
                title = lib.get("title") or lib.get("name") or lib.get("key", "")
                lib_type = lib.get("type") or lib.get("libraryType") or ""
                lid = lib.get("id") or lib.get("key") or ""
                if title or lib_type:
                    lines.append(f"- {title or 'Unnamed'} ({lib_type})" + (f" id={lid}" if lid else ""))
            else:
                lines.append(f"- {lib}")
        if lines:
            parts.append("")
            parts.append("## Media libraries")
            parts.extend(lines)
    else:
        parts.append("")
        parts.append("## Media libraries")
        parts.append("Library list not available.")

    parts.append("")
    parts.append(
        "Answer using the above context. For search, suggest keyword search (Search page or plex_search) or semantic search (Semantic search page or plex_rag semantic_search) if the user wants natural-language queries."
    )
    return "\n".join(parts).strip()

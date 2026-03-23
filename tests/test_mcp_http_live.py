"""Optional live checks against the FastAPI webapp (MCP mounted at /mcp when import succeeds)."""

from __future__ import annotations

import pytest


@pytest.mark.mcp_http
def test_backend_health(mcp_http_live: str) -> None:
    """GET /health returns JSON when webapp backend is running."""
    import httpx

    r = httpx.get(f"{mcp_http_live}/health", timeout=5.0)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"


@pytest.mark.asyncio
async def test_fastmcp_list_tools_inprocess() -> None:
    """In-process tool registration (no HTTP): always runs in CI and locally."""
    from plex_mcp.server import mcp

    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "plex_library" in names
    assert "plex_help" in names
    assert "agentic_plex_workflow" in names

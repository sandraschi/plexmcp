"""Industrial API tests for the PlexMCP webapp.

Verifies and validates the new RAG and Repair Hub endpoints
using mocked services for CI/CD compatibility.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_api_rag_sync_trigger(webapp_app):
    """Test triggering a RAG sync via API."""
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        # Patch the tool call inside mcp_client
        with patch("webapp.backend.app.mcp.client.MCPClient.call_tool", new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"success": True, "indexed_count": 5}

            response = await ac.post("/api/rag/sync")
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["started"] is True


@pytest.mark.asyncio
async def test_api_rag_stats(webapp_app):
    """Test fetching RAG stats via API."""
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        with patch("webapp.backend.app.mcp.client.MCPClient.call_tool", new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"success": True, "data": {"available": True, "count": 100, "backend": "lancedb"}}

            response = await ac.get("/api/rag/stats")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["count"] == 100


@pytest.mark.asyncio
async def test_api_repair_probe(webapp_app):
    """Test probing media via repair API."""
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        with patch("webapp.backend.app.mcp.client.MCPClient.call_tool", new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"success": True, "result": {"format": "mkv", "duration": 3600}}

            response = await ac.post("/api/repair/probe", params={"media_key": "123"})
            assert response.status_code == 200
            assert response.json()["result"]["format"] == "mkv"
            mock_tool.assert_called_once_with("plex_ffmpeg_mgr", {"operation": "probe", "media_key": "123"})

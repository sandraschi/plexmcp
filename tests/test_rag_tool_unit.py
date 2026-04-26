"""Unit tests for the plex_rag portmanteau tool.

Verifies tool dispatch and operation handling for RAG.
"""

from unittest.mock import AsyncMock, patch

import pytest

from plex_mcp.tools.portmanteau.rag import plex_rag


@pytest.mark.asyncio
async def test_plex_rag_status(mock_plex_service):
    """Test the 'status' operation of the plex_rag tool."""
    with patch("plex_mcp.tools.portmanteau.rag._get_plex_service", return_value=mock_plex_service):
        result = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(operation="status")

        assert result["success"] is True
        assert result["operation"] == "status"
        assert "data" in result
        assert result["data"]["available"] is True
        assert "count" in result["data"]


@pytest.mark.asyncio
async def test_plex_rag_sync(mock_plex_service):
    """Test the 'sync_metadata' operation of the plex_rag tool."""
    with patch("plex_mcp.tools.portmanteau.rag._get_plex_service", return_value=mock_plex_service):
        # Mock the service implementation to avoid real DB creation
        with patch(
            "plex_mcp.services.rag_ingestor.PlexIngestor.extract_and_index_all", new_callable=AsyncMock
        ) as mock_sync:
            mock_sync.return_value = 10

            result = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(operation="sync_metadata")

            assert result["success"] is True
            assert result["operation"] == "sync_metadata"
            assert result["indexed_count"] == 10
            mock_sync.assert_called_once()


@pytest.mark.asyncio
async def test_plex_rag_search(mock_plex_service):
    """Test the 'semantic_search' operation of the plex_rag tool."""
    with patch("plex_mcp.tools.portmanteau.rag._get_plex_service", return_value=mock_plex_service):
        with patch("plex_mcp.services.rag_ingestor.PlexIngestor.semantic_search") as mock_search:
            mock_search.return_value = [{"content": "Result 1", "score": 0.9}]

            result = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(
                operation="semantic_search", query="test query"
            )

            assert result["success"] is True
            assert result["operation"] == "semantic_search"
            assert len(result["results"]) == 1
            assert result["results"][0]["content"] == "Result 1"
            mock_search.assert_called_once_with("test query", limit=5, table="plex_media")

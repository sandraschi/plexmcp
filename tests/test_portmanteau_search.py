"""Tests for plex_search portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.search import plex_search


class TestPlexSearch:
    """Test cases for plex_search portmanteau tool."""

    @pytest.mark.asyncio
    async def test_search_operation(self, mock_plex_service):
        """Test search operation."""
        with patch(
            "plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_search.fn(operation="search", query="test")

            assert result["success"] is True
            assert result["operation"] == "search"
            assert "results" in result or "data" in result

    @pytest.mark.asyncio
    async def test_search_operation_missing_query(self):
        """Test search operation requires query."""
        result = await plex_search.fn(operation="search")

        assert result["success"] is False
        assert "query" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_advanced_search_operation(self, mock_plex_service):
        """Test advanced_search operation."""
        with patch(
            "plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_search.fn(operation="advanced_search", query="test", genre="Action")

            assert result["success"] is True
            assert result["operation"] == "advanced_search"

    @pytest.mark.asyncio
    async def test_suggest_operation(self, mock_plex_service):
        """Test suggest operation."""
        with patch(
            "plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_search.fn(operation="suggest", query="test")

            assert result["success"] is True
            assert result["operation"] == "suggest"

    @pytest.mark.asyncio
    async def test_recent_searches_operation(self, mock_plex_service):
        """Test recent_searches operation."""
        with patch(
            "plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_search.fn(operation="recent_searches")

            assert result["success"] is True
            assert result["operation"] == "recent_searches"

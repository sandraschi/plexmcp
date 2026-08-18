"""Tests for plex_search portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.search import plex_search
from tests.helpers import tool_payload


class TestPlexSearch:
    """Test cases for plex_search portmanteau tool."""

    @pytest.mark.asyncio
    async def test_search_operation(self, mock_plex_service):
        """Test search operation."""
        with patch("plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service):
            result = await (plex_search.fn if hasattr(plex_search, "fn") else plex_search)(
                operation="search", query="test"
            )

            # List ops return a readable text summary as content (Prefab structured_content
            # holds the rich UI; non-App hosts get the string).
            content = getattr(result, "content", None)
            if isinstance(content, list) and content:
                text = getattr(content[0], "text", "") or ""
            else:
                text = content or ""
            assert isinstance(text, str) and len(text) > 0
            assert "result" in text.lower()

    @pytest.mark.asyncio
    async def test_search_operation_missing_query(self, mock_plex_service):
        """Test search operation requires query."""
        with patch("plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_search.fn if hasattr(plex_search, "fn") else plex_search)(operation="search")
            )

        assert result["success"] is False
        assert "query" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_advanced_search_operation(self, mock_plex_service):
        """Test advanced_search operation."""
        with patch("plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service):
            result = await (plex_search.fn if hasattr(plex_search, "fn") else plex_search)(
                operation="advanced_search", query="test", genre="Action"
            )

            content = getattr(result, "content", None)
            if isinstance(content, list) and content:
                text = getattr(content[0], "text", "") or ""
            else:
                text = content or ""
            assert isinstance(text, str) and len(text) > 0

    @pytest.mark.asyncio
    async def test_suggest_operation(self, mock_plex_service):
        """Test suggest operation."""
        with patch("plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_search.fn if hasattr(plex_search, "fn") else plex_search)(operation="suggest", query="test")
            )

            assert result["success"] is True
            assert result["operation"] == "suggest"

    @pytest.mark.asyncio
    async def test_recent_searches_operation(self, mock_plex_service):
        """Test recent_searches operation."""
        with patch("plex_mcp.tools.portmanteau.search._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_search.fn if hasattr(plex_search, "fn") else plex_search)(operation="recent_searches")
            )

            assert result["success"] is True
            assert result["operation"] == "recent_searches"

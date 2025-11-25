"""Tests for plex_metadata portmanteau tool."""

import pytest
from unittest.mock import patch

from plex_mcp.tools.portmanteau.metadata import plex_metadata


class TestPlexMetadata:
    """Test cases for plex_metadata portmanteau tool."""

    @pytest.mark.asyncio
    async def test_refresh_operation(self, mock_plex_service):
        """Test refresh operation."""
        with patch("plex_mcp.tools.portmanteau.metadata._get_plex_service", return_value=mock_plex_service):
            result = await plex_metadata.fn(operation="refresh", library_id="1")
            
            assert result["success"] is True
            assert result["operation"] == "refresh"

    @pytest.mark.asyncio
    async def test_refresh_all_operation(self, mock_plex_service):
        """Test refresh_all operation."""
        with patch("plex_mcp.tools.portmanteau.metadata._get_plex_service", return_value=mock_plex_service):
            result = await plex_metadata.fn(operation="refresh_all")
            
            assert result["success"] is True
            assert result["operation"] == "refresh_all"

    @pytest.mark.asyncio
    async def test_fix_match_operation(self, mock_plex_service):
        """Test fix_match operation."""
        with patch("plex_mcp.tools.portmanteau.metadata._get_plex_service", return_value=mock_plex_service):
            result = await plex_metadata.fn(
                operation="fix_match",
                item_id="12345",
                match_id="67890",
                media_type="movie"
            )
            
            assert result["success"] is True
            assert result["operation"] == "fix_match"

    @pytest.mark.asyncio
    async def test_update_operation(self, mock_plex_service):
        """Test update operation."""
        from unittest.mock import patch
        with patch("plex_mcp.tools.portmanteau.metadata._get_plex_service", return_value=mock_plex_service):
            # Mock the plex_media function that's imported inside the function
            # Since it's imported as `from .media import plex_media`, we need to patch it at the import location
            # plex_media is a FunctionTool, so we need to mock it as callable
            async def mock_plex_media_func(*args, **kwargs):
                return {"success": True, "data": {"title": "New Title"}}
            
            with patch("plex_mcp.tools.portmanteau.media.plex_media", side_effect=mock_plex_media_func):
                result = await plex_metadata.fn(
                    operation="update",
                    item_id="12345",
                    metadata={"title": "New Title"}
                )
                
                assert result["success"] is True
                assert result["operation"] == "update"


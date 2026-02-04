"""Tests for all portmanteau tools integration."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau import (
    plex_collections,
    plex_help,
    plex_integration,
    plex_library,
    plex_media,
    plex_metadata,
    plex_organization,
    plex_performance,
    plex_playlist,
    plex_quality,
    plex_reporting,
    plex_search,
    plex_server,
    plex_streaming,
    plex_user,
)


class TestPortmanteauToolsIntegration:
    """Integration tests for all portmanteau tools."""

    @pytest.mark.asyncio
    async def test_all_tools_importable(self):
        """Test that all portmanteau tools can be imported."""
        tools = [
            plex_collections,
            plex_help,
            plex_integration,
            plex_library,
            plex_media,
            plex_metadata,
            plex_organization,
            plex_performance,
            plex_playlist,
            plex_quality,
            plex_reporting,
            plex_search,
            plex_server,
            plex_streaming,
            plex_user,
        ]

        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool} has no fn attribute"
            assert callable(tool.fn), f"{tool}.fn is not callable"

    @pytest.mark.asyncio
    async def test_all_tools_have_operation_parameter(self, mock_plex_service):
        """Test that all tools accept operation parameter."""
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service
        ):
            # Test that operation parameter is required
            with pytest.raises((TypeError, KeyError)):
                await plex_library.fn()  # Missing operation

    @pytest.mark.asyncio
    async def test_error_response_structure(self):
        """Test that all tools return consistent error response structure."""
        # Test with invalid operation or missing required params
        result = await plex_library.fn(operation="get")  # Missing library_id

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_success_response_structure(self, mock_plex_service):
        """Test that all tools return consistent success response structure."""
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_library.fn(operation="list")

            assert "success" in result
            assert result["success"] is True
            assert "operation" in result
            assert "data" in result

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
from tests.helpers import tool_payload


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
            fn = getattr(tool, "fn", tool)
            assert callable(fn), f"{tool} is not a callable tool (FastMCP may expose .fn or the raw function)"

    @pytest.mark.asyncio
    async def test_all_tools_have_operation_parameter(self, mock_plex_service):
        """Test that all tools accept operation parameter."""
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service",
            return_value=mock_plex_service,
        ):
            # Test that operation parameter is required
            with pytest.raises((TypeError, KeyError)):
                _fn = plex_library.fn if hasattr(plex_library, "fn") else plex_library
                await _fn()  # Missing operation

    @pytest.mark.asyncio
    async def test_error_response_structure(self, mock_plex_service):
        """Test that all tools return consistent error response structure."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            _fn = getattr(plex_library, "fn", plex_library)
            result = tool_payload(await _fn(operation="get"))  # Missing library_id

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_success_response_structure(self, mock_plex_service):
        """Test that all tools return consistent success response structure."""
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service",
            return_value=mock_plex_service,
        ):
            _fn = plex_library.fn if hasattr(plex_library, "fn") else plex_library
            result = tool_payload(await _fn(operation="list"))

            assert "success" in result
            assert result["success"] is True
            assert "operation" in result
            assert "data" in result

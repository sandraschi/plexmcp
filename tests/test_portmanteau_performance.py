"""Tests for plex_performance portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.performance import plex_performance


class TestPlexPerformance:
    """Test cases for plex_performance portmanteau tool."""

    @pytest.mark.asyncio
    async def test_get_transcode_settings_operation(self, mock_plex_service):
        """Test get_transcode_settings operation."""
        with patch(
            "plex_mcp.tools.portmanteau.performance._get_plex_service",
            return_value=mock_plex_service,
        ):
            result = await plex_performance.fn(operation="get_transcode_settings")

            assert result["success"] is True
            assert result["operation"] == "get_transcode_settings"

    @pytest.mark.asyncio
    async def test_get_transcoding_status_operation(self, mock_plex_service):
        """Test get_transcoding_status operation."""
        with patch(
            "plex_mcp.tools.portmanteau.performance._get_plex_service",
            return_value=mock_plex_service,
        ):
            result = await plex_performance.fn(operation="get_transcoding_status")

            assert result["success"] is True
            assert result["operation"] == "get_transcoding_status"

    @pytest.mark.asyncio
    async def test_get_bandwidth_operation(self, mock_plex_service):
        """Test get_bandwidth operation."""
        with patch(
            "plex_mcp.tools.portmanteau.performance._get_plex_service",
            return_value=mock_plex_service,
        ):
            result = await plex_performance.fn(operation="get_bandwidth")

            assert result["success"] is True
            assert result["operation"] == "get_bandwidth"

    @pytest.mark.asyncio
    async def test_get_server_status_operation(self, mock_plex_service):
        """Test get_server_status operation."""
        with patch(
            "plex_mcp.tools.portmanteau.performance._get_plex_service",
            return_value=mock_plex_service,
        ):
            result = await plex_performance.fn(operation="get_server_status")

            assert result["success"] is True
            assert result["operation"] == "get_server_status"

    @pytest.mark.asyncio
    async def test_get_server_info_operation(self, mock_plex_service):
        """Test get_server_info operation."""
        with patch(
            "plex_mcp.tools.portmanteau.performance._get_plex_service",
            return_value=mock_plex_service,
        ):
            result = await plex_performance.fn(operation="get_server_info")

            assert result["success"] is True
            assert result["operation"] == "get_server_info"

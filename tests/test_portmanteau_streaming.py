"""Tests for plex_streaming portmanteau tool."""

import pytest
from unittest.mock import patch

from plex_mcp.tools.portmanteau.streaming import plex_streaming


class TestPlexStreaming:
    """Test cases for plex_streaming portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_sessions_operation(self, mock_plex_service):
        """Test list_sessions operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="list_sessions")
            
            assert result["success"] is True
            assert result["operation"] == "list_sessions"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_clients_operation(self, mock_plex_service):
        """Test list_clients operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="list_clients")
            
            assert result["success"] is True
            assert result["operation"] == "list_clients"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_play_operation(self, mock_plex_service):
        """Test play operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(
                operation="play",
                client_id="client123",
                media_key="12345"
            )
            
            assert result["success"] is True
            assert result["operation"] == "play"

    @pytest.mark.asyncio
    async def test_play_operation_missing_params(self):
        """Test play operation requires client_id and media_key."""
        result = await plex_streaming.fn(operation="play")
        
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_pause_operation(self, mock_plex_service):
        """Test pause operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="pause", client_id="client123")
            
            assert result["success"] is True
            assert result["operation"] == "pause"

    @pytest.mark.asyncio
    async def test_stop_operation(self, mock_plex_service):
        """Test stop operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="stop", client_id="client123")
            
            assert result["success"] is True
            assert result["operation"] == "stop"

    @pytest.mark.asyncio
    async def test_seek_operation(self, mock_plex_service):
        """Test seek operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(
                operation="seek",
                client_id="client123",
                seek_to=60000
            )
            
            assert result["success"] is True
            assert result["operation"] == "seek"

    @pytest.mark.asyncio
    async def test_skip_next_operation(self, mock_plex_service):
        """Test skip_next operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="skip_next", client_id="client123")
            
            assert result["success"] is True
            assert result["operation"] == "skip_next"

    @pytest.mark.asyncio
    async def test_skip_previous_operation(self, mock_plex_service):
        """Test skip_previous operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(operation="skip_previous", client_id="client123")
            
            assert result["success"] is True
            assert result["operation"] == "skip_previous"

    @pytest.mark.asyncio
    async def test_control_operation(self, mock_plex_service):
        """Test control operation."""
        with patch("plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=mock_plex_service):
            result = await plex_streaming.fn(
                operation="control",
                client_id="client123",
                action="play",
                media_key="12345"
            )
            
            assert result["success"] is True
            assert result["operation"] == "control"


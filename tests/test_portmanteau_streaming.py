"""Tests for plex_streaming portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.streaming import plex_streaming


class TestPlexStreaming:
    """Test cases for plex_streaming portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_sessions_operation(self, plex_service):
        """Test list_sessions operation (uses real server if available, otherwise mocks)."""
        # Ensure connected if using real service
        if hasattr(plex_service, "_initialized") and not plex_service._initialized:
            try:
                await plex_service.connect()
            except Exception:
                pass  # Will use mocked behavior

        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="list_sessions")

            assert result["success"] is True
            assert result["operation"] == "list_sessions"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_clients_operation(self, plex_service):
        """Test list_clients operation (uses real server if available, otherwise mocks)."""
        # Ensure connected if using real service
        if hasattr(plex_service, "_initialized") and not plex_service._initialized:
            try:
                await plex_service.connect()
            except Exception:
                pass  # Will use mocked behavior

        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="list_clients")

            assert result["success"] is True
            assert result["operation"] == "list_clients"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_play_operation(self, plex_service):
        """Test play operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(
                operation="play", client_id="client123", media_key="12345"
            )

            assert result["success"] is True
            assert result["operation"] == "play"

    @pytest.mark.asyncio
    async def test_play_operation_missing_params(self):
        """Test play operation requires client_id and media_key."""
        result = await plex_streaming.fn(operation="play")

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_pause_operation(self, plex_service):
        """Test pause operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="pause", client_id="client123")

            assert result["success"] is True
            assert result["operation"] == "pause"

    @pytest.mark.asyncio
    async def test_stop_operation(self, plex_service):
        """Test stop operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="stop", client_id="client123")

            assert result["success"] is True
            assert result["operation"] == "stop"

    @pytest.mark.asyncio
    async def test_seek_operation(self, plex_service):
        """Test seek operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="seek", client_id="client123", seek_to=60000)

            assert result["success"] is True
            assert result["operation"] == "seek"

    @pytest.mark.asyncio
    async def test_skip_next_operation(self, plex_service):
        """Test skip_next operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="skip_next", client_id="client123")

            assert result["success"] is True
            assert result["operation"] == "skip_next"

    @pytest.mark.asyncio
    async def test_skip_previous_operation(self, plex_service):
        """Test skip_previous operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(operation="skip_previous", client_id="client123")

            assert result["success"] is True
            assert result["operation"] == "skip_previous"

    @pytest.mark.asyncio
    async def test_control_operation(self, plex_service):
        """Test control operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(
                operation="control", client_id="client123", action="play", media_key="12345"
            )

            assert result["success"] is True
            assert result["operation"] == "control"

    @pytest.mark.asyncio
    async def test_set_quality_operation(self, plex_service):
        """Test set_quality operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(
                operation="set_quality", client_id="client123", quality="1080p"
            )

            # set_quality is not yet fully implemented, should return NOT_IMPLEMENTED
            assert result["success"] is False
            assert result["error_code"] == "NOT_IMPLEMENTED"

    @pytest.mark.asyncio
    async def test_set_quality_missing_params(self):
        """Test set_quality operation requires quality parameter."""
        result = await plex_streaming.fn(operation="set_quality", client_id="client123")

        assert result["success"] is False
        assert result["error_code"] == "MISSING_QUALITY"

    @pytest.mark.asyncio
    async def test_set_volume_operation(self, plex_service):
        """Test set_volume operation (uses real server if available, otherwise mocks)."""
        with patch(
            "plex_mcp.tools.portmanteau.streaming._get_plex_service", return_value=plex_service
        ):
            result = await plex_streaming.fn(
                operation="set_volume", client_id="client123", volume=75
            )

            assert result["success"] is True
            assert result["operation"] == "set_volume"
            assert result["volume"] == 75

    @pytest.mark.asyncio
    async def test_set_volume_missing_client_id(self):
        """Test set_volume operation requires client_id."""
        result = await plex_streaming.fn(operation="set_volume", volume=75)

        assert result["success"] is False
        assert result["error_code"] == "MISSING_CLIENT_ID"

    @pytest.mark.asyncio
    async def test_set_volume_missing_volume(self):
        """Test set_volume operation requires volume parameter."""
        result = await plex_streaming.fn(operation="set_volume", client_id="client123")

        assert result["success"] is False
        assert result["error_code"] == "MISSING_VOLUME"

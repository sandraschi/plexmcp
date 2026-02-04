"""Tests for plex_playlist portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.playlist import plex_playlist


class TestPlexPlaylist:
    """Test cases for plex_playlist portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_operation(self, mock_plex_service):
        """Test list operation returns playlists."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(operation="list")

            assert result["success"] is True
            assert result["operation"] == "list"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_operation(self, mock_plex_service):
        """Test get operation returns playlist details."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(operation="get", playlist_id="playlist123")

            assert result["success"] is True
            assert result["operation"] == "get"

    @pytest.mark.asyncio
    async def test_create_operation(self, mock_plex_service):
        """Test create operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(
                operation="create", title="My Playlist", items=["12345", "67890"]
            )

            assert result["success"] is True
            assert result["operation"] == "create"

    @pytest.mark.asyncio
    async def test_create_operation_missing_required(self):
        """Test create operation requires title and items."""
        result = await plex_playlist.fn(operation="create")

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_update_operation(self, mock_plex_service):
        """Test update operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(
                operation="update", playlist_id="playlist123", title="Updated Playlist"
            )

            assert result["success"] is True
            assert result["operation"] == "update"

    @pytest.mark.asyncio
    async def test_delete_operation(self, mock_plex_service):
        """Test delete operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(operation="delete", playlist_id="playlist123")

            assert result["success"] is True
            assert result["operation"] == "delete"

    @pytest.mark.asyncio
    async def test_add_items_operation(self, mock_plex_service):
        """Test add_items operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(
                operation="add_items", playlist_id="playlist123", items=["54321"]
            )

            assert result["success"] is True
            assert result["operation"] == "add_items"

    @pytest.mark.asyncio
    async def test_remove_items_operation(self, mock_plex_service):
        """Test remove_items operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(
                operation="remove_items", playlist_id="playlist123", items=["12345"]
            )

            assert result["success"] is True
            assert result["operation"] == "remove_items"

    @pytest.mark.asyncio
    async def test_get_analytics_operation(self, mock_plex_service):
        """Test get_analytics operation."""
        with patch(
            "plex_mcp.tools.portmanteau.playlist._get_plex_service", return_value=mock_plex_service
        ):
            result = await plex_playlist.fn(operation="get_analytics", playlist_id="playlist123")

            assert result["success"] is True
            assert result["operation"] == "get_analytics"

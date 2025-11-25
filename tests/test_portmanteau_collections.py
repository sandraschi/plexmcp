"""Tests for plex_collections portmanteau tool."""

import pytest
from unittest.mock import patch

from plex_mcp.tools.portmanteau.collections import plex_collections


class TestPlexCollections:
    """Test cases for plex_collections portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_operation(self, mock_plex_service):
        """Test list operation returns collections."""
        with patch("plex_mcp.tools.portmanteau.collections._get_plex_service", return_value=mock_plex_service):
            result = await plex_collections.fn(operation="list")
            
            assert result["success"] is True
            assert result["operation"] == "list"
            assert "collections" in result or "data" in result

    @pytest.mark.asyncio
    async def test_get_operation(self, mock_plex_service):
        """Test get operation returns collection details."""
        with patch("plex_mcp.tools.portmanteau.collections._get_plex_service", return_value=mock_plex_service):
            result = await plex_collections.fn(operation="get", collection_id="collection123")
            
            assert result["success"] is True
            assert result["operation"] == "get"

    @pytest.mark.asyncio
    async def test_create_operation(self, mock_plex_service):
        """Test create operation."""
        with patch("plex_mcp.tools.portmanteau.collections._get_plex_service", return_value=mock_plex_service):
            result = await plex_collections.fn(
                operation="create",
                title="My Collection",
                library_id="1",
                items=["12345"]
            )
            
            assert result["success"] is True
            assert result["operation"] == "create"

    @pytest.mark.asyncio
    async def test_update_operation(self, mock_plex_service):
        """Test update operation."""
        with patch("plex_mcp.tools.portmanteau.collections._get_plex_service", return_value=mock_plex_service):
            result = await plex_collections.fn(
                operation="update",
                collection_id="collection123",
                title="Updated Collection"
            )
            
            assert result["success"] is True
            assert result["operation"] == "update"

    @pytest.mark.asyncio
    async def test_delete_operation(self, mock_plex_service):
        """Test delete operation."""
        with patch("plex_mcp.tools.portmanteau.collections._get_plex_service", return_value=mock_plex_service):
            result = await plex_collections.fn(operation="delete", collection_id="collection123")
            
            assert result["success"] is True
            assert result["operation"] == "delete"


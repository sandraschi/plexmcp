"""Tests for plex_user portmanteau tool."""

import pytest
from unittest.mock import patch

from plex_mcp.tools.portmanteau.user import plex_user


class TestPlexUser:
    """Test cases for plex_user portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_operation(self, mock_plex_service):
        """Test list operation returns users."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(operation="list")
            
            assert result["success"] is True
            assert result["operation"] == "list"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_operation(self, mock_plex_service):
        """Test get operation returns user details."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(operation="get", user_id="user123")
            
            assert result["success"] is True
            assert result["operation"] == "get"

    @pytest.mark.asyncio
    async def test_get_operation_missing_id(self):
        """Test get operation requires user_id."""
        result = await plex_user.fn(operation="get")
        
        assert result["success"] is False
        assert "user_id" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_create_operation(self, mock_plex_service):
        """Test create operation."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(
                operation="create",
                username="newuser",
                email="newuser@example.com",
                password="securepass123"
            )
            
            assert result["success"] is True
            assert result["operation"] == "create"

    @pytest.mark.asyncio
    async def test_create_operation_missing_required(self):
        """Test create operation requires username, email, password."""
        result = await plex_user.fn(operation="create")
        
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_update_operation(self, mock_plex_service):
        """Test update operation."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(
                operation="update",
                user_id="user123",
                username="updateduser"
            )
            
            assert result["success"] is True
            assert result["operation"] == "update"

    @pytest.mark.asyncio
    async def test_delete_operation(self, mock_plex_service):
        """Test delete operation."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(operation="delete", user_id="user123")
            
            assert result["success"] is True
            assert result["operation"] == "delete"

    @pytest.mark.asyncio
    async def test_update_permissions_operation(self, mock_plex_service):
        """Test update_permissions operation."""
        with patch("plex_mcp.tools.portmanteau.user._get_plex_service", return_value=mock_plex_service):
            result = await plex_user.fn(
                operation="update_permissions",
                user_id="user123",
                permissions={"allowSync": True}
            )
            
            assert result["success"] is True
            assert result["operation"] == "update_permissions"


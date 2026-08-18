"""Tests for plex_library portmanteau tool."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.library import plex_library
from tests.helpers import tool_payload


class TestPlexLibrary:
    """Test cases for plex_library portmanteau tool."""

    @pytest.mark.asyncio
    async def test_list_operation(self, mock_plex_service):
        """Test list operation returns libraries."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(operation="list")

            content = getattr(result, "content", None)
            if isinstance(content, list) and content:
                text = getattr(content[0], "text", "") or ""
            else:
                text = content or ""
            assert isinstance(text, str) and len(text) > 0

    @pytest.mark.asyncio
    async def test_get_operation(self, mock_plex_service):
        """Test get operation returns library details."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                    operation="get", library_id="1"
                )
            )

            assert result["success"] is True
            assert result["operation"] == "get"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_operation_missing_id(self, mock_plex_service):
        """Test get operation requires library_id."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(operation="get")
            )

        assert result["success"] is False
        assert "library_id" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_scan_operation(self, mock_plex_service):
        """Test scan operation."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                    operation="scan", library_id="1"
                )
            )

            assert result["success"] is True
            assert result["operation"] == "scan"

    @pytest.mark.asyncio
    async def test_refresh_operation(self, mock_plex_service):
        """Test refresh operation."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                    operation="refresh", library_id="1"
                )
            )

            assert result["success"] is True
            assert result["operation"] == "refresh"

    @pytest.mark.asyncio
    async def test_optimize_operation(self, mock_plex_service):
        """Test optimize operation."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                    operation="optimize", library_id="1"
                )
            )

            assert result["success"] is True
            assert result["operation"] == "optimize"

    @pytest.mark.asyncio
    async def test_empty_trash_operation(self, mock_plex_service):
        """Test empty_trash operation."""
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                    operation="empty_trash", library_id="1"
                )
            )

            assert result["success"] is True
            assert result["operation"] == "empty_trash"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling when PlexService fails."""
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service",
            side_effect=Exception("Connection failed"),
        ):
            result = tool_payload(
                await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(operation="list")
            )

            assert result["success"] is False
            assert "error" in result
            assert "suggestions" in result

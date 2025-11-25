"""Tests for plex_server portmanteau tool."""

import pytest
from unittest.mock import patch

from plex_mcp.tools.portmanteau.server import plex_server


class TestPlexServer:
    """Test cases for plex_server portmanteau tool."""

    @pytest.mark.asyncio
    async def test_status_operation(self, mock_plex_service):
        """Test status operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = await plex_server.fn(operation="status")
            
            assert result["success"] is True
            assert result["operation"] == "status"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_info_operation(self, mock_plex_service):
        """Test info operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = await plex_server.fn(operation="info")
            
            assert result["success"] is True
            assert result["operation"] == "info"

    @pytest.mark.asyncio
    async def test_health_operation(self, mock_plex_service):
        """Test health operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = await plex_server.fn(operation="health")
            
            assert result["success"] is True
            assert result["operation"] == "health"

    @pytest.mark.asyncio
    async def test_maintenance_operation(self, mock_plex_service):
        """Test maintenance operation."""
        from unittest.mock import AsyncMock
        from plex_mcp.api.admin import ServerMaintenanceResult
        
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            with patch("plex_mcp.api.admin.run_server_maintenance", new_callable=AsyncMock) as mock_maintenance:
                mock_maintenance.return_value = ServerMaintenanceResult(
                    operation="optimize",
                    status="completed",
                    details={},
                    space_freed_gb=0,
                    items_processed=0,
                    duration_seconds=0,
                    recommendations=[],
                    warnings=[],
                    next_recommended=None
                )
                result = await plex_server.fn(
                    operation="maintenance",
                    maintenance_operation="optimize"
                )
                
                assert result["success"] is True
                assert result["operation"] == "maintenance"


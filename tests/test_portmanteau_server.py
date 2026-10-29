"""Tests for plex_server portmanteau tool."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from plex_mcp.models.server import PlexServerStatus
from plex_mcp.prefabs import build_server_status
from plex_mcp.services.plex_service import PlexService
from plex_mcp.tools.portmanteau.server import plex_server
from tests.helpers import tool_payload


class TestPlexServer:
    """Test cases for plex_server portmanteau tool."""

    @pytest.mark.asyncio
    async def test_status_operation(self, mock_plex_service):
        """Test status operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_server.fn if hasattr(plex_server, "fn") else plex_server)(operation="status")
            )

            assert result["success"] is True
            assert result["operation"] == "status"
            assert "data" in result

    def test_status_model_preserves_live_counts(self):
        """Pydantic must not silently discard the fields the status card uses."""
        status = PlexServerStatus(
            name="AS6804T-6C42",
            version="1.43.3",
            platform="Linux",
            updated_at=0,
            active_sessions=2,
            libraries=["Movies", "TV Shows"],
        ).model_dump()

        assert status["connected"] is True
        assert status["active_sessions"] == 2
        assert status["libraries"] == ["Movies", "TV Shows"]

    def test_successful_status_probe_is_connected(self):
        """Reaching Plex and reading sections is itself a positive live probe."""
        service = object.__new__(PlexService)
        server = MagicMock()
        server.friendlyName = "AS6804T-6C42"
        server.version = "1.43.3"
        server.platform = "Linux"
        server.updated_at = datetime(2026, 8, 5)
        server.sessions.return_value = [object()]
        server.library.sections.return_value = [
            SimpleNamespace(title="Movies"),
            SimpleNamespace(title="TV Shows"),
        ]
        service.server = server

        status = PlexServerStatus(**service._get_server_status_sync())

        assert status.connected is True
        assert status.active_sessions == 1
        assert status.libraries == ["Movies", "TV Shows"]

    def test_status_prefab_reports_online_and_library_count(self):
        """The user-facing card must render counts, not a list or false zero."""
        status = PlexServerStatus(
            name="AS6804T-6C42",
            version="1.43.3",
            platform="Linux",
            updated_at=0,
            connected=True,
            active_sessions=2,
            libraries=["Movies", "TV Shows"],
        ).model_dump()

        app = build_server_status(status)
        badge = app.view.children[0].children[1]
        metrics = {item.label: item.value for item in app.view.children[2].children}

        assert badge.label == "Online"
        assert metrics["Active Sessions"] == "2"
        assert metrics["Libraries"] == "2"

    @pytest.mark.asyncio
    async def test_info_operation(self, mock_plex_service):
        """Test info operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_server.fn if hasattr(plex_server, "fn") else plex_server)(operation="info")
            )

            assert result["success"] is True
            assert result["operation"] == "info"

    @pytest.mark.asyncio
    async def test_health_operation(self, mock_plex_service):
        """Test health operation."""
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=mock_plex_service):
            result = tool_payload(
                await (plex_server.fn if hasattr(plex_server, "fn") else plex_server)(operation="health")
            )

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
                    next_recommended=None,
                )
                result = tool_payload(
                    await (plex_server.fn if hasattr(plex_server, "fn") else plex_server)(
                        operation="maintenance", maintenance_operation="optimize"
                    )
                )

                assert result["success"] is True
                assert result["operation"] == "maintenance"

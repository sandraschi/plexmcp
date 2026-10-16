"""Tests for plex_completeness portmanteau tool (TV gap detection)."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.completeness import plex_completeness
from tests.helpers import tool_payload


async def _call(**kwargs):
    fn = plex_completeness.fn if hasattr(plex_completeness, "fn") else plex_completeness
    return tool_payload(await fn(**kwargs))


class TestPlexCompleteness:
    @pytest.mark.asyncio
    async def test_status(self, mock_plex_service):
        with patch("plex_mcp.tools.portmanteau.completeness._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="status")
        assert result["success"] is True
        assert result["operation"] == "status"
        libs = result["data"]["show_libraries"]
        assert len(libs) == 1 and libs[0]["title"] == "TV Shows"
        assert result["data"]["total_shows"] == 1

    @pytest.mark.asyncio
    async def test_scan_library_finds_gap(self, mock_plex_service):
        with patch("plex_mcp.tools.portmanteau.completeness._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="scan_library", library_id="2")
        assert result["success"] is True
        data = result["data"]
        assert data["shows_scanned"] == 1
        assert data["total_missing_episodes"] == 1
        show = data["shows"][0]
        assert show["show_title"] == "Mock Show"
        assert show["missing_count"] == 1
        assert show["seasons"][0]["gaps"] == ["S01E03"]
        assert show["seasons"][1]["missing"] == []
        assert show["completion_percent"] == pytest.approx(83.3, abs=0.1)

    @pytest.mark.asyncio
    async def test_scan_library_requires_id(self, mock_plex_service):
        with patch("plex_mcp.tools.portmanteau.completeness._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="scan_library")
        assert result["success"] is False
        assert "library_id" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_show_gaps(self, mock_plex_service):
        with patch("plex_mcp.tools.portmanteau.completeness._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="show_gaps", rating_key="s1")
        assert result["success"] is True
        assert result["data"]["missing_count"] == 1
        assert result["data"]["seasons"][0]["missing"] == [3]

    @pytest.mark.asyncio
    async def test_show_gaps_requires_key(self, mock_plex_service):
        with patch("plex_mcp.tools.portmanteau.completeness._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="show_gaps")
        assert result["success"] is False
        assert "rating_key" in result["error"].lower()

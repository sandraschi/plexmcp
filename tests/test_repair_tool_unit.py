"""Unit tests for the plex_ffmpeg_mgr portmanteau tool.

Verifies technical probe and repair operation dispatch.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from plex_mcp.tools.portmanteau.ffmpeg_mgr import plex_ffmpeg_mgr


@pytest.mark.asyncio
async def test_ffmpeg_probe():
    """Test the 'probe' operation."""
    # Mock PlexService.get_media_analysis via _get_plex_service
    with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr._get_plex_service") as mock_get_plex:
        mock_plex = AsyncMock()
        mock_plex.get_media_analysis.return_value = {"media": [{"parts": [{"file": "test.mkv"}]}]}
        mock_get_plex.return_value = mock_plex

        with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr.Path.exists", return_value=True):
            with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr._handle_probe") as mock_probe:
                mock_probe.return_value = json.dumps({"success": True, "operation": "probe", "result": {"streams": []}})

                # The tool is wrapped by FastMCP decorator, so we call it directly (it's async)
                result_json = await plex_ffmpeg_mgr(operation="probe", media_key="123")
                result = json.loads(result_json)

                assert result["success"] is True
                assert result["operation"] == "probe"
                mock_probe.assert_called_once()


@pytest.mark.asyncio
async def test_ffmpeg_sync_audio():
    """Test the 'sync_audio' operation."""
    with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr._get_plex_service") as mock_get_plex:
        mock_plex = AsyncMock()
        mock_plex.get_media_analysis.return_value = {"media": [{"parts": [{"file": "test.mkv"}]}]}
        mock_get_plex.return_value = mock_plex

        with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr.Path.exists", return_value=True):
            with patch("plex_mcp.tools.portmanteau.ffmpeg_mgr._handle_sync_audio") as mock_sync:
                mock_sync.return_value = json.dumps(
                    {"success": True, "operation": "sync_audio", "result": {"message": "Success"}}
                )

                result_json = await plex_ffmpeg_mgr(operation="sync_audio", media_key="123", offset_seconds=1.5)
                result = json.loads(result_json)

                assert result["success"] is True
                assert result["operation"] == "sync_audio"
                mock_sync.assert_called_once()

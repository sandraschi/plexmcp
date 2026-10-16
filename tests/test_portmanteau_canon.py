"""Tests for plex_canon portmanteau tool (holdings vs canon lists)."""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.canon import _norm, _titles_match, _year_ok, plex_canon
from tests.helpers import tool_payload

MOD = "plex_mcp.tools.portmanteau.canon"


async def _call(**kwargs):
    fn = plex_canon.fn if hasattr(plex_canon, "fn") else plex_canon
    return tool_payload(await fn(**kwargs))


class TestCanonMatching:
    def test_norm(self):
        assert _norm("The Godfather: Part II!") == "the godfather part ii"

    def test_titles_match(self):
        assert _titles_match("Stalker", "Stalker (1979)")
        assert _titles_match("Stalker (1979)", "Stalker")
        assert not _titles_match("It", "It (2017)")  # min-length guard
        assert not _titles_match("Stalker", "Solaris")

    def test_year_ok(self):
        assert _year_ok(1979, 1979)
        assert _year_ok(1979, 1980)
        assert not _year_ok(1979, 2000)
        assert _year_ok(None, 2000)
        assert _year_ok(1979, None)


class TestPlexCanon:
    @pytest.mark.asyncio
    async def test_list_canons(self):
        result = await _call(operation="list_canons")
        assert result["success"] is True
        ids = [c["id"] for c in result["data"]["canons"]]
        assert ids == ["oscar_best_picture", "afi_100", "tmdb_top", "check_list"]

    @pytest.mark.asyncio
    async def test_check_list_owned(self, mock_plex_service):
        mock_plex_service.search_media.return_value = [{"id": "m1", "title": "Stalker", "year": 1979, "type": "movie"}]
        with patch(f"{MOD}._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="check_list", items=[{"title": "Stalker", "year": 1979}])
        assert result["success"] is True
        assert result["data"]["owned_count"] == 1
        assert result["data"]["missing_count"] == 0
        assert result["data"]["owned"][0]["held_as"]["id"] == "m1"

    @pytest.mark.asyncio
    async def test_check_list_missing_and_year_gate(self, mock_plex_service):
        mock_plex_service.search_media.return_value = [{"id": "m9", "title": "Stalker", "year": 2000, "type": "movie"}]
        with patch(f"{MOD}._get_plex_service", return_value=mock_plex_service):
            result = await _call(
                operation="check_list",
                items=[{"title": "Stalker", "year": 1979}, {"title": "Unknown Film XYZ"}],
            )
        assert result["success"] is True
        assert result["data"]["owned_count"] == 0
        assert result["data"]["missing_count"] == 2

    @pytest.mark.asyncio
    async def test_check_list_requires_items(self, mock_plex_service):
        with patch(f"{MOD}._get_plex_service", return_value=mock_plex_service):
            result = await _call(operation="check_list")
        assert result["success"] is False
        assert "items" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_afi_100(self, mock_plex_service):
        mock_plex_service.search_media.return_value = [
            {"id": "m1", "title": "Citizen Kane", "year": 1941, "type": "movie"}
        ]
        with (
            patch(f"{MOD}._get_plex_service", return_value=mock_plex_service),
            patch(
                f"{MOD}._fetch_afi_100",
                return_value=[
                    {"rank": 1, "title": "Citizen Kane", "year": 1941},
                    {"rank": 2, "title": "Missing Masterpiece XYZ", "year": 1950},
                ],
            ),
        ):
            result = await _call(operation="afi_100", limit=2)
        assert result["success"] is True
        assert result["data"]["owned_count"] == 1
        assert result["data"]["missing_count"] == 1
        assert result["data"]["missing"][0]["rank"] == 2

    @pytest.mark.asyncio
    async def test_tmdb_top_needs_key(self, mock_plex_service):
        with (
            patch(f"{MOD}._get_plex_service", return_value=mock_plex_service),
            patch(f"{MOD}._tmdb_key", return_value=""),
        ):
            result = await _call(operation="tmdb_top", media_type="movie", limit=5)
        assert result["success"] is False
        assert "TMDB_API_KEY" in result["error"]

"""Shared AsyncMock PlexService shape for portmanteau unit tests."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock


def _dt() -> datetime:
    return datetime(2020, 1, 1)


def _mock_playlist_obj(rating_key: str = "pl1") -> MagicMock:
    """Minimal playlist object for _format_playlist in playlist.py."""
    m = MagicMock()
    m.ratingKey = rating_key
    m.title = "Mock Playlist"
    m.playlistType = "video"
    m.summary = ""
    m.duration = 0
    m.items = MagicMock(return_value=[])
    m.smart = False
    m.addedAt = _dt()
    m.updatedAt = _dt()
    m.username = "mock"
    m.delete = AsyncMock()
    m.addItems = AsyncMock()
    m.reload = MagicMock()
    m.editTitle = MagicMock()
    m.editSummary = MagicMock()
    return m


def build_mock_plex_service() -> MagicMock:
    """Return a MagicMock with async methods used across portmanteau tools."""
    svc = MagicMock()
    svc._initialized = True

    status = MagicMock()
    status.dict.return_value = {
        "friendlyName": "MockPlex",
        "version": "1.0.0",
        "platform": "Linux",
    }

    async def _connect() -> None:
        svc._initialized = True

    svc.connect = AsyncMock(side_effect=_connect)
    lib_row = [{"id": "1", "key": "1", "title": "Movies", "type": "movie"}]
    svc.get_libraries = AsyncMock(return_value=lib_row)
    svc.list_libraries = AsyncMock(return_value=lib_row)
    svc.get_library = AsyncMock(
        return_value={"id": "1", "key": "1", "title": "Movies", "type": "movie"}
    )
    svc.get_server_status = AsyncMock(return_value=status)
    svc.get_library_items = AsyncMock(return_value={"items": [], "total": 0})
    svc.search_media = AsyncMock(return_value=[])
    svc.get_media_info = AsyncMock(return_value={"title": "x"})
    svc.get_recently_added = AsyncMock(return_value=[])
    svc.update_media_metadata = AsyncMock(return_value=True)
    svc.list_users = AsyncMock(return_value=[])
    svc.get_user = AsyncMock(return_value={"id": "u1", "username": "u"})
    svc.create_user = AsyncMock(return_value={"id": "u2"})
    svc.update_user = AsyncMock(return_value={"id": "u1"})
    svc.delete_user = AsyncMock(return_value=True)
    svc.update_user_permissions = AsyncMock(return_value=True)
    svc.get_sessions = AsyncMock(return_value=[])
    svc.get_clients = AsyncMock(
        return_value=[{"name": "c1", "machineIdentifier": "client123", "id": "client123"}]
    )
    svc.control_playback = AsyncMock(return_value=True)
    svc._run_in_executor = AsyncMock(
        side_effect=lambda fn, *a, **k: fn(*a, **k) if callable(fn) else None
    )
    svc._get_media_type = MagicMock(return_value="movie")
    svc._select_client_for_media = MagicMock(
        return_value={"name": "c1", "machineIdentifier": "client123"}
    )
    svc.get_transcode_settings = AsyncMock(return_value={})
    svc.update_transcode_settings = AsyncMock(return_value=True)
    svc.get_transcoding_status = AsyncMock(return_value={})
    svc.get_bandwidth_usage = AsyncMock(return_value={})
    svc.set_stream_quality = AsyncMock(return_value=True)
    svc.get_throttling_status = AsyncMock(return_value={})
    svc.set_throttling = AsyncMock(return_value=True)
    svc.list_quality_profiles = AsyncMock(return_value=[])
    svc.create_quality_profile = AsyncMock(return_value=True)
    svc.delete_quality_profile = AsyncMock(return_value=True)
    svc.scan_library = AsyncMock(return_value={"scan_successful": True})
    svc.refresh_library_metadata = AsyncMock(return_value=True)
    svc.empty_trash = AsyncMock(return_value=True)
    svc.add_library = AsyncMock(return_value=True)
    svc.update_library = AsyncMock(return_value=True)
    svc.delete_library = AsyncMock(return_value=True)
    svc.optimize_library = AsyncMock(return_value=True)
    svc.add_library_location = AsyncMock(return_value=True)
    svc.remove_library_location = AsyncMock(return_value=True)
    svc.clean_bundles = AsyncMock(return_value=True)
    svc.organize_library = AsyncMock(return_value=True)
    svc.analyze_library = AsyncMock(return_value={})
    svc.refresh_metadata = AsyncMock(return_value=True)
    svc.get_audio_streams = AsyncMock(return_value=[])
    svc.set_audio_stream = AsyncMock(return_value=True)
    svc.handover_media = AsyncMock(return_value=True)

    pl = _mock_playlist_obj()
    server = MagicMock()
    server.playlists = AsyncMock(return_value=[pl])
    server.playlist = AsyncMock(return_value=pl)
    server.lookupItem = AsyncMock(return_value=MagicMock())
    server.createPlaylist = AsyncMock(return_value=pl)
    svc.server = server

    return svc

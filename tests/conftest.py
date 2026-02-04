"""Pytest configuration and fixtures for PlexMCP tests."""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_plex_server():
    """Mock PlexServer for testing."""
    mock_server = Mock()
    mock_server.friendlyName = "Test Plex Server"
    mock_server.version = "1.32.0.123"
    mock_server.platform = "Windows"
    mock_server.myPlexUsername = "testuser"
    mock_server.updated_at = Mock()
    mock_server.updated_at.timestamp = Mock(return_value=1234567890.0)

    # Mock library sections
    mock_section = Mock()
    mock_section.key = "1"
    mock_section.title = "Movies"
    mock_section.type = "movie"
    mock_section.agent = "com.plexapp.agents.imdb"
    mock_section.scanner = "Plex Movie Scanner"
    mock_section.language = "en"
    mock_section.updatedAt = Mock()
    mock_section.updatedAt.timestamp = Mock(return_value=1234567890.0)
    mock_section.addedAt = Mock()
    mock_section.addedAt.timestamp = Mock(return_value=1234567890.0)
    mock_section.scannedAt = Mock()
    mock_section.scannedAt.timestamp = Mock(return_value=1234567890.0)
    mock_section.totalSize = 100

    mock_library = Mock()
    mock_library.sections = Mock(return_value=[mock_section])
    mock_server.library = mock_library

    # Mock sessions
    mock_server.sessions = Mock(return_value=[])

    return mock_server


@pytest.fixture
def plex_service(request, mock_plex_service):
    """
    PlexService fixture that prefers real server when available, falls back to mocks.

    This fixture checks if a real Plex server is available. If so, it returns
    the real service. Otherwise, it returns the mocked service.

    Tests using this fixture will automatically use the real server if PLEX_URL
    and PLEX_TOKEN are set, otherwise they will use mocks.
    """
    # Check if real server is available
    plex_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL")
    plex_token = os.getenv("PLEX_TOKEN")

    if plex_url and plex_token:
        try:
            # Try to get real service (may skip if not available)
            real_service = request.getfixturevalue("real_plex_service")
            return real_service
        except Exception:
            # Fall back to mock if real service not available or fails
            # This catches pytest.skip exceptions and other errors
            pass

    return mock_plex_service


@pytest.fixture
def mock_plex_service(mock_plex_server, mock_library_data):
    """Mock PlexService for testing portmanteau tools."""
    from unittest.mock import AsyncMock

    from plex_mcp.services.plex_service import PlexService

    with patch("plex_mcp.services.plex_service.PlexServer") as mock_plex_server_class:
        mock_plex_server_class.return_value = mock_plex_server

        service = PlexService(base_url="http://localhost:32400", token="test_token")
        service.server = mock_plex_server
        service._initialized = True

        # Mock async methods for library operations
        service.get_libraries = AsyncMock(return_value=[mock_library_data])
        service.get_library = AsyncMock(return_value=mock_library_data)
        service.scan_library = AsyncMock(return_value={"scan_successful": True})
        service.refresh_library_metadata = AsyncMock(return_value=True)
        service.optimize_library = AsyncMock(return_value=True)
        service.empty_trash = AsyncMock(return_value=True)

        # Mock async methods for media operations
        service.search_media = AsyncMock(return_value=[])
        service.get_media_details = AsyncMock(return_value={})
        service.get_recently_added = AsyncMock(return_value=[])
        service.update_media_metadata = AsyncMock(return_value=True)
        service.browse_library = AsyncMock(return_value=[])
        # Mock get_library_items to return a list with a mock item that has dict() method
        mock_item = Mock()
        mock_item.dict = Mock(return_value={"id": "1", "title": "Test Item"})
        service.get_library_items = AsyncMock(return_value=[mock_item])

        # Mock async methods for user operations
        service.list_users = AsyncMock(return_value=[mock_user_data])
        service.get_user = AsyncMock(return_value=mock_user_data)
        service.create_user = AsyncMock(return_value=mock_user_data)
        service.update_user = AsyncMock(return_value=mock_user_data)
        service.delete_user = AsyncMock(return_value=True)
        service.update_user_permissions = AsyncMock(return_value=mock_user_data)

        # Mock async methods for playlist operations
        service.list_playlists = AsyncMock(return_value=[mock_playlist_data])
        service.get_playlist = AsyncMock(return_value=mock_playlist_data)
        service.create_playlist = AsyncMock(return_value=mock_playlist_data)
        service.update_playlist = AsyncMock(return_value=mock_playlist_data)
        service.delete_playlist = AsyncMock(return_value=True)
        service.add_to_playlist = AsyncMock(return_value=mock_playlist_data)
        service.remove_from_playlist = AsyncMock(return_value=mock_playlist_data)
        service.get_playlist_analytics = AsyncMock(return_value={})

        # Mock async methods for streaming operations
        service.get_sessions = AsyncMock(return_value=[mock_session_data])
        service.get_clients = AsyncMock(return_value=[{"id": "client123", "name": "Test Client"}])
        service.list_sessions = AsyncMock(return_value=[mock_session_data])
        service.list_clients = AsyncMock(return_value=[{"id": "client123", "name": "Test Client"}])
        service.play_media = AsyncMock(return_value=True)
        service.pause_playback = AsyncMock(return_value=True)
        service.stop_playback = AsyncMock(return_value=True)
        service.seek_playback = AsyncMock(return_value=True)
        service.skip_next = AsyncMock(return_value=True)
        service.skip_previous = AsyncMock(return_value=True)
        service.control_playback = AsyncMock(return_value=True)
        # Mock set_volume specifically (it uses control_playback with volume parameter)
        service.control_playback = AsyncMock(return_value=True)

        # Mock async methods for server operations
        service.get_server_status = AsyncMock(
            return_value={"name": "Test Server", "version": "1.0.0"}
        )
        service.get_server_info = AsyncMock(
            return_value={"name": "Test Server", "version": "1.0.0"}
        )
        service.get_server_health = AsyncMock(return_value={"status": "healthy"})
        service.list_libraries = AsyncMock(return_value=[mock_library_data])

        # Mock server.playlists() for playlist operations
        from datetime import datetime

        mock_playlist_obj = Mock()
        mock_playlist_obj.title = "Test Playlist"
        mock_playlist_obj.key = "playlist123"
        mock_playlist_obj.ratingKey = "playlist123"
        mock_playlist_obj.type = "playlist"
        mock_playlist_obj.playlistType = "video"
        mock_playlist_obj.summary = "Test summary"
        mock_playlist_obj.duration = 3600
        mock_playlist_obj.items = Mock(return_value=[])
        mock_playlist_obj.smart = False
        mock_playlist_obj.addedAt = Mock()
        mock_playlist_obj.addedAt.timestamp = Mock(return_value=datetime.now().timestamp())
        mock_playlist_obj.updatedAt = Mock()
        mock_playlist_obj.updatedAt.timestamp = Mock(return_value=datetime.now().timestamp())
        mock_playlist_obj.username = "testuser"
        service.server.playlists = AsyncMock(return_value=[mock_playlist_obj])
        service.server.playlist = AsyncMock(return_value=mock_playlist_obj)
        service.server.lookupItem = AsyncMock(return_value=Mock())
        service.server.createPlaylist = AsyncMock(return_value=mock_playlist_obj)
        service.server.deletePlaylist = AsyncMock(return_value=True)
        # Mock playlist methods
        mock_playlist_obj.delete = AsyncMock(return_value=None)
        mock_playlist_obj.addItems = AsyncMock(return_value=None)
        mock_playlist_obj.reload = Mock(return_value=None)

        # Mock connect method
        service.connect = AsyncMock(return_value=None)

        # Mock async methods for metadata operations
        service.refresh_metadata = AsyncMock(return_value=True)
        service.fix_media_match = AsyncMock(return_value=True)

        # Mock async methods for performance operations
        service.get_transcode_settings = AsyncMock(return_value={})
        service.get_transcoding_status = AsyncMock(return_value={})
        service.get_bandwidth_usage = AsyncMock(return_value={})

        # Mock async methods for search operations
        service.advanced_search = AsyncMock(return_value=[])
        service.get_search_suggestions = AsyncMock(return_value=[])

        # Mock async methods for collections operations
        service.list_collections = AsyncMock(return_value=[])
        service.get_collection = AsyncMock(return_value={})
        service.create_collection = AsyncMock(return_value={})
        service.update_collection = AsyncMock(return_value={})
        service.delete_collection = AsyncMock(return_value=True)

        yield service


@pytest.fixture
def mock_plex_api(mock_plex_server):
    """Mock plexapi for testing."""
    with patch("plex_mcp.services.plex_service.PlexServer") as mock_plex_server_class:
        mock_plex_server_class.return_value = mock_plex_server
        yield mock_plex_server


@pytest.fixture
def sample_plex_config():
    """Sample Plex configuration for testing."""
    return {"server_url": "http://localhost:32400", "plex_token": "test_token_123", "timeout": 30}


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for consistent testing."""
    env_vars = {
        "PLEX_URL": "http://localhost:32400",
        "PLEX_TOKEN": "test_token_123",
        "PYTHONPATH": "src",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def mock_media_item():
    """Mock media item for testing."""
    return {
        "key": "12345",
        "title": "Test Movie",
        "type": "movie",
        "year": 2020,
        "summary": "A test movie",
        "rating": 8.5,
        "thumb": "http://localhost:32400/thumb.jpg",
        "duration": 7200000,
        "added_at": 1234567890.0,
    }


@pytest.fixture
def mock_library_data():
    """Mock library data for testing."""
    return {
        "id": "1",
        "title": "Movies",
        "type": "movie",
        "agent": "com.plexapp.agents.imdb",
        "scanner": "Plex Movie Scanner",
        "language": "en",
        "updated_at": 1234567890.0,
        "created_at": 1234567890.0,
        "scanned_at": 1234567890.0,
        "count": 100,
    }


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "id": "user123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "restricted": False,
    }


@pytest.fixture
def mock_playlist_data():
    """Mock playlist data for testing."""
    return {
        "id": "playlist123",
        "title": "My Playlist",
        "description": "A test playlist",
        "items": ["12345", "67890"],
    }


@pytest.fixture
def mock_session_data():
    """Mock session data for testing."""
    return {
        "id": "session123",
        "client": "Test Client",
        "media": {
            "title": "Test Movie",
            "key": "12345",
        },
        "state": "playing",
    }


# ============================================================================
# Fixture Database Support (Minimal Plex Database)
# ============================================================================


@pytest.fixture(scope="session")
def plex_fixture_db():
    """
    Minimal Plex SQLite database fixture for testing.

    Creates a minimal Plex database with:
    - 1 library section (Movies)
    - 1 test movie
    - 1 test video file reference

    Returns path to database file.
    """
    from tests.fixtures import (  # noqa: F401
        DB_PATH,
        create_library_structure,
        create_test_database,
        create_test_video,
    )

    # Ensure fixtures exist
    if not DB_PATH.exists():
        # Create test video first
        create_test_video()
        # Create database
        create_test_database()
        # Create library structure
        create_library_structure()

    return DB_PATH


@pytest.fixture(scope="session")
def plex_fixture_video():
    """
    Minimal test video file fixture.

    Returns path to test video file (5 seconds, < 1MB).
    """
    from tests.fixtures import MEDIA_DIR, create_test_video  # noqa: F401

    video_path = MEDIA_DIR / "test_video.mp4"

    if not video_path.exists():
        create_test_video()

    return video_path


@pytest.fixture
def plex_fixture_service(plex_fixture_db, plex_fixture_video):
    """
    PlexService configured to use fixture database.

    This fixture creates a PlexService instance that can work with
    the minimal test database. Note: This requires PlexAPI to support
    direct database access, which may not be fully supported.

    For now, this is a placeholder for future implementation.
    """

    # Note: PlexAPI doesn't directly support SQLite database access
    # This would require custom implementation or using Plex's HTTP API
    # with a test server instance

    # For now, return None to indicate this needs real server
    pytest.skip("Fixture database service requires custom PlexAPI implementation")

    # Future implementation would:
    # 1. Start a minimal Plex server instance pointing to fixture library
    # 2. Or implement direct database access layer
    # 3. Or use PlexAPI with fixture paths


# ============================================================================
# Integration Test Fixtures (Real Plex Server)
# ============================================================================


def _check_plex_available() -> tuple[bool, str | None]:
    """
    Check if a real Plex server is available for integration testing.

    Returns:
        Tuple of (is_available, reason_if_not_available)
    """
    plex_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL")
    plex_token = os.getenv("PLEX_TOKEN")

    if not plex_url:
        return False, "PLEX_URL or PLEX_SERVER_URL environment variable not set"

    if not plex_token:
        return False, "PLEX_TOKEN environment variable not set"

    # Basic check: if env vars are set, assume server might be available
    # Actual connection will be tested in the real_plex_service fixture
    # This allows tests to be marked but skipped if connection fails
    return True, None


@pytest.fixture(scope="session")
def plex_available():
    """
    Pytest fixture that skips integration tests if Plex server is not available.

    Usage:
        @pytest.mark.integration
        def test_something(plex_available):
            # This test will be skipped if Plex is not available
            ...
    """
    is_available, reason = _check_plex_available()
    if not is_available:
        pytest.skip(f"Plex server not available for integration testing: {reason}")
    return True


@pytest.fixture
def real_plex_service(plex_available):
    """
    Real PlexService connected to actual Plex server.

    Only available when Plex server is accessible and credentials are valid.
    Connection is tested when service is first used in tests.
    """
    from plex_mcp.services.plex_service import PlexService

    plex_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    plex_token = os.getenv("PLEX_TOKEN")

    if not plex_token:
        pytest.skip("PLEX_TOKEN not set")

    service = PlexService(base_url=plex_url, token=plex_token)
    return service


@pytest.fixture
async def test_library_id(real_plex_service, plex_available):
    """
    Get the first available library ID for integration testing.

    Returns None if no libraries are available.
    """
    # Connect and get libraries
    try:
        await real_plex_service.connect()
        libraries = await real_plex_service.list_libraries()
        if libraries and len(libraries) > 0:
            library_id = libraries[0].get("id") or str(libraries[0].get("key", ""))
            if library_id:
                return library_id
    except Exception as e:
        pytest.skip(f"Failed to connect to Plex server: {str(e)}")

    pytest.skip("No libraries available on Plex server for testing")

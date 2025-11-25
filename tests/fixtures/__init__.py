"""PlexMCP test fixtures."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent
MEDIA_DIR = FIXTURES_DIR / "media"
LIBRARY_DIR = FIXTURES_DIR / "library"
DB_PATH = FIXTURES_DIR / "plex_test.db"

# Import creation functions for use in conftest
from .create_fixtures import create_test_database, create_test_video, create_library_structure  # noqa: E402

__all__ = [
    "FIXTURES_DIR",
    "MEDIA_DIR",
    "LIBRARY_DIR",
    "DB_PATH",
    "create_test_database",
    "create_test_video",
    "create_library_structure",
]


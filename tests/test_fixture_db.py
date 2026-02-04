"""
Tests using fixture database (minimal Plex SQLite database).

These tests use a minimal Plex database structure without requiring
a full Plex server. Useful for testing database queries and data structures.
"""

import sqlite3

import pytest


@pytest.mark.fixture_db
class TestFixtureDatabase:
    """Tests using fixture database."""

    def test_fixture_db_exists(self, plex_fixture_db):
        """Test that fixture database exists and is valid SQLite."""
        assert plex_fixture_db.exists(), "Fixture database should exist"
        assert plex_fixture_db.suffix == ".db", "Should be SQLite database"

        # Verify it's a valid SQLite database
        conn = sqlite3.connect(str(plex_fixture_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "library_sections" in tables, "Should have library_sections table"
        assert "metadata_items" in tables, "Should have metadata_items table"
        assert "media_items" in tables, "Should have media_items table"
        assert "media_parts" in tables, "Should have media_parts table"

    def test_fixture_db_has_test_data(self, plex_fixture_db):
        """Test that fixture database contains test data."""
        conn = sqlite3.connect(str(plex_fixture_db))
        cursor = conn.cursor()

        # Check library section
        cursor.execute("SELECT COUNT(*) FROM library_sections")
        section_count = cursor.fetchone()[0]
        assert section_count > 0, "Should have at least one library section"

        # Check metadata items
        cursor.execute("SELECT COUNT(*) FROM metadata_items")
        item_count = cursor.fetchone()[0]
        assert item_count > 0, "Should have at least one metadata item"

        # Check media items
        cursor.execute("SELECT COUNT(*) FROM media_items")
        media_count = cursor.fetchone()[0]
        assert media_count > 0, "Should have at least one media item"

        # Check media parts
        cursor.execute("SELECT COUNT(*) FROM media_parts")
        parts_count = cursor.fetchone()[0]
        assert parts_count > 0, "Should have at least one media part"

        conn.close()

    def test_fixture_db_library_structure(self, plex_fixture_db):
        """Test library section structure in fixture database."""
        conn = sqlite3.connect(str(plex_fixture_db))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, section_type, language, agent, scanner
            FROM library_sections
            LIMIT 1
        """)
        section = cursor.fetchone()
        conn.close()

        assert section is not None, "Should have a library section"
        assert section[1] == "Test Movies", "Should be named 'Test Movies'"
        assert section[2] == 1, "Should be movie type (1)"

    def test_fixture_db_metadata_item(self, plex_fixture_db):
        """Test metadata item structure in fixture database."""
        conn = sqlite3.connect(str(plex_fixture_db))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, library_section_id, title, year, rating
            FROM metadata_items
            WHERE metadata_type = 1
            LIMIT 1
        """)
        item = cursor.fetchone()
        conn.close()

        assert item is not None, "Should have a metadata item"
        assert item[2] == "Test Movie", "Should be titled 'Test Movie'"
        assert item[3] == 2024, "Should be from year 2024"

    def test_fixture_video_exists(self, plex_fixture_video):
        """Test that fixture video file exists."""
        assert plex_fixture_video.exists(), "Fixture video should exist"
        assert plex_fixture_video.suffix == ".mp4", "Should be MP4 file"

        # Check file size (should be small, < 1MB)
        size = plex_fixture_video.stat().st_size
        assert size > 0, "Video file should not be empty"
        assert size < 1024 * 1024, "Video should be < 1MB (minimal test file)"

    def test_fixture_library_structure(self, plex_fixture_db):
        """Test that library directory structure matches database."""
        from tests.fixtures import LIBRARY_DIR

        # Check that library directory exists
        assert LIBRARY_DIR.exists(), "Library directory should exist"

        # Check for movie directory
        movie_dir = LIBRARY_DIR / "Movies" / "Test Movie (2024)"
        assert movie_dir.exists(), "Test movie directory should exist"

        # Check for video file in library
        video_file = movie_dir / "Test Movie (2024).mp4"
        assert video_file.exists(), "Test video should be in library structure"

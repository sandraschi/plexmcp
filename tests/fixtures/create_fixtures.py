"""
Script to create minimal Plex test fixtures.

Creates:
1. Minimal test video file (5 seconds, < 1MB)
2. Minimal Plex SQLite database with test data
3. Test library directory structure
"""

import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

# Base paths
FIXTURES_DIR = Path(__file__).parent
MEDIA_DIR = FIXTURES_DIR / "media"
LIBRARY_DIR = FIXTURES_DIR / "library"
DB_PATH = FIXTURES_DIR / "plex_test.db"


def create_test_video():
    """Create a minimal test video file using FFmpeg."""
    video_path = MEDIA_DIR / "test_video.mp4"
    MEDIA_DIR.mkdir(exist_ok=True)

    if video_path.exists():
        print(f"Test video already exists: {video_path}")
        return video_path

    # Try to create minimal video with FFmpeg
    import subprocess

    try:
        # Create 5-second test pattern video (320x240, very small)
        cmd = [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=5:size=320x240:rate=1",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "28",  # Lower quality = smaller file
            "-t",
            "5",
            "-y",  # Overwrite
            str(video_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Created test video: {video_path} ({video_path.stat().st_size} bytes)")
            return video_path
        else:
            print(f"FFmpeg failed: {result.stderr}")
            return None
    except FileNotFoundError:
        print("FFmpeg not found. Creating placeholder file instead.")
        # Create a minimal valid MP4 header (262 bytes minimum)
        # This is a minimal MP4 file that Plex can recognize
        minimal_mp4 = (
            b"\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00"
            b"mp41isom\x00\x00\x02\x00mdat\x00\x00\x00\x08"
            b"\x00\x00\x00\x00" * 50  # Minimal data
        )
        video_path.write_bytes(minimal_mp4)
        print(f"Created placeholder video: {video_path} ({len(minimal_mp4)} bytes)")
        return video_path


def create_test_database():
    """Create minimal Plex SQLite database with test data."""
    if DB_PATH.exists():
        DB_PATH.unlink()  # Remove existing

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create minimal schema based on Plex database structure
    # These are the essential tables for basic operations

    # Library sections (libraries)
    cursor.execute("""
        CREATE TABLE library_sections (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            section_type INTEGER NOT NULL,
            language TEXT,
            agent TEXT,
            scanner TEXT,
            created_at DATETIME,
            updated_at DATETIME
        )
    """)

    # Metadata items (movies, shows, etc.)
    cursor.execute("""
        CREATE TABLE metadata_items (
            id INTEGER PRIMARY KEY,
            library_section_id INTEGER,
            parent_id INTEGER,
            metadata_type INTEGER NOT NULL,
            guid TEXT,
            media_item_count INTEGER DEFAULT 0,
            title TEXT NOT NULL,
            title_sort TEXT,
            original_title TEXT,
            summary TEXT,
            rating REAL,
            year INTEGER,
            added_at DATETIME,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (library_section_id) REFERENCES library_sections(id)
        )
    """)

    # Media items (files)
    cursor.execute("""
        CREATE TABLE media_items (
            id INTEGER PRIMARY KEY,
            library_section_id INTEGER,
            metadata_item_id INTEGER NOT NULL,
            width INTEGER,
            height INTEGER,
            duration INTEGER,
            bitrate INTEGER,
            container TEXT,
            video_codec TEXT,
            audio_codec TEXT,
            FOREIGN KEY (metadata_item_id) REFERENCES metadata_items(id),
            FOREIGN KEY (library_section_id) REFERENCES library_sections(id)
        )
    """)

    # Media parts (file paths)
    cursor.execute("""
        CREATE TABLE media_parts (
            id INTEGER PRIMARY KEY,
            media_item_id INTEGER NOT NULL,
            file TEXT NOT NULL,
            size INTEGER,
            duration INTEGER,
            FOREIGN KEY (media_item_id) REFERENCES media_items(id)
        )
    """)

    # Insert test data
    now = datetime.now(UTC).isoformat()

    # Test library section
    cursor.execute(
        """
        INSERT INTO library_sections (id, name, section_type, language, agent, scanner, created_at, updated_at)
        VALUES (1, 'Test Movies', 1, 'en', 'com.plexapp.agents.imdb', 'Plex Movie Scanner', ?, ?)
    """,
        (now, now),
    )

    # Test movie
    cursor.execute(
        """
        INSERT INTO metadata_items (
            id, library_section_id, metadata_type, title, title_sort, year,
            summary, rating, added_at, created_at, updated_at
        )
        VALUES (1, 1, 1, 'Test Movie', 'Test Movie', 2024, 'A test movie for PlexMCP testing', 7.5, ?, ?, ?)
    """,
        (now, now, now),
    )

    # Test media item
    relative_path = "library/Movies/Test Movie (2024)/Test Movie (2024).mp4"

    cursor.execute("""
        INSERT INTO media_items (
            id, library_section_id, metadata_item_id, width, height, duration,
            container, video_codec, audio_codec
        )
        VALUES (1, 1, 1, 320, 240, 5000, 'mp4', 'h264', 'aac')
    """)

    # Test media part
    cursor.execute(
        """
        INSERT INTO media_parts (id, media_item_id, file, size, duration)
        VALUES (1, 1, ?, 1000000, 5000)
    """,
        (relative_path,),
    )

    conn.commit()
    conn.close()

    print(f"Created test database: {DB_PATH}")
    return DB_PATH


def create_library_structure():
    """Create test library directory structure."""
    library_path = LIBRARY_DIR / "Movies" / "Test Movie (2024)"
    library_path.mkdir(parents=True, exist_ok=True)

    # Copy test video to library structure
    source_video = MEDIA_DIR / "test_video.mp4"
    dest_video = library_path / "Test Movie (2024).mp4"

    if source_video.exists() and not dest_video.exists():
        shutil.copy2(source_video, dest_video)
        print(f"Created library structure: {library_path}")

    return library_path


def main():
    """Create all test fixtures."""
    print("Creating PlexMCP test fixtures...")
    print("-" * 50)

    # Create directories
    FIXTURES_DIR.mkdir(exist_ok=True)
    MEDIA_DIR.mkdir(exist_ok=True)
    LIBRARY_DIR.mkdir(exist_ok=True)

    # Create fixtures
    video_path = create_test_video()
    db_path = create_test_database()
    library_path = create_library_structure()

    print("-" * 50)
    print("Fixtures created successfully!")
    print(f"  Video: {video_path}")
    print(f"  Database: {db_path}")
    print(f"  Library: {library_path}")

    # Calculate total size
    total_size = sum(f.stat().st_size for f in FIXTURES_DIR.rglob("*") if f.is_file())
    print(f"  Total size: {total_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()

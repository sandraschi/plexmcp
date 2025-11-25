# PlexMCP Test Fixtures

## Overview

This directory contains minimal test fixtures for PlexMCP testing:
- **Minimal Plex database** (SQLite format)
- **Small test video file** (few seconds, minimal size)
- **Test library structure** (mimics Plex library organization)

## Structure

```
fixtures/
├── README.md                    # This file
├── plex_test.db                 # Minimal Plex SQLite database
├── media/                       # Test media files
│   └── test_video.mp4          # Minimal test video (5-10 seconds)
└── library/                     # Test library structure
    └── Movies/
        └── Test Movie (2024)/
            └── Test Movie (2024).mp4
```

## Usage

The fixtures are automatically set up by pytest fixtures in `conftest.py`:

```python
@pytest.fixture
def plex_fixture_db():
    """Fixture database for testing."""
    # Returns path to test database
```

## Creating Fixtures

### Test Video

The test video is a minimal MP4 file (~5-10 seconds, < 1MB) created using FFmpeg:

```bash
ffmpeg -f lavfi -i testsrc=duration=5:size=320x240:rate=1 -c:v libx264 -t 5 tests/fixtures/media/test_video.mp4
```

### Test Database

The test database is created programmatically with minimal schema:

- `metadata_items` - Main media items table
- `library_sections` - Library sections
- `media_items` - Media file references
- `media_parts` - File parts

## Maintenance

- Keep fixtures minimal (< 10MB total)
- Update schema if Plex changes database structure
- Test video should be valid MP4 that Plex can process


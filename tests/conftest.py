"""Pytest configuration: logging guard, mock PlexService, optional real Plex + MCP HTTP."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

os.environ.setdefault("PLEXMCP_ALLOW_LOGGING", "1")
os.environ.setdefault("APP_SETTINGS_MODULE", "webapp.backend.app.config.Settings")  # Ensure settings load for tests

from fixtures.mock_plex_service import build_mock_plex_service
from fixtures.mock_rag_engine import patch_rag_engine


def _write_minimal_plex_sqlite(db_path: Path) -> None:
    """Create a tiny Plex-shaped SQLite DB for fixture_db tests."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(
            """
            CREATE TABLE library_sections (
                id INTEGER PRIMARY KEY,
                name TEXT,
                section_type INTEGER,
                language TEXT,
                agent TEXT,
                scanner TEXT
            );
            INSERT INTO library_sections VALUES (1, 'Test Movies', 1, 'en', 'agent', 'scanner');

            CREATE TABLE metadata_items (
                id INTEGER PRIMARY KEY,
                library_section_id INTEGER,
                title TEXT,
                year INTEGER,
                rating REAL,
                metadata_type INTEGER
            );
            INSERT INTO metadata_items VALUES (1, 1, 'Test Movie', 2024, 8.0, 1);

            CREATE TABLE media_items (id INTEGER PRIMARY KEY);
            INSERT INTO media_items VALUES (1);

            CREATE TABLE media_parts (id INTEGER PRIMARY KEY);
            INSERT INTO media_parts VALUES (1);
            """
        )
        conn.commit()
    finally:
        conn.close()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "mcp_http: needs webapp backend reachable at MCP_TEST_BASE_URL (default :10740)")
    config.addinivalue_line("markers", "integration: real Plex server (skipped in CI)")


@pytest.fixture
def mock_plex_service() -> Any:
    """Patched `PlexService` shape for portmanteau unit tests (no network)."""
    return build_mock_plex_service()


@pytest.fixture(autouse=True)
def mock_rag_engine():
    """Automatically patch RAG dependencies for all tests unless disabled."""
    patches = patch_rag_engine()
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.fixture
def plex_service(mock_plex_service: Any) -> Any:
    """Alias used by streaming tests."""
    return mock_plex_service


@pytest.fixture
def plex_available() -> None:
    """Skip real-Plex tests when CI or credentials missing."""
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        pytest.skip("Real Plex integration tests are disabled in GitHub Actions (mock-only CI).")
    token = (os.getenv("PLEX_TOKEN") or "").strip()
    url = (os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL") or "").strip()
    if not token or not url:
        pytest.skip("PLEX_TOKEN and PLEX_URL / PLEX_SERVER_URL not set — skipping real Plex tests.")


@pytest.fixture
def test_library_id() -> str:
    """Library section id for integration tests (override with PLEX_TEST_LIBRARY_ID)."""
    return (os.getenv("PLEX_TEST_LIBRARY_ID") or "1").strip()


@pytest_asyncio.fixture
async def real_plex_service(plex_available: None) -> AsyncGenerator[Any, None]:
    """Connected `PlexService` when credentials and network allow."""
    from plex_mcp.services.plex_service import PlexService

    base = (os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL") or "http://localhost:32400").strip()
    token = (os.getenv("PLEX_TOKEN") or "").strip()
    svc = PlexService(base_url=base, token=token)
    try:
        await svc.connect()
    except Exception as e:
        pytest.skip(f"Plex connect failed: {e}")
    try:
        yield svc
    finally:
        pass


@pytest.fixture
def mcp_backend_url() -> str:
    """Base URL for FastAPI webapp (health + mounted /mcp)."""
    return (os.getenv("MCP_TEST_BASE_URL") or "http://127.0.0.1:10740").rstrip("/")


@pytest.fixture
def mcp_http_live(mcp_backend_url: str) -> str:
    """Skip unless backend responds on /health (local dev); always skip in GitHub Actions."""
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        pytest.skip("MCP HTTP live tests skipped in GitHub Actions.")
    try:
        import httpx

        r = httpx.get(f"{mcp_backend_url}/health", timeout=3.0)
        if r.status_code != 200:
            pytest.skip(f"Backend not healthy at {mcp_backend_url}: HTTP {r.status_code}")
    except Exception as e:
        pytest.skip(f"Backend not running at {mcp_backend_url}: {e}")
    return mcp_backend_url


@pytest.fixture
def plex_library_dir(tmp_path: Path) -> Path:
    """Minimal folder layout aligned with fixture DB sample titles."""
    root = tmp_path / "PlexLibrary"
    movie_dir = root / "Movies" / "Test Movie (2024)"
    movie_dir.mkdir(parents=True)
    vid = movie_dir / "Test Movie (2024).mp4"
    vid.write_bytes(b"\x00\x00\x00\x20ftypisom" + b"\x00" * 200)
    return root


@pytest.fixture
def plex_fixture_video(plex_library_dir: Path) -> Path:
    """Small MP4 path under the sample library tree."""
    return plex_library_dir / "Movies" / "Test Movie (2024)" / "Test Movie (2024).mp4"


@pytest.fixture
def plex_fixture_db(tmp_path: Path) -> Path:
    """SQLite file with library_sections / metadata_items / media_* rows."""
    db = tmp_path / "com.plexapp.plugins.library.db"
    _write_minimal_plex_sqlite(db)
    return db


@pytest.fixture
def webapp_app():
    """Returns the FastAPI app instance from webapp.backend.app.main."""
    from webapp.backend.app.main import app

    return app

"""Unit tests for PlexIngestor (RAG Service).

Verifies recursive traversal for shows/artists and correct document formatting.
"""

from unittest.mock import MagicMock

import pytest

from plex_mcp.services.rag_ingestor import PlexIngestor


@pytest.mark.asyncio
async def test_ingestor_recursive_show(mock_plex_service):
    """Verify that 'show' libraries trigger recursive episode extraction."""
    ingestor = PlexIngestor(mock_plex_service, db_path=":memory:")

    # Run implementation directly to avoid background threading issues in basic unit test
    count = await ingestor._extract_and_index_all_impl(enrich=False)

    # 1 Movie, 1 Show, 1 Artist + 1 Episode + 1 Album = 5 items total
    # (Actually: Movie 1, Mock Show, Mock Artist, Episode 1, Album 1)
    # The current mock returns:
    # eligible: lib 1 (movie), lib 2 (show), lib 3 (artist)
    # lib 1 items: [m1]
    # lib 2 items: [s1] + recursive ep_result [e1]
    # lib 3 items: [ar1] + recursive album_result [a1]
    # Total doc count should be 5.
    assert count == 5

    # Check that get_library_items was called with libtype="episode" for library 2
    mock_plex_service.get_library_items.assert_any_call(library_id="2", libtype="episode", limit=50000)
    mock_plex_service.get_library_items.assert_any_call(library_id="3", libtype="album", limit=50000)


@pytest.mark.asyncio
async def test_ingestor_content_formatting(mock_plex_service):
    """Verify that episode content includes grandparent context."""
    ingestor = PlexIngestor(mock_plex_service, db_path=":memory:")

    # Mock add_documents to capture the docs
    ingestor.vector_store.add_documents = MagicMock()

    await ingestor._extract_and_index_all_impl(enrich=False)

    # Extract docs from call
    docs = ingestor.vector_store.add_documents.call_args[0][0]

    # Find the episode doc
    ep_doc = next((d for d in docs if d["metadata"]["type"] == "episode"), None)
    assert ep_doc is not None
    assert "Show: Mock Show" in ep_doc["content"]
    assert "Season 1, Episode 1" in ep_doc["content"]

    # Find the album doc
    album_doc = next((d for d in docs if d["metadata"]["type"] == "album"), None)
    assert album_doc is not None
    assert "Artist: Mock Artist" in album_doc["content"]
    assert "Album: Album 1" in album_doc["content"]

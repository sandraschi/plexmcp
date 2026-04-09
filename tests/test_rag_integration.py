"""Live integration tests for RAG (Semantic Search).

Requires PLEX_TOKEN and PLEX_URL.
These tests verify real indexing into LanceDB and semantic retrieval.
"""

import pytest

from plex_mcp.services.rag_ingestor import PlexIngestor
from plex_mcp.tools.portmanteau.rag import plex_rag


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rag_sync_and_search_real(real_plex_service, tmp_path):
    """Perform a full sync and search against a real Plex server."""
    db_path = str(tmp_path / "lancedb_test")

    # Ensure RAG dependencies are actually present for integration test
    try:
        import lancedb
        import sentence_transformers
    except ImportError:
        pytest.skip("RAG dependencies (lancedb, sentence_transformers) not installed.")

    # 1. Initialize Ingestor with real service
    ingestor = PlexIngestor(real_plex_service, db_path=db_path)
    if not ingestor.is_available:
        pytest.skip("RAG engine not available on this system.")

    # 2. Extract and index (limit to a small set if possible, but our implementation scans all)
    # We'll just run it and hope for the best, or skip if it's too slow.
    await ingestor.extract_and_index_all(enrich=False)

    stats = ingestor.get_stats()
    assert stats["available"] is True
    assert stats["count"] >= 0  # Might be 0 if library is empty

    # 3. Perform a semantic search
    results = ingestor.semantic_search("movie", limit=1)
    if stats["count"] > 0:
        assert len(results) > 0
        assert "content" in results[0]
        assert "score" in results[0]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rag_tool_real(real_plex_service, plex_available):
    """Test the plex_rag tool against a real server."""
    from unittest.mock import patch

    with patch("plex_mcp.tools.portmanteau.rag._get_plex_service", return_value=real_plex_service):
        result = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(operation="status")
        assert result["success"] is True
        assert "count" in result["data"]

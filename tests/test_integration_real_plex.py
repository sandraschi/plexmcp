"""
Integration tests against real Plex Media Server.

These tests require:
- PLEX_URL or PLEX_SERVER_URL environment variable
- PLEX_TOKEN environment variable
- Accessible Plex Media Server

Tests are automatically skipped if server is not available.
"""

from unittest.mock import patch

import pytest

from plex_mcp.tools.portmanteau.library import plex_library
from plex_mcp.tools.portmanteau.media import plex_media
from plex_mcp.tools.portmanteau.server import plex_server


@pytest.mark.integration
@pytest.mark.asyncio
class TestRealPlexIntegration:
    """Integration tests against real Plex server."""

    async def test_list_libraries_real(self, real_plex_service, plex_available):
        """Test listing libraries against real Plex server."""
        # Connect to real server
        try:
            await real_plex_service.connect()
        except Exception as e:
            pytest.skip(f"Failed to connect to Plex server: {str(e)}")

        # Patch _get_plex_service to use our real service instance
        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service", return_value=real_plex_service
        ):
            result = await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                operation="list"
            )

            assert result["success"] is True
            assert result["operation"] == "list"
            assert "data" in result
            assert isinstance(result["data"], list)
            # Real server should have at least one library
            assert len(result["data"]) > 0, "Real Plex server should have at least one library"

            # Verify library structure
            library = result["data"][0]
            assert "id" in library or "key" in library
            assert "title" in library
            assert "type" in library

    async def test_get_library_real(self, real_plex_service, plex_available, test_library_id):
        """Test getting library details from real Plex server."""
        # Ensure connected
        if not real_plex_service._initialized:
            await real_plex_service.connect()

        with patch(
            "plex_mcp.tools.portmanteau.library._get_plex_service", return_value=real_plex_service
        ):
            result = await (plex_library.fn if hasattr(plex_library, "fn") else plex_library)(
                operation="get", library_id=test_library_id
            )

            assert result["success"] is True
            assert result["operation"] == "get"
            assert "data" in result
            library = result["data"]
            assert library.get("id") == test_library_id or library.get("key") == test_library_id

    async def test_server_status_real(self, real_plex_service, plex_available):
        """Test getting server status from real Plex server."""
        # Ensure connected
        if not real_plex_service._initialized:
            await real_plex_service.connect()

        with patch(
            "plex_mcp.tools.portmanteau.server._get_plex_service", return_value=real_plex_service
        ):
            result = await (plex_server.fn if hasattr(plex_server, "fn") else plex_server)(
                operation="status"
            )

            assert result["success"] is True
            assert result["operation"] == "status"
            assert "data" in result
            # Real server should have name and version
            status = result["data"]
            assert "name" in status or "friendlyName" in status

    async def test_browse_library_real(self, real_plex_service, plex_available, test_library_id):
        """Test browsing library contents from real Plex server."""
        # Ensure connected
        if not real_plex_service._initialized:
            await real_plex_service.connect()

        with patch(
            "plex_mcp.tools.portmanteau.media._get_plex_service", return_value=real_plex_service
        ):
            result = await (plex_media.fn if hasattr(plex_media, "fn") else plex_media)(
                operation="browse", library_id=test_library_id, limit=10
            )

            assert result["success"] is True
            assert result["operation"] == "browse"
            assert "data" in result
            assert isinstance(result["data"], list)
            # Note: Library might be empty, so we just check structure
            if len(result["data"]) > 0:
                item = result["data"][0]
                assert "id" in item or "key" in item or "title" in item

    async def test_search_media_real(self, real_plex_service, plex_available):
        """Test searching media on real Plex server."""
        # Ensure connected
        if not real_plex_service._initialized:
            await real_plex_service.connect()

        with patch(
            "plex_mcp.tools.portmanteau.media._get_plex_service", return_value=real_plex_service
        ):
            # Search for something common (empty string searches all)
            result = await (plex_media.fn if hasattr(plex_media, "fn") else plex_media)(
                operation="search", query="", limit=5
            )

            assert result["success"] is True
            assert result["operation"] == "search"
            assert "data" in result
            assert isinstance(result["data"], list)
            # Note: Results might be empty, so we just check structure

    async def test_subtitle_rag_real(self, real_plex_service, plex_available, test_library_id):
        """Test subtitle RAG sync and search on real Plex server."""
        from plex_mcp.tools.portmanteau.rag import plex_rag
        
        # Ensure connected
        if not real_plex_service._initialized:
            await real_plex_service.connect()

        with patch("plex_mcp.tools.portmanteau.rag._get_plex_service", return_value=real_plex_service):
            # 1. Browse for a media item that might have subtitles
            browse_res = await plex_media(operation="browse", library_id=test_library_id, limit=5)
            if not browse_res["success"] or not browse_res["data"]:
                pytest.skip("No media found in test library to index subtitles for.")
            
            media_id = browse_res["data"][0].get("id") or browse_res["data"][0].get("ratingKey")
            
            # 2. Try to sync subtitles for this item
            # Note: This might be slow and might return 'no subtitles found' which is a success case for the logic
            sync_res = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(
                operation="sync_subtitles", media_id=str(media_id)
            )
            
            assert sync_res["success"] is True
            assert sync_res["operation"] == "sync_subtitles"
            
            # 3. Search subtitles (even if sync added 0, the tool should run)
            search_res = await (plex_rag.fn if hasattr(plex_rag, "fn") else plex_rag)(
                operation="search_subtitles", query="hello", limit=5
            )
            
            assert search_res["success"] is True
            assert search_res["operation"] == "search_subtitles"
            assert "data" in search_res

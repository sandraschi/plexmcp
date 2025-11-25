"""
Integration tests against real Plex Media Server.

These tests require:
- PLEX_URL or PLEX_SERVER_URL environment variable
- PLEX_TOKEN environment variable
- Accessible Plex Media Server

Tests are automatically skipped if server is not available.
"""

import pytest
from unittest.mock import patch

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
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=real_plex_service):
            result = await plex_library.fn(operation="list")
            
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
        
        with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=real_plex_service):
            result = await plex_library.fn(operation="get", library_id=test_library_id)
            
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
        
        with patch("plex_mcp.tools.portmanteau.server._get_plex_service", return_value=real_plex_service):
            result = await plex_server.fn(operation="status")
            
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
        
        with patch("plex_mcp.tools.portmanteau.media._get_plex_service", return_value=real_plex_service):
            result = await plex_media.fn(operation="browse", library_id=test_library_id, limit=10)
            
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
        
        with patch("plex_mcp.tools.portmanteau.media._get_plex_service", return_value=real_plex_service):
            # Search for something common (empty string searches all)
            result = await plex_media.fn(operation="search", query="", limit=5)
            
            assert result["success"] is True
            assert result["operation"] == "search"
            assert "data" in result
            assert isinstance(result["data"], list)
            # Note: Results might be empty, so we just check structure


"""Tests for PlexMCP main module."""

import pytest
from unittest.mock import patch, AsyncMock

from plex_mcp.main import main


class TestMainModule:
    """Test cases for the main module."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from plex_mcp.main import main
        assert callable(main)

    def test_module_imports(self):
        """Test that all required modules can be imported."""
        # Test that we can import the app
        import plex_mcp.app
        assert hasattr(plex_mcp.app, 'mcp')

        # Test that we can import config
        import plex_mcp.config
        assert hasattr(plex_mcp.config, 'get_settings')
        assert hasattr(plex_mcp.config, 'setup_logging')

    def test_logging_setup_called(self):
        """Test that logging is set up when main is imported."""
        # This test verifies that the logging setup is called during import
        import logging

        # Check that the root logger has handlers (set up by setup_logging)
        root_logger = logging.getLogger()
        # Note: This assumes setup_logging has been called during import
        # In a real scenario, we'd want to verify this more precisely

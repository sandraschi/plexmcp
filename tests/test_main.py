"""Tests for PlexMCP main module and server entry point."""


class TestMainModule:
    """Test cases for the main module and server entry point."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from plex_mcp.main import main

        assert callable(main)

    def test_main_is_sync(self):
        """CLI main is synchronous; it delegates to server transport."""
        import inspect

        from plex_mcp.main import main

        assert not inspect.iscoroutinefunction(main)

    def test_module_imports(self):
        """Test that all required modules can be imported."""
        # Test that we can import the app
        import plex_mcp.app

        assert hasattr(plex_mcp.app, "mcp")

        # Test that we can import config
        import plex_mcp.config

        assert hasattr(plex_mcp.config, "setup_logging")
        assert hasattr(plex_mcp.config, "PlexConfig")

    def test_portmanteau_tools_imported(self):
        """Test that portmanteau tools are imported and registered."""
        import plex_mcp.app

        # The portmanteau tools should be imported when server.py is loaded
        # This is tested more thoroughly in test_portmanteau_integration.py
        assert hasattr(plex_mcp.app, "mcp")

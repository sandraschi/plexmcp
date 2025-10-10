"""Tests for PlexMCP configuration module."""

import os
import pytest
from unittest.mock import patch

from plex_mcp.config import PlexConfig, setup_logging


class TestPlexConfig:
    """Test cases for PlexConfig."""

    def test_valid_config(self):
        """Test configuration with valid values."""
        config = PlexConfig(
            server_url="http://localhost:32400",
            plex_token="test_token_123"
        )
        assert config.server_url == "http://localhost:32400"
        assert config.plex_token == "test_token_123"
        assert config.timeout == 30

    def test_server_url_normalization(self):
        """Test that server URL is normalized."""
        config = PlexConfig(
            server_url="localhost:32400",
            plex_token="test_token"
        )
        assert config.server_url == "http://localhost:32400"

    def test_server_url_with_trailing_slash(self):
        """Test that trailing slashes are removed."""
        config = PlexConfig(
            server_url="http://localhost:32400/",
            plex_token="test_token"
        )
        assert config.server_url == "http://localhost:32400"

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeout
        config = PlexConfig(server_url="http://localhost:32400", plex_token="test", timeout=60)
        assert config.timeout == 60

        # Minimum timeout
        config = PlexConfig(server_url="http://localhost:32400", plex_token="test", timeout=1)
        assert config.timeout == 5  # Should be clamped to minimum

        # Maximum timeout
        config = PlexConfig(server_url="http://localhost:32400", plex_token="test", timeout=400)
        assert config.timeout == 300  # Should be clamped to maximum

    def test_plex_token_required(self):
        """Test that plex_token is required."""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            PlexConfig(server_url="http://localhost:32400")

    def test_empty_plex_token(self):
        """Test that empty plex_token raises error."""
        with pytest.raises(ValueError, match="PLEX_TOKEN is required"):
            PlexConfig(server_url="http://localhost:32400", plex_token="")

    @patch.dict(os.environ, {
        'PLEX_URL': 'http://plex.example.com:32400',
        'PLEX_TOKEN': 'env_token_123'
    })
    def test_from_environment(self):
        """Test loading configuration from environment variables."""
        from plex_mcp.config import get_settings

        # This test assumes get_settings() loads from environment
        # Adjust based on actual implementation
        pass  # Placeholder for now


class TestLoggingSetup:
    """Test cases for logging setup."""

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        import logging

        # Reset any existing handlers
        logger = logging.getLogger()
        original_handlers = logger.handlers[:]
        logger.handlers.clear()

        try:
            setup_logging(level="INFO")

            # Check that handlers were added
            assert len(logger.handlers) > 0

            # Check that level was set
            assert logger.level == logging.INFO

        finally:
            # Restore original handlers
            logger.handlers[:] = original_handlers

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        import logging

        logger = logging.getLogger()
        original_handlers = logger.handlers[:]
        original_level = logger.level
        logger.handlers.clear()

        try:
            setup_logging(level="DEBUG")

            assert logger.level == logging.DEBUG

        finally:
            logger.handlers[:] = original_handlers
            logger.setLevel(original_level)

    def test_setup_logging_custom_format(self):
        """Test logging setup with custom format."""
        import logging

        logger = logging.getLogger()
        original_handlers = logger.handlers[:]
        logger.handlers.clear()

        try:
            custom_format = "%(levelname)s: %(message)s"
            setup_logging(format_string=custom_format)

            # Check that a handler was created
            assert len(logger.handlers) > 0

        finally:
            logger.handlers[:] = original_handlers

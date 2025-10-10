"""Pytest configuration and fixtures for PlexMCP tests."""

import os
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_plex_server():
    """Mock PlexServer for testing."""
    mock_server = Mock()
    mock_server.friendlyName = "Test Plex Server"
    mock_server.version = "1.32.0.123"
    mock_server.myPlexUsername = "testuser"
    return mock_server


@pytest.fixture
def mock_plex_api():
    """Mock plexapi for testing."""
    with patch('plex_mcp.services.plex_service.PlexServer') as mock_plex_server_class:
        mock_server_instance = Mock()
        mock_server_instance.friendlyName = "Test Plex Server"
        mock_server_instance.version = "1.32.0.123"
        mock_server_instance.myPlexUsername = "testuser"

        # Mock library sections
        mock_section = Mock()
        mock_section.title = "Movies"
        mock_section.type = "movie"
        mock_section.key = "1"
        mock_server_instance.library.sections.return_value = [mock_section]

        mock_plex_server_class.return_value = mock_server_instance
        yield mock_server_instance


@pytest.fixture
def sample_plex_config():
    """Sample Plex configuration for testing."""
    return {
        'server_url': 'http://localhost:32400',
        'plex_token': 'test_token_123',
        'timeout': 30
    }


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for consistent testing."""
    env_vars = {
        'PLEX_URL': 'http://localhost:32400',
        'PLEX_TOKEN': 'test_token_123',
        'PYTHONPATH': 'src'
    }

    with patch.dict(os.environ, env_vars):
        yield

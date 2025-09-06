"""FastMCP 2.10.1 server setup for Plex MCP."""
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP, MCPTool, MCPConfig

from .services.plex_service import PlexService
from .tools import (
    get_server_status,
    list_libraries,
    get_server_info,
    search_media,
    get_media_info,
    get_library_items,
    list_sessions,
    list_clients,
    control_playback
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlexMCP(FastMCP):
    """Plex MCP server implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Plex MCP server.
        
        Args:
            config: Optional configuration overrides
        """
        # Default configuration
        default_config = {
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'debug': False,
            },
            'plex': {
                'base_url': os.getenv('PLEX_SERVER_URL', 'http://localhost:32400'),
                'token': os.getenv('PLEX_TOKEN', ''),
                'timeout': int(os.getenv('PLEX_TIMEOUT', '30')),
            },
            'mcp': {
                'name': 'plex-mcp',
                'version': '1.0.0',
                'description': 'Plex Media Server MCP',
            }
        }
        
        # Merge with provided config
        if config:
            self._merge_config(default_config, config)
        
        # Initialize FastMCP
        super().__init__(config=default_config)
        
        # Initialize Plex service
        self.plex = PlexService(
            base_url=default_config['plex']['base_url'],
            token=default_config['plex']['token'],
            timeout=default_config['plex']['timeout']
        )
        
        # Register tools with dependency injection
        self.register_tool(get_server_status, self.plex)
        self.register_tool(list_libraries, self.plex)
        self.register_tool(get_server_info, self.plex)
        self.register_tool(search_media, self.plex)
        self.register_tool(get_media_info, self.plex)
        self.register_tool(get_library_items, self.plex)
        self.register_tool(list_sessions, self.plex)
        self.register_tool(list_clients, self.plex)
        self.register_tool(control_playback, self.plex)
    
    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    async def startup(self) -> None:
        """Perform startup tasks."""
        logger.info("Starting Plex MCP server...")
        await self.plex.connect()
        logger.info(f"Connected to Plex server: {self.plex.server.friendlyName}")
    
    async def shutdown(self) -> None:
        """Perform shutdown tasks."""
        logger.info("Shutting down Plex MCP server...")
        await self.plex.close()
        logger.info("Plex MCP server stopped")

def run_server(config_path: Optional[str] = None):
    """Run the Plex MCP server.
    
    Args:
        config_path: Optional path to a configuration file
    """
    # Load configuration if provided
    config = {}
    if config_path:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    
    # Create and start the server
    app = PlexMCP(config=config)
    
    # Get server config
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8000)
    debug = server_config.get('debug', False)
    
    # Run the server
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the Plex MCP server')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    args = parser.parse_args()
    
    run_server(config_path=args.config)

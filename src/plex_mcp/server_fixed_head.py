"""
PlexMCP - FastMCP 2.1 Server for Plex Media Server Management

Austrian efficiency for Sandra's media streaming needs.
Provides 22 tools: 10 core + 3 playlist + 2 remote + 2 performance + 2 admin + 3 Austrian efficiency
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console
from dotenv import load_dotenv

# Import our utility modules
from .utils import (
    get_logger,
    async_retry,
    run_in_executor,
    validate_plex_url,
    validate_plex_token,
    ValidationError
)

# Set up logger
logger = get_logger(__name__)

# Robust import handling for both package and direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when run as package)
    from .plex_manager import PlexManager, PlexAPIError
    from .config import PlexConfig
except ImportError:
    try:
        # Try absolute imports (when run directly)
        from plex_mcp.plex_manager import PlexManager, PlexAPIError
        from plex_mcp.config import PlexConfig
    except ImportError:
        # Final fallback - direct imports from same directory
        from plex_manager import PlexManager, PlexAPIError
        from config import PlexConfig

# Load environment variables from multiple possible paths
import pathlib
possible_env_paths = [
    pathlib.Path(__file__).parent.parent.parent / '.env',  # repo root
    pathlib.Path.cwd() / '.env',  # current working directory  
    pathlib.Path('D:/Dev/repos/plexmcp/.env')  # absolute path fallback
]

for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
else:
    load_dotenv()  # fallback

# Initialize console for logging (redirect to stderr for MCP compatibility)
console = Console(file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("PlexMCP 🎬")

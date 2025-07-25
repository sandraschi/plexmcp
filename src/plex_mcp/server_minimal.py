"""
PlexMCP - FastMCP 2.1 Server for Plex Media Server Management (MINIMAL WORKING VERSION)

Austrian efficiency for Sandra's media streaming needs.
Simple version to test functionality.
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
    from fastmcp import FastMCP
    from pydantic import BaseModel, Field
    from rich.console import Console
    from dotenv import load_dotenv
    print("✅ Core dependencies imported successfully")
except ImportError as e:
    print(f"❌ Core dependency import error: {e}")
    sys.exit(1)

# Now try to import our modules
try:
    # Direct absolute imports
    from plex_mcp.plex_manager import PlexManager, PlexAPIError
    from plex_mcp.config import PlexConfig
    print("✅ PlexMCP modules imported successfully")
except ImportError as e:
    print(f"❌ PlexMCP module import error: {e}")
    print("Trying fallback imports...")
    try:
        # Fallback imports
        from config import PlexConfig
        from plex_manager import PlexManager, PlexAPIError
        print("✅ PlexMCP modules imported via fallback")
    except ImportError as e2:
        print(f"❌ Fallback import also failed: {e2}")
        sys.exit(1)

# Load environment variables
load_dotenv()

# Initialize console for logging (no emojis for Windows compatibility)
console = Console()

# Initialize FastMCP server
mcp = FastMCP("PlexMCP")

# Global Plex manager (initialized on startup)
plex_manager: Optional[PlexManager] = None

class PlexServerStatus(BaseModel):
    """Plex server status information"""
    name: str = Field(description="Server name")
    version: str = Field(description="Plex server version")
    connected: bool = Field(description="Connection status")

async def get_plex_manager() -> PlexManager:
    """Get initialized Plex manager, creating if needed"""
    global plex_manager
    if plex_manager is None:
        config = PlexConfig()
        plex_manager = PlexManager(config)
    return plex_manager

@mcp.tool()
async def get_plex_status() -> PlexServerStatus:
    """
    Get Plex server status and identity information.
    
    Returns basic server information to test connectivity.
    
    Returns:
        Basic server status information
    """
    try:
        manager = await get_plex_manager()
        status_data = await manager.get_server_status()
        
        return PlexServerStatus(
            name=status_data.get('friendlyName', 'Plex Server'),
            version=status_data.get('version', 'Unknown'),
            connected=True
        )
        
    except Exception as e:
        console.print(f"[red]Error in get_plex_status: {e}[/red]")
        return PlexServerStatus(
            name="Error",
            version="Unknown",
            connected=False
        )

def main():
    """Main entry point for PlexMCP server"""
    console.print("[green]Starting PlexMCP - Minimal Test Version[/green]")
    console.print("[blue]Austrian efficiency for your media streaming![/blue]")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()

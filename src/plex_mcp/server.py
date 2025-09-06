"""
PlexMCP - FastMCP 2.10+ Server for Plex Media Server Management

Austrian efficiency for Sandra's media streaming needs.
"""

import sys

# Import the shared FastMCP instance
from .app import mcp

# Set up logger
from .utils import get_logger
logger = get_logger(__name__)

# Import all API modules to register their tools with the shared mcp instance
from .api import core, playback, playlists, admin, vienna

def main():
    """
    Main entry point for PlexMCP server with FastMCP 2.10+ compatibility.
    
    Supports both HTTP and STDIO (JSON-RPC) modes based on command line arguments.
    When run without arguments, defaults to STDIO mode (FastMCP 2.10+ default).
    
    For STDIO mode (default in FastMCP 2.10+): python -m plex_mcp.server
    For HTTP mode: python -m plex_mcp.server --http
    """
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='PlexMCP - Austrian efficiency for media streaming')
    parser.add_argument('--stdio', action='store_true', help='Run in STDIO (JSON-RPC) mode (default)')
    parser.add_argument('--http', action='store_true', help='Run in HTTP mode')
    parser.add_argument('--sse', action='store_true', help='Run in SSE mode (deprecated)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (HTTP/SSE mode only)')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on (HTTP/SSE mode only)')
    parser.add_argument('--path', default='/mcp', help='Path for HTTP mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Determine transport mode - default to stdio if no transport specified
    if args.http:
        transport_mode = "http"
    elif args.sse:
        transport_mode = "sse"
    else:
        transport_mode = "stdio"  # Default in FastMCP 2.10+
    
    # Log startup to stderr for visibility
    print(f"[PlexMCP] Starting FastMCP 2.10+ Server - Austrian efficiency for media streaming! 🚀", file=sys.stderr)
    print(f"[PlexMCP] Transport: {transport_mode.upper()}", file=sys.stderr)
    
    # Run server with FastMCP 2.10+ syntax
    try:
        if transport_mode == "stdio":
            # STDIO mode (default) - no additional parameters needed
            print("[PlexMCP] Running in STDIO mode - Ready for Claude Desktop! ✅", file=sys.stderr)
            mcp.run()  # stdio is default in FastMCP 2.10+
            
        elif transport_mode == "http":
            # HTTP mode (streamable HTTP)
            print(f"[PlexMCP] Running in HTTP mode on http://{args.host}:{args.port}{args.path}", file=sys.stderr)
            mcp.run(
                transport="http",
                host=args.host,
                port=args.port,
                path=args.path
            )
            
        elif transport_mode == "sse":
            # SSE mode (deprecated but still supported)
            print(f"[PlexMCP] Running in SSE mode on http://{args.host}:{args.port} (deprecated)", file=sys.stderr)
            mcp.run(
                transport="sse",
                host=args.host,
                port=args.port
            )
            
    except Exception as e:
        print(f"[PlexMCP] ERROR: Failed to start server: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()

"""
PlexMCP - FastMCP 2.1 Server for Plex Media Server Management

Austrian efficiency for Sandra's media streaming needs.
"""

import sys
from fastmcp import FastMCP

# Import all API modules to register their tools
from .api import core, playback, playlists, admin, vienna

# Set up logger
from .utils import get_logger
logger = get_logger(__name__)

# Create the main FastMCP instance
mcp = FastMCP(
    name="PlexMCP",
    version="2.1.0",
    description="Comprehensive Plex Media Server management with Austrian efficiency"
)

# Mount all API modules
mcp.mount("/core", core.app)
mcp.mount("/playback", playback.app)
mcp.mount("/playlists", playlists.app)
mcp.mount("/admin", admin.app)
mcp.mount("/vienna", vienna.app)

def main():
    """
    Main entry point for PlexMCP server with FastMCP 2.10+ compatibility.
    
    Supports both HTTP and STDIO (JSON-RPC) modes based on command line arguments.
    When run without arguments, defaults to HTTP mode for backward compatibility.
    
    For STDIO mode (recommended for FastMCP 2.10+), use: python -m plex_mcp.server --stdio
    """
    import argparse
    from fastmcp.transports import HTTPTransport, StdioTransport
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='PlexMCP - Austrian efficiency for media streaming')
    parser.add_argument('--stdio', action='store_true', help='Run in STDIO (JSON-RPC) mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (HTTP mode only)')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on (HTTP mode only)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Log startup to stderr
    print(f"[PlexMCP] Starting FastMCP 2.10+ Server - Austrian efficiency for media streaming!", file=sys.stderr)
    print(f"[PlexMCP] Mode: {'STDIO' if args.stdio else 'HTTP'}", file=sys.stderr)
    
    # Run in the appropriate mode
    if args.stdio:
        # STDIO mode (JSON-RPC over stdin/stdout)
        print("[PlexMCP] Running in STDIO (JSON-RPC) mode. Ready to accept requests...", file=sys.stderr)
        transport = StdioTransport()
        mcp.run(transport=transport, debug=args.debug)
    else:
        # HTTP mode (legacy)
        print(f"[PlexMCP] Running in HTTP mode on http://{args.host}:{args.port}", file=sys.stderr)
        transport = HTTPTransport(host=args.host, port=args.port)
        mcp.run(transport=transport, debug=args.debug)


if __name__ == "__main__":
    main()

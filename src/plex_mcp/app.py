"""
Shared FastMCP instance for PlexMCP.

This module creates the central FastMCP instance that all API modules use.
Separating it prevents circular import issues.
"""

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
import os
import sys

if os.name == 'nt':  # Windows only
    try:
        # Force binary mode for stdin/stdout to prevent CRLF conversion
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        # Fallback: just ensure no CRLF conversion
        pass

# DevNullStdout class for stdio mode to prevent any console output during initialization
class DevNullStdout:
    """Suppress all stdout writes during stdio mode to prevent JSON-RPC protocol corruption."""
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = []

    def write(self, text):
        # Buffer output instead of writing to stdout
        self.buffer.append(text)

    def flush(self):
        # Do nothing - prevent any stdout writes
        pass

    def get_buffered_output(self):
        """Get all buffered output for debugging if needed."""
        return ''.join(self.buffer)

    def restore(self):
        """Restore original stdout."""
        sys.stdout = self.original_stdout

# CRITICAL: Detect stdio mode BEFORE importing logger
# This must be done before ANY logging imports
_is_stdio_mode = not sys.stdout.isatty()

# NUCLEAR OPTION: Completely disable logger during stdio mode
# Import logger first, then replace it with a no-op to prevent any stdout writes
import logging

if _is_stdio_mode:
    # Replace stdout with our devnull version to catch any accidental writes
    original_stdout = sys.stdout
    sys.stdout = DevNullStdout(original_stdout)

    # Create a null logger that does nothing
    class NullLogger:
        def debug(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
        def critical(self, *args, **kwargs): pass
        def exception(self, *args, **kwargs): pass

        def setLevel(self, *args, **kwargs): pass
        def addHandler(self, *args, **kwargs): pass
        def removeHandler(self, *args, **kwargs): pass

    # Replace the logging module's getLogger function
    original_getLogger = logging.getLogger
    def null_getLogger(name=None):
        return NullLogger()
    logging.getLogger = null_getLogger

from fastmcp import FastMCP

# Create the main FastMCP instance with conversational features
mcp = FastMCP(
    name="PlexMCP",
    version="2.1.0",
    instructions="""You are PlexMCP, a comprehensive FastMCP 2.14.3 server for Plex Media Server management.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- Media Library Management: Browse, search, and organize your Plex libraries
- Playback Control: Control media playback across all connected clients
- Server Management: Monitor and manage Plex server health and performance
- User Management: Handle user accounts, permissions, and access
- Content Organization: Manage playlists, collections, and metadata

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex media workflows
- Agentic capabilities for intelligent content discovery and playback

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
"""
)


def http_app():
    """
    Return FastAPI app for HTTP mode (FastMCP 2.14+).

    This provides the HTTP interface that can be mounted in webapps.
    """
    return mcp.http_app()

# CRITICAL: After server initialization, restore stdout for stdio mode
# This allows the server to communicate via JSON-RPC while preventing initialization logging
if _is_stdio_mode:
    if hasattr(sys.stdout, 'restore'):
        sys.stdout.restore()
        # Now we can safely write to stdout for JSON-RPC communication

    # Restore the original logging functionality
    logging.getLogger = original_getLogger

    # Set up proper logging to stderr only (not stdout)
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Critical: log to stderr, not stdout
    )

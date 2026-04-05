"""
Shared FastMCP instance for PlexMCP.

This module creates the central FastMCP instance that all API modules use.
Separating it prevents circular import issues.
"""

# CRITICAL: Load .env file before any other imports
import os
from dotenv import load_dotenv
load_dotenv()

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
import sys

if os.name == "nt":  # Windows only
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
        return "".join(self.buffer)

    def restore(self):
        """Restore original stdout."""
        sys.stdout = self.original_stdout


# CRITICAL: Detect stdio mode BEFORE importing logger
# This must be done before ANY logging imports
_is_stdio_mode = not sys.stdout.isatty()
# Pytest and tooling use non-TTY stdout; replacing logging globally breaks FastMCP / pytest / ruff.
if os.getenv("PLEXMCP_ALLOW_LOGGING", "").lower() in ("1", "true", "yes") or any(
    "pytest" in (arg or "") for arg in sys.argv
):
    _is_stdio_mode = False

# NUCLEAR OPTION: Completely disable logger during stdio mode
# Import logger first, then replace it with a no-op to prevent any stdout writes
import logging  # noqa: E402

if _is_stdio_mode:
    # Replace stdout with our devnull version to catch any accidental writes
    original_stdout = sys.stdout
    sys.stdout = DevNullStdout(original_stdout)

    # Create a null logger that does nothing
    # Create a null logger that does nothing but satisfies fastmcp's requirements
    class NullLogger(logging.Logger):
        def __init__(self, name="null", level=logging.NOTSET):
            super().__init__(name, level)
            self.propagate = False
            self.handlers = []

        def handle(self, record):
            pass

        def addHandler(self, hdlr):
            pass

        def removeHandler(self, hdlr):
            pass

        def hasHandlers(self):
            return False

    # Replace the logging module's getLogger function
    original_getLogger = logging.getLogger

    def null_getLogger(name=None):
        return NullLogger(name or "root")

    logging.getLogger = null_getLogger

from contextlib import asynccontextmanager  # noqa: E402

from fastmcp import FastMCP, Context
from fastmcp.prompts import Message  # noqa: E402

from .sampling import PlexSamplingConfig, PlexSamplingHandler  # noqa: E402


@asynccontextmanager
async def _plex_lifespan(app):
    """FastMCP 3.2 lifespan hook for Plex connectivity and state management."""
    yield


_plex_sampling_config = PlexSamplingConfig.from_env()
_plex_sampling_handler = PlexSamplingHandler(config=_plex_sampling_config)
_USE_CLIENT_SAMPLING = os.getenv("PLEX_SAMPLING_USE_CLIENT_LLM", "").lower() in ("1", "true", "yes")

mcp = FastMCP(
    "PlexMCP",
    version="3.2.0",
    instructions=(
        "PlexMCP is a SOTA FastMCP 3.2 server for Plex Media Server. "
        "It provides comprehensive library, media, and search tools using the Portmanteau pattern. "
        "Metadata RAG is available via plex_rag; sampling is handled via PLEX_SAMPLING_BASE_URL. "
        "Consult resource://plex/capabilities and resource://plex/skills for expert guidance."
    ),
    lifespan=_plex_lifespan,
    sampling_handler=_plex_sampling_handler,
    sampling_handler_behavior="fallback" if _USE_CLIENT_SAMPLING else "always",
    on_duplicate="replace",
    strict_input_validation=True,
)


@mcp.resource("resource://plex/health")
def plex_health_resource() -> str:
    """Health check for monitoring and load balancers."""
    try:
        from .monitoring import get_health_metrics
        import asyncio
        
        # Get health metrics
        health_data = asyncio.run(get_health_metrics())
        
        # Add basic system info
        import time
        import sys
        
        health_data.update({
            "version": "3.2.0",
            "python_version": sys.version,
            "fastmcp_version": "3.2.0",
            "tools_count": 21,
            "resources_count": 3,
        })
        
        import json
        return json.dumps(health_data, indent=2)
    except Exception as e:
        return f'{{"status": "unhealthy", "error": "{str(e)}"}}'


@mcp.resource("resource://plex/capabilities")
def plex_capabilities_resource() -> str:
    """Discover tools, sampling, RAG, and agentic entrypoints."""
    return """# PlexMCP capabilities (FastMCP 3.2)

## Tools
Portmanteau: plex_library, plex_media, plex_search, plex_streaming, plex_user, plex_playlist,
plex_metadata, plex_server, plex_performance, plex_reporting, plex_collections, plex_quality,
plex_rag, plex_help, plex_integration, plex_audio_mgr, and others — see plex_help(operation='discover').

## Sampling
- Default: OpenAI-compatible HTTP at PLEX_SAMPLING_BASE_URL (e.g. Ollama http://127.0.0.1:11434/v1).
- PLEX_SAMPLING_USE_CLIENT_LLM=1: prefer MCP host for sampling.
- agentic_plex_workflow: sample_step loop with real tool execution.
- plex_natural_assistant: sample() only (no tools).

## RAG
plex_rag: LanceDB-backed metadata (movies, shows, music artists) when indexing is configured.


## Prompts
plex_media_guide, prompt://plex/rag-workflow, prompt://plex/agentic-pattern, prompt://plex/library-tour
"""


@mcp.resource("resource://plex/skills")
def plex_skills_resource() -> str:
    """Expert personas and workflows (skills reference for LLMs)."""
    return """# PlexMCP skills (2026)

## Plex expert
Power-user help: libraries, agents, transcoding, remote access, managed users, diagnostics.
Use plex_library, plex_server, plex_user, plex_performance, plex_search. Never invent server URLs or tokens.

## Anime & serial drama curator
Series structure, seasons, anime collections, binge order, episode lookup.
Use plex_media (browse), plex_search, plex_collections; confirm show-type libraries.

## Home theater / A/V
Direct play, transcoding triggers, subtitles, audio tracks. Use plex_streaming, plex_server, plex_quality.

## Semantic discovery
Natural-language discovery after indexing: plex_rag(operation='semantic_search', query='...'). Run sync_metadata if results are empty.

## Agentic
agentic_plex_workflow(workflow_prompt, available_tools=['plex_library','plex_search',...]) for multi-step tasks.
"""


@mcp.prompt()
def plex_media_guide() -> list[Message]:
    """Guide for Plex media search and RAG. Use for agentic workflows."""
    return [
        Message(
            "PlexMCP: Use plex_search for keyword search; use plex_rag(operation='semantic_search', query='...') for natural-language semantic search over indexed metadata. Run plex_rag(operation='sync_metadata') once to index before semantic search.",
            role="user",
        )
    ]


@mcp.prompt("prompt://plex/rag-workflow")
def prompt_plex_rag_workflow() -> str:
    """Instructions for metadata sync and semantic query."""
    return """Guide the user through Plex metadata RAG.
1. Run plex_rag(operation='sync_metadata') to index libraries (may take time on large libraries).
2. Run plex_rag(operation='semantic_search', query='...', limit=...) for natural-language discovery.
3. If results are empty, confirm PLEX_TOKEN/PLEX_URL and that sync completed; check plex_help for RAG status."""


@mcp.prompt("prompt://plex/agentic-pattern")
def prompt_plex_agentic_pattern() -> str:
    """How to invoke agentic_plex_workflow safely."""
    return """Use agentic_plex_workflow with:
- workflow_prompt: clear goal in natural language.
- available_tools: exact tool names from this server (e.g. plex_library, plex_search, plex_media).
- max_iterations: 5–10 typically.
Requires sampling (Ollama at PLEX_SAMPLING_BASE_URL or client sampling). Do not claim actions were performed if tools were not called."""


@mcp.prompt("prompt://plex/library-tour")
def prompt_plex_library_tour() -> str:
    """Walkthrough for listing and browsing libraries."""
    return """Walk the user through exploring Plex via MCP:
1. plex_library(operation='list') for sections and types.
2. plex_media(operation='browse', library_id='...', ...) for items (use id from list).
3. plex_search for keyword search across libraries or within one library."""


def http_app():
    """
    Return ASGI app for HTTP mode (FastMCP 3.2).

    This provides the HTTP interface for webapp fleet discovery and dashboard embedding.
    """
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    allowed_origins = [
        "http://localhost:10741",
        "http://127.0.0.1:10741",
        "http://localhost:10740",
        "http://127.0.0.1:10740",
    ]
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
    ]
    return mcp.http_app(middleware=middleware)


# CRITICAL: After server initialization, restore stdout for stdio mode
# This allows the server to communicate via JSON-RPC while preventing initialization logging
if _is_stdio_mode:
    if hasattr(sys.stdout, "restore"):
        sys.stdout.restore()
        # Now we can safely write to stdout for JSON-RPC communication

    # Restore the original logging functionality
    logging.getLogger = original_getLogger

    # Set up proper logging to stderr only (not stdout)
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Critical: log to stderr, not stdout
    )

#!/usr/bin/env python3
"""
PlexMCP CLI entry — delegates to the shared FastMCP app in ``server`` (tools on ``mcp`` from ``app``).

Do not construct a separate ``FastMCP`` here; that would start stdio with no registered tools.
"""


def main() -> None:
    """Start PlexMCP using fleet transport (stdio / http / sse)."""
    from .config import get_settings, setup_logging

    setup_logging()
    get_settings()

    from .server import main as server_main

    server_main()


if __name__ == "__main__":
    main()

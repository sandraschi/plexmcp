"""
PlexMCP Server Lifecycle Tool

Graceful self-termination for agents and the fleet launcher. The HTTP daemon
is stopped via POST /api/shutdown; this MCP tool covers stdio/proxy instances
(where there is no HTTP listener to call).
"""

import os
import threading
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def plex_shutdown(
    operation: Annotated[
        Literal["status", "shutdown"],
        Field(
            description="status: report whether this instance owns state or is a proxy. shutdown: exit this process after responding."
        ),
    ],
) -> ToolResult:
    """
    Graceful self-termination for agents and the fleet launcher.

    OPERATIONS:
    - status: report process ownership (standalone server vs HTTP-daemon proxy).
    - shutdown: respond first, then exit the process ~500 ms later so the
      MCP response flushes (same contract as POST /api/shutdown).

    ## Return Format
    {"success": bool, "operation": str, "message": str}

    ## Examples
    await plex_shutdown(operation="status")
    await plex_shutdown(operation="shutdown")
    """
    try:
        if operation == "status":
            probe_url = os.environ.get("PLEX_MCP_API_URL", "http://127.0.0.1:10740/mcp")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "status",
                    "message": f"PlexMCP stdio instance alive (pid {os.getpid()}). HTTP daemon probe URL: {probe_url}.",
                }
            )

        if operation == "shutdown":
            timer = threading.Timer(0.5, lambda: os._exit(0))
            timer.daemon = True
            timer.start()
            logger.info("plex_shutdown requested — exiting in ~500 ms")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "shutdown",
                    "message": "PlexMCP shutting down in ~500 ms.",
                }
            )

        return ToolResult(
            content={
                "success": False,
                "operation": operation,
                "message": f"Unknown operation: {operation}. Use 'status' or 'shutdown'.",
            }
        )
    except Exception as e:
        logger.error("Error in plex_shutdown operation '%s': %s", operation, e, exc_info=True)
        return ToolResult(
            content={
                "success": False,
                "operation": operation,
                "message": f"plex_shutdown failed: {e}",
            }
        )

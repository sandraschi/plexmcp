"""
Optional *arr stack status (Radarr, Sonarr, Lidarr) via HTTP API.

Does not manage downloads; reports reachability, version, and queue counts when URLs/API keys are set.
"""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.arr_client import get_arr_stack_status
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def arr_stack(
    operation: Annotated[Literal["status"], Field(description="Operation to perform.")],
) -> ToolResult:
    """Query Radarr, Sonarr, and Lidarr HTTP APIs for media stack health.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 3 synchronization services into a single tool to match established
    industry patterns for managing "the stack" as a unified metadata pipeline.

    ## Return Format
    {"success": bool, "data": dict, "message": str}

    ## Examples
    await arr_stack(operation="status")
    """
    try:
        data = await get_arr_stack_status()
        return ToolResult(
            content={
                "success": True,
                "operation": operation,
                "data": data,
                "message": "Arr stack status (HTTP probe).",
            }
        )
    except Exception as e:
        logger.error("arr_stack failed: %s", e, exc_info=True)
        return ToolResult(
            content={
                "success": False,
                "operation": operation,
                "error": str(e),
                "error_code": "ARR_STACK_ERROR",
                "suggestions": [
                    "Set RADARR_URL / SONARR_URL / LIDARR_URL and matching X-Api-Key values in the environment.",
                    "In the webapp, use Settings to save URLs and API keys (writes data/settings.json).",
                ],
            }
        )

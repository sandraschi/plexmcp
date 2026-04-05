"""
Optional *arr stack status (Radarr, Sonarr, Lidarr) via HTTP API.

Does not manage downloads; reports reachability, version, and queue counts when URLs/API keys are set.
"""

from typing import Any, Literal

from ...app import mcp
from ...services.arr_client import get_arr_stack_status
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool()
async def arr_stack(
    operation: Literal["status"],
) -> dict[str, Any]:
    """
    Query Radarr, Sonarr, and Lidarr HTTP APIs for media stack health.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 3 synchronization services into a single tool to match established
    industry patterns for managing "the stack" as a unified metadata pipeline.

    OPERATIONS:
    - status: Probe HTTP reachability, version strings, and active download queue counts.

    Returns:
    FastMCP 3.1+ dialogic response with stack reachability and pipeline status.
    Enables autonomous synchronization monitoring and reachability auditing.
    """
    try:
        data = await get_arr_stack_status()
        return {
            "success": True,
            "operation": operation,
            "data": data,
            "message": "Arr stack status (HTTP probe).",
        }
    except Exception as e:
        logger.error("arr_stack failed: %s", e, exc_info=True)
        return {
            "success": False,
            "operation": operation,
            "error": str(e),
            "error_code": "ARR_STACK_ERROR",
            "suggestions": [
                "Set RADARR_URL / SONARR_URL / LIDARR_URL and matching X-Api-Key values in the environment.",
                "In the webapp, use Settings to save URLs and API keys (writes data/settings.json).",
            ],
        }

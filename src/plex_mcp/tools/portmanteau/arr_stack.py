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
    """Query Radarr, Sonarr, and Lidarr HTTP APIs (optional integration).

    PORTMANTEAU PATTERN RATIONALE: One tool for the whole *arr snapshot instead of three
    separate tools, matching how operators think about the stack.

    Prerequisites:
        Environment variables (or webapp Settings file that sets them):
        - RADARR_URL, RADARR_API_KEY
        - SONARR_URL, SONARR_API_KEY
        - LIDARR_URL, LIDARR_API_KEY

    Operations:
        status: GET /system/status and /queue on each configured service (API v3 for Radarr/Sonarr, v1 for Lidarr).

    Returns:
        success, data with radarr/sonarr/lidarr objects (configured, reachable, version, queue_count, error).
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

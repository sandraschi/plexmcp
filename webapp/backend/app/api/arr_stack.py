"""Optional Radarr / Sonarr / Lidarr HTTP status (same probes as MCP arr_stack tool)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def arr_stack_status():
    """Reachability, version, and queue counts for configured *arr apps."""
    from plex_mcp.services.arr_client import get_arr_stack_status

    return await get_arr_stack_status()

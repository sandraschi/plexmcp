"""Error handling utilities."""

from fastapi import HTTPException


def handle_mcp_error(e: Exception) -> HTTPException:
    """Convert MCP/tool errors to HTTP exceptions."""
    msg = str(e)
    if "PLEX_TOKEN" in msg:
        return HTTPException(status_code=503, detail="PLEX_TOKEN not configured. Set in backend/.env")
    if "PLEX" in msg and "required" in msg.lower():
        return HTTPException(status_code=503, detail=msg)
    return HTTPException(status_code=502, detail=msg)

import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def handle_mcp_error(e: Exception) -> HTTPException:
    """Convert MCP/tool errors to HTTP exceptions."""
    msg = str(e)
    logger.error("MCP Tool Error (%s): %s", type(e).__name__, msg)
    
    if "PLEX_TOKEN" in msg:
        return HTTPException(status_code=503, detail="PLEX_TOKEN not configured. Set in backend/.env")
    if "PLEX" in msg and ("required" in msg.lower() or "unauthorized" in msg.lower()):
        return HTTPException(status_code=401, detail=f"Plex Authentication Failed: {msg}")
    
    return HTTPException(status_code=502, detail=msg)

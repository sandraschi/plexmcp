"""Legacy v1 API: semantic search and chat (delegated to MCP tools)."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ..mcp.client import mcp_client

logger = logging.getLogger(__name__)

router = APIRouter()


class SearchQuery(BaseModel):
    query: str
    limit: int = 10


class ChatQuery(BaseModel):
    message: str
    context: str = ""


@router.post("/search")
async def semantic_search(req: SearchQuery) -> dict:
    """Semantic search over RAG index (uses plex_rag tool)."""
    try:
        result = await mcp_client.call_tool(
            "plex_rag",
            {
                "operation": "semantic_search",
                "query": req.query,
                "limit": req.limit,
            },
        )
    except Exception as e:
        logger.exception("v1 search error")
        return {"success": False, "error": str(e)}
    else:
        if not result.get("success", True):
            return {
                "success": False,
                "error": result.get("error", "RAG not available"),
                "results": [],
            }
        return {
            "success": True,
            "results": result.get("data") or result.get("results") or [],
        }


@router.post("/chat")
async def chat_with_media(req: ChatQuery) -> dict:
    """Placeholder for chat (LLM orchestration)."""
    return {
        "success": True,
        "response": f"Chat integration placeholder. Received: {req.message}",
        "context_used": bool(req.context),
    }

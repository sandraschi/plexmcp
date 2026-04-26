"""AI workflows: run multi-step flows (e.g. search Plex then summarize with LLM)."""

import logging

import httpx
from fastapi import APIRouter, Body

from ..config import settings
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"


def _llm_url() -> str:
    return (settings.LLM_BASE_URL or OLLAMA_DEFAULT).rstrip("/")


@router.post("/run")
async def run_workflow(
    body: dict = Body(...),
):
    """Run a workflow by id. Supported: search_and_summarize."""
    workflow_id = (body.get("id") or body.get("workflow_id") or "").strip()
    params = body.get("params") or body.get("arguments") or {}
    if not workflow_id:
        return {"success": False, "error": "Missing id or workflow_id"}

    if workflow_id == "search_and_summarize":
        query = params.get("query", "")
        library_id = params.get("library_id")
        model = params.get("model", "llama3.2")
        if not query:
            return {"success": False, "error": "params.query required"}
        try:
            search_result = await mcp_client.call_tool(
                "plex_search",
                {"operation": "search", "query": query, "library_id": library_id, "limit": 20},
            )
        except Exception as e:
            raise handle_mcp_error(e) from e
        if not search_result.get("success"):
            return {"success": False, "search_result": search_result, "error": "Plex search failed"}
        items = search_result.get("data") or search_result.get("results") or []
        text_blob = str(items)[:8000]
        messages = [
            {
                "role": "system",
                "content": "Summarize the following Plex search results in a few short sentences. List key titles or categories.",
            },
            {"role": "user", "content": f"Query: {query}\n\nResults:\n{text_blob}"},
        ]
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                r = await client.post(
                    f"{_llm_url()}/api/chat",
                    json={"model": model, "messages": messages, "stream": False},
                )
        except Exception as e:
            logger.warning("LLM summarize failed: %s", e)
            return {
                "success": True,
                "workflow_id": workflow_id,
                "search_result": search_result,
                "summary": None,
                "error": str(e),
            }
        if r.status_code != 200:
            return {
                "success": True,
                "workflow_id": workflow_id,
                "search_result": search_result,
                "summary": None,
                "error": r.text,
            }
        data = r.json()
        summary = (data.get("message") or {}).get("content", "").strip()
        return {"success": True, "workflow_id": workflow_id, "search_result": search_result, "summary": summary}
    return {"success": False, "error": f"Unknown workflow: {workflow_id}"}

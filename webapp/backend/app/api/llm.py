"""LLM API for chat, prompt refine, and workflows (Ollama / OpenAI-compatible)."""

import json
import logging
import os

import httpx
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from ..chat_context import build_chat_preprompt
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_libraries",
            "description": "List all Plex media libraries with their types (movie, show, music, photo).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_media",
            "description": "Search for media in Plex by title, actor, genre, or year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search text — title, actor, or keywords."},
                    "library_id": {"type": "string", "description": "Library section ID to search within (optional)."},
                    "limit": {"type": "integer", "description": "Max results (1-50).", "default": 15},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_server_status",
            "description": "Get Plex server status, version, and connection info.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_media",
            "description": "Get recently added media across all libraries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 20},
                },
                "required": [],
            },
        },
    },
]


def _get_base_url(provider: str | None = None, base_url: str | None = None) -> str:
    if base_url and base_url.strip():
        return base_url.rstrip("/")
    p = (provider or os.environ.get("LLM_PROVIDER") or settings.LLM_PROVIDER or "ollama").lower()
    url = os.environ.get("LLM_BASE_URL") or settings.LLM_BASE_URL
    if p in ("ollama",):
        return url or OLLAMA_DEFAULT
    if p in ("lmstudio", "lm_studio"):
        return url or LMSTUDIO_DEFAULT
    return url or OLLAMA_DEFAULT


@router.get("/models")
async def list_models(
    provider: str | None = None,
    base_url: str | None = None,
):
    """List available models (Ollama or OpenAI-compatible)."""
    url = _get_base_url(provider, base_url)
    if ":11434" in url or "ollama" in url.lower():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{url}/api/tags")
                if r.status_code != 200:
                    return {"models": [], "error": r.text}
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return {"models": models, "provider": "ollama"}
        except Exception as e:
            logger.warning("Ollama models fetch failed: %s", e)
            return {"models": [], "error": str(e)}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {}
            key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
            if key:
                headers["Authorization"] = f"Bearer {key}"
            r = await client.get(f"{url.rstrip('/')}/v1/models", headers=headers or None)
            if r.status_code != 200:
                return {"models": [], "error": r.text}
            data = r.json()
            items = data.get("data", data.get("models", []))
            names = [x.get("id") or x.get("name") or str(x) for x in (items or []) if isinstance(x, (dict, str))]
            if not isinstance(items, list):
                names = []
            return {"models": names, "provider": "openai-compatible"}
    except Exception as e:
        logger.warning("Models fetch failed: %s", e)
        return {"models": [], "error": str(e)}


@router.post("/chat")
async def chat(
    messages: list[dict[str, str]] = Body(...),
    model: str = Body(os.environ.get("LLM_MODEL", "gemma4:12b")),
    stream: bool = Body(False),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
    use_context: bool = Body(True),
):
    """Chat completion. Supports streaming. Injects MCP/webapp/libraries context when use_context=True."""
    if use_context and messages:
        try:
            preprompt = await build_chat_preprompt()
            if preprompt:
                existing_system = ""
                rest = list(messages)
                if rest and (rest[0].get("role") or "").lower() == "system":
                    existing_system = (rest[0].get("content") or "").strip()
                    rest = rest[1:]
                system_content = preprompt + ("\n\n" + existing_system if existing_system else "")
                messages = [{"role": "system", "content": system_content}] + rest
        except Exception as e:
            logger.warning("Chat preprompt build failed: %s", e)
    url = _get_base_url(provider, base_url)
    if ":11434" in url or "ollama" in url.lower():
        req_url = f"{url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": stream}
        if stream:

            async def _stream():
                async with (
                    httpx.AsyncClient(timeout=60.0) as client,
                    client.stream("POST", req_url, json=payload) as resp,
                ):
                    async for chunk in resp.aiter_text():
                        yield chunk

            return StreamingResponse(_stream(), media_type="text/event-stream")
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(req_url, json=payload)
            if r.status_code != 200:
                return {"error": r.text, "status": r.status_code}
            return r.json()
    req_url = f"{url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {"model": model, "messages": messages, "stream": stream}
    if stream:

        async def _stream_openai():
            async with (
                httpx.AsyncClient(timeout=60.0) as client,
                client.stream("POST", req_url, json=payload, headers=headers) as resp,
            ):
                async for chunk in resp.aiter_text():
                    yield chunk

        return StreamingResponse(_stream_openai(), media_type="text/event-stream")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(req_url, json=payload, headers=headers)
        if r.status_code != 200:
            return {"error": r.text, "status": r.status_code}
        return r.json()


async def _llm_call(messages: list, model: str, url: str, tools: list | None = None) -> dict | None:
    if ":11434" in url or "ollama" in url.lower():
        payload = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                r = await client.post(f"{url}/api/chat", json=payload)
                return r.json() if r.status_code == 200 else None
            except httpx.ConnectError:
                return None
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {"model": model, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(f"{url}/v1/chat/completions", json=payload, headers=headers)
            return r.json() if r.status_code == 200 else None
        except httpx.ConnectError:
            return None


def _extract_message(data: dict | None) -> dict | None:
    if not data:
        return None
    if "message" in data:
        return data["message"]
    choices = data.get("choices", [])
    return choices[0].get("message") if choices else None


def _extract_content(msg: dict | None) -> str:
    return (msg or {}).get("content") or ""


def _extract_tool_calls(msg: dict | None) -> list[dict]:
    tc = (msg or {}).get("tool_calls") or []
    return [{"id": t.get("id", ""), "function": t.get("function", t)} for t in tc]


async def _dispatch_mcp(tool_name: str, args: dict) -> dict:
    from ..mcp.client import mcp_client as _mc

    route = {
        "list_libraries": ("plex_library", {"operation": "list"}),
        "search_media": (
            "plex_search",
            {"operation": "search", "query": args.get("query", ""), "limit": min(args.get("limit", 15), 50)},
        ),
        "get_server_status": ("plex_server", {"operation": "status"}),
        "get_recent_media": ("plex_media", {"operation": "get_recent", "limit": min(args.get("limit", 20), 50)}),
    }
    mcp_tool, mcp_args = route.get(tool_name, (None, None))
    if not mcp_tool:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        result = await _mc.call_tool(mcp_tool, mcp_args)
        return result if isinstance(result, dict) else {"result": str(result)}
    except Exception as e:
        logger.warning("Tool call %s failed: %s", tool_name, e)
        return {"error": str(e)}


@router.post("/agentic")
async def agentic_chat(
    messages: list[dict[str, str]] = Body(...),
    model: str = Body("gemma4:12b"),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
):
    """Agentic chat with proper OpenAI-compatible tool calling for Plex."""
    try:
        return await _agentic_impl(messages, model, provider, base_url)
    except Exception as e:
        logger.error("Agentic chat error: %s", e, exc_info=True)
        return {"message": {"role": "assistant", "content": f"Sorry, something went wrong: {e}"}}


async def _agentic_impl(
    messages: list[dict[str, str]],
    model: str,
    provider: str | None,
    base_url: str | None,
) -> dict:
    url = _get_base_url(provider, base_url)
    system_msgs = [m for m in messages if m["role"] == "system"]
    history = [m for m in messages if m["role"] in ("user", "assistant")]
    if not history:
        return {"message": {"role": "assistant", "content": "Send a message to start."}}

    ctx = [*system_msgs, *history]
    for _turn in range(5):
        data = await _llm_call(ctx, model, url, tools=TOOLS)
        msg = _extract_message(data)
        if not msg:
            return {"message": {"role": "assistant", "content": "LLM not reachable"}}

        content = _extract_content(msg)
        tool_calls = _extract_tool_calls(msg)
        if not tool_calls:
            return {"message": {"role": "assistant", "content": content or "Done."}}

        ctx.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "") if isinstance(fn, dict) else ""
            raw_args = fn.get("arguments", "{}") if isinstance(fn, dict) else "{}"
            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

            result = await _dispatch_mcp(name, parsed_args)
            result_str = json.dumps(result, default=str, ensure_ascii=False)
            if len(result_str) > 4000:
                result_str = result_str[:4000] + "\n... (truncated)"
            ctx.append({"role": "tool", "content": result_str, "tool_call_id": tc.get("id", ""), "name": name})

    last_msg = _extract_message(await _llm_call(ctx, model, url))
    return {
        "message": {"role": "assistant", "content": _extract_content(last_msg) or "I need more specific information."}
    }


@router.post("/refine")
async def refine_prompt(
    body: dict = Body(...),
):
    """Use LLM to refine/improve a user message (e.g. before sending to chat)."""
    text = body.get("text", "") or ""
    model = body.get("model") or os.environ.get("LLM_MODEL", "gemma4:12b")
    provider = body.get("provider")
    base_url = body.get("base_url")
    """Use LLM to refine/improve a user message (e.g. before sending to chat)."""
    url = _get_base_url(provider, base_url)
    system_msg = "Rewrite the following user message to be clearer and more specific. Keep the same intent. Output only the rewritten message, no preamble."
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": text},
    ]
    if ":11434" in url or "ollama" in url.lower():
        req_url = f"{url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": False}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(req_url, json=payload)
            if r.status_code != 200:
                return {"refined": text, "error": r.text}
            data = r.json()
            content = (data.get("message") or {}).get("content", "").strip() or text
            return {"refined": content}
    req_url = f"{url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
    if key:
        headers["Authorization"] = f"Bearer {key}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(req_url, json={"model": model, "messages": messages}, headers=headers)
        if r.status_code != 200:
            return {"refined": text, "error": r.text}
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip() or text
        return {"refined": content}

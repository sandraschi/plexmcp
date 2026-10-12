"""LLM API for chat, prompt refine, and workflows (local + cloud providers)."""

import asyncio
import json
import logging
import os

import httpx
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from .. import llm_providers as lp
from ..chat_context import build_chat_preprompt
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"


def _registry_provider(provider: str | None) -> dict | None:
    """Return the registry row for `provider` if it's a known ID, else None
    (a custom base_url / legacy config that predates the provider registry)."""
    if not provider:
        return None
    return lp.get_provider(provider)


# --- Provider registry, onboarding, VRAM (new: local + cloud, GPU-less-safe) --


@router.get("/providers")
async def get_providers():
    """Registry of local + cloud providers: which are configured, never key bytes."""
    return {"providers": lp.public_provider_info()}


@router.get("/onboarding")
async def get_onboarding():
    """Fresh-install starter facts + recommended path (local vs cloud)."""
    return lp.onboarding_state()


@router.get("/gpus")
async def get_gpus():
    """Live GPU VRAM telemetry. Empty list on a GPU-less machine - not an error."""
    return {"gpus": await asyncio.to_thread(lp.gpu_vram)}


@router.get("/loaded")
async def get_loaded(base_url: str | None = None):
    """Models currently resident on the local Ollama engine (VRAM KPI)."""
    return await lp.ollama_loaded(base_url or OLLAMA_DEFAULT)


@router.post("/unload")
async def post_unload(body: dict = Body(default={})):
    """Evict Ollama models from VRAM. Empty/omitted `keep` evicts everything -
    the escape hatch when VRAM is full and an AI task needs room to run."""
    keep = str(body.get("keep") or "").strip()
    base_url = body.get("base_url") or OLLAMA_DEFAULT
    result = await lp.switch_ollama_model(keep, base_url)
    return {"success": True, **result}


@router.post("/keys/{provider}")
async def save_provider_key(provider: str, body: dict = Body(...)):
    """Save a cloud provider's API key to the 0600 keystore (write-only - never
    echoed back)."""
    api_key = str(body.get("api_key") or "")
    try:
        lp.save_key(provider, api_key)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    return {"success": True, "provider": provider}


@router.delete("/keys/{provider}")
async def delete_provider_key(provider: str):
    """Remove a cloud provider's stored API key."""
    try:
        deleted = lp.delete_key(provider)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    return {"success": True, "deleted": deleted}


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
    """List available models. Cloud providers (Anthropic, DeepSeek, OpenRouter,
    keyed OpenAI) go through the provider registry for correct auth; a custom
    base_url always overrides (points a local engine at a non-default port)."""
    if not (base_url and base_url.strip()):
        row = _registry_provider(provider)
        if row is not None:
            result = await lp.list_provider_models(row["id"])
            return {"models": result["models"], "provider": row["id"], "source": result["source"]}
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

    row = _registry_provider(provider) if not (base_url and base_url.strip()) else None
    if row is not None and row["kind"] == "cloud":
        # Cloud providers (including Anthropic, whose format the old ollama/
        # openai-compatible branches below can't speak) go through the
        # registry for correct auth headers and message-format conversion.
        if stream:

            async def _stream_registry():
                try:
                    async for chunk in lp.chat_stream(row["id"], model, messages):
                        yield chunk
                except Exception as e:
                    logger.warning("Registry chat stream (%s) failed: %s", row["id"], e)
                    yield f"data: {json.dumps({'error': str(e)})}\n\n".encode()

            return StreamingResponse(_stream_registry(), media_type="text/event-stream")
        try:
            content = await lp.chat_complete(row["id"], model, messages)
        except Exception as e:
            return {"error": str(e), "status": 502}
        return {"message": {"role": "assistant", "content": content}}

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


async def _llm_call(
    messages: list, model: str, url: str, tools: list | None = None, provider: str | None = None
) -> dict | None:
    """OpenAI-shaped chat call (choices[0].message, optional tool_calls).

    Anthropic is deliberately not routed through here - its message/tool
    format is different (content blocks, not choices) and the extraction
    helpers below assume OpenAI shape. Callers keep Anthropic on the plain
    chat_complete() path (see _agentic_impl) instead of half-supporting tools.
    """
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
    row = _registry_provider(provider) if provider else None
    if row is not None and row["kind"] == "cloud":
        # Registry rows know their own exact chat path (providers disagree on
        # whether it's prefixed with /v1) - use it instead of guessing.
        key = lp.get_key(row["id"])
        if key:
            headers["Authorization"] = f"Bearer {key}"
        chat_url = row["base_url"] + row["chat_path"]
    else:
        key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
        if key:
            headers["Authorization"] = f"Bearer {key}"
        chat_url = f"{url}/v1/chat/completions"
    payload = {"model": model, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(chat_url, json=payload, headers=headers)
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
    # Prefab cards produced by tool calls during this turn. Returned to the
    # frontend so the webapp can render the same cards an MCP host renders.
    prefabs: list[dict] = []
    row = _registry_provider(provider)
    if row is not None and row["id"] == "anthropic":
        # Anthropic's tool-use format is content blocks, not OpenAI-style
        # tool_calls - the extraction helpers below assume OpenAI shape.
        # Graceful degrade: answer directly, no Plex tool-calling, rather
        # than send it a request format it can't parse.
        try:
            content = await lp.chat_complete("anthropic", model, messages)
        except Exception as e:
            return {"message": {"role": "assistant", "content": f"Anthropic request failed: {e}"}}
        return {"message": {"role": "assistant", "content": content or "Done."}, "prefabs": prefabs}

    url = _get_base_url(provider, base_url)
    system_msgs = [m for m in messages if m["role"] == "system"]
    history = [m for m in messages if m["role"] in ("user", "assistant")]
    if not history:
        return {
            "message": {"role": "assistant", "content": "Send a message to start."},
            "prefabs": prefabs,
        }

    ctx = [*system_msgs, *history]
    for _turn in range(5):
        data = await _llm_call(ctx, model, url, tools=TOOLS, provider=provider)
        msg = _extract_message(data)
        if not msg:
            return {
                "message": {"role": "assistant", "content": "LLM not reachable"},
                "prefabs": prefabs,
            }

        content = _extract_content(msg)
        tool_calls = _extract_tool_calls(msg)
        if not tool_calls:
            return {
                "message": {"role": "assistant", "content": content or "Done."},
                "prefabs": prefabs,
            }

        ctx.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "") if isinstance(fn, dict) else ""
            raw_args = fn.get("arguments", "{}") if isinstance(fn, dict) else "{}"
            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

            result = await _dispatch_mcp(name, parsed_args)

            # Surface the tool's Prefab card. FastMCP normalises a PrefabApp to
            # the prefab_ui wire dict on structured_content, which client.py
            # exposes as "_prefab".
            if isinstance(result, dict):
                prefab = result.get("_prefab")
                if prefab:
                    prefabs.append({"tool": name, "prefab": prefab})

            # Feed the model the domain data only: the Prefab tree is UI, not
            # information, and runs to several KB per card - pure context waste.
            llm_view = {k: v for k, v in result.items() if k != "_prefab"} if isinstance(result, dict) else result
            result_str = json.dumps(llm_view, default=str, ensure_ascii=False)
            if len(result_str) > 4000:
                result_str = result_str[:4000] + "\n... (truncated)"
            ctx.append({"role": "tool", "content": result_str, "tool_call_id": tc.get("id", ""), "name": name})

    last_msg = _extract_message(await _llm_call(ctx, model, url, provider=provider))
    return {
        "message": {
            "role": "assistant",
            "content": _extract_content(last_msg) or "I need more specific information.",
        },
        "prefabs": prefabs,
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

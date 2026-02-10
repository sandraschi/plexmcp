"""LLM API for chat, prompt refine, and workflows (Ollama / OpenAI-compatible)."""

import logging
import os

import httpx
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"


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
            r = await client.get(f"{url.rstrip('/')}/models", headers=headers or None)
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
    model: str = Body("llama3.2"),
    stream: bool = Body(False),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
):
    """Chat completion. Supports streaming."""
    url = _get_base_url(provider, base_url)
    if ":11434" in url or "ollama" in url.lower():
        req_url = f"{url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": stream}
        if stream:

            async def _stream():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream("POST", req_url, json=payload) as resp:
                        async for chunk in resp.aiter_text():
                            yield chunk

            return StreamingResponse(_stream(), media_type="text/event-stream")
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(req_url, json=payload)
            if r.status_code != 200:
                return {"error": r.text, "status": r.status_code}
            return r.json()
    req_url = f"{url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {"model": model, "messages": messages, "stream": stream}
    if stream:

        async def _stream_openai():
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", req_url, json=payload, headers=headers) as resp:
                    async for chunk in resp.aiter_text():
                        yield chunk

        return StreamingResponse(_stream_openai(), media_type="text/event-stream")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(req_url, json=payload, headers=headers)
        if r.status_code != 200:
            return {"error": r.text, "status": r.status_code}
        return r.json()


@router.post("/refine")
async def refine_prompt(
    body: dict = Body(...),
):
    """Use LLM to refine/improve a user message (e.g. before sending to chat)."""
    text = body.get("text", "") or ""
    model = body.get("model", "llama3.2")
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
    req_url = f"{url}/chat/completions"
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

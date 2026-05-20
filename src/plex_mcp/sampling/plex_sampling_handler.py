# MIT License
#
# Copyright (c) 2025 OCR-MCP Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
#
#
#
#

"""
PlexMCP sampling for FastMCP 3.1 (server-side OpenAI-compatible chat/completions).

FastMCP invokes the handler as::

    await handler(messages, SamplingParams, request_context)

**Default:** local **Ollama** at ``http://127.0.0.1:11434/v1`` (see
``PLEX_SAMPLING_BASE_URL``), or derive from ``LLM_BASE_URL``. No API key on
loopback / RFC1918 LAN.

Set ``PLEX_SAMPLING_USE_CLIENT_LLM=1`` so the MCP host performs sampling instead.

Cloud endpoints: set ``PLEX_SAMPLING_API_KEY`` (or reuse ``OPENAI_API_KEY`` when
documented for your provider).
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import httpx
from mcp.shared.context import RequestContext
from mcp.types import (
    CreateMessageRequestParams as SamplingParams,
)
from mcp.types import (
    CreateMessageResult,
    CreateMessageResultWithTools,
    ImageContent,
    SamplingMessage,
    TextContent,
    Tool,
    ToolResultContent,
    ToolUseContent,
)

from .plex_sampling_config import PlexSamplingConfig

if TYPE_CHECKING:
    from mcp.server.session import ServerSession

logger = logging.getLogger(__name__)


def _sampling_allows_empty_api_key(base_url: str) -> bool:
    """Ollama and similar local servers often need no Bearer token."""
    try:
        parsed = urlparse(base_url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if host in ("127.0.0.1", "localhost", "::1"):
        return True
    if host.startswith("192.168."):
        return True
    if host.startswith("10."):
        return True
    if host.startswith("172."):
        parts = host.split(".")
        if len(parts) >= 2 and parts[0] == "172":
            try:
                second = int(parts[1])
            except ValueError:
                return False
            if 16 <= second <= 31:
                return True
    return False


def _sampling_http_enabled(api_key: str | None, base_url: str) -> bool:
    return bool(api_key and api_key.strip()) or _sampling_allows_empty_api_key(base_url)


def _hint_model(params: SamplingParams, default: str) -> str:
    mp = params.modelPreferences
    if mp is None:
        return default
    hints = getattr(mp, "hints", None) or []
    for h in hints:
        name = getattr(h, "name", None)
        if name:
            return name
    return default


def _tool_choice_openai(tc: Any | None) -> str | dict[str, Any]:
    if tc is None:
        return "auto"
    mode = getattr(tc, "mode", None)
    if mode == "required":
        return "required"
    if mode == "none":
        return "none"
    return "auto"


def _mcp_tools_to_openai(tools: list[Tool] | None) -> list[dict[str, Any]] | None:
    if not tools:
        return None
    out: list[dict[str, Any]] = []
    for t in tools:
        out.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or f"MCP tool {t.name}",
                    "parameters": (t.inputSchema if isinstance(t.inputSchema, dict) else {"type": "object"}),
                },
            }
        )
    return out


def _serialize_tool_result(tr: ToolResultContent) -> str:
    if tr.structuredContent is not None:
        try:
            return json.dumps(tr.structuredContent, ensure_ascii=False)[:80000]
        except (TypeError, ValueError):
            return str(tr.structuredContent)[:80000]
    parts: list[str] = []
    for block in tr.content:
        if isinstance(block, TextContent):
            parts.append(block.text)
        elif isinstance(block, ImageContent):
            parts.append("[image]")
        else:
            parts.append(str(block))
    body = "\n".join(parts).strip()
    if tr.isError:
        return f"[tool error] {body}" if body else "[tool error]"
    return body if body else "(empty tool result)"


def _sampling_messages_to_openai(
    messages: list[SamplingMessage],
    system_prompt: str | None,
) -> list[dict[str, Any]]:
    """Map MCP sampling history to OpenAI-style chat messages."""
    out: list[dict[str, Any]] = []
    if system_prompt:
        out.append({"role": "system", "content": system_prompt})

    for msg in messages:
        blocks = msg.content_as_list
        if msg.role == "user":
            tool_results = [b for b in blocks if isinstance(b, ToolResultContent)]
            texts = [b for b in blocks if isinstance(b, TextContent)]
            non_text = [b for b in blocks if not isinstance(b, TextContent | ToolResultContent)]
            for tr in tool_results:
                out.append(
                    {
                        "role": "tool",
                        "tool_call_id": tr.toolUseId,
                        "content": _serialize_tool_result(tr),
                    }
                )
            if texts:
                joined = "\n".join(t.text for t in texts).strip()
                if joined:
                    out.append({"role": "user", "content": joined})
            for b in non_text:
                out.append(
                    {
                        "role": "user",
                        "content": f"[unsupported block in fallback handler: {type(b).__name__}]",
                    }
                )
        elif msg.role == "assistant":
            tool_uses = [b for b in blocks if isinstance(b, ToolUseContent)]
            texts = [b for b in blocks if isinstance(b, TextContent)]
            non_text = [b for b in blocks if not isinstance(b, TextContent | ToolUseContent)]
            if tool_uses:
                tool_calls = []
                for tu in tool_uses:
                    args = tu.input
                    arg_str = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
                    tool_calls.append(
                        {
                            "id": tu.id or str(uuid.uuid4()),
                            "type": "function",
                            "function": {"name": tu.name, "arguments": arg_str},
                        }
                    )
                text_part = "\n".join(t.text for t in texts).strip() or None
                row: dict[str, Any] = {
                    "role": "assistant",
                    "tool_calls": tool_calls,
                }
                if text_part:
                    row["content"] = text_part
                else:
                    row["content"] = None
                out.append(row)
            else:
                joined = "\n".join(t.text for t in texts).strip()
                out.append({"role": "assistant", "content": joined})
            for b in non_text:
                out.append(
                    {
                        "role": "assistant",
                        "content": f"[unsupported block: {type(b).__name__}]",
                    }
                )
    return out


def _plex_degraded_response_text(user_text: str, has_tools: bool) -> str:
    """Actionable guidance when no HTTP LLM is reachable (no fake LLM output)."""
    _ = user_text
    tool_note = (
        "Start **Ollama** (`ollama serve`), `ollama pull` your model, set "
        "**PLEX_SAMPLING_BASE_URL** (default http://127.0.0.1:11434/v1) and **PLEX_SAMPLING_MODEL**, "
        "or align **LLM_BASE_URL** with the webapp. "
        "Alternatively set **PLEX_SAMPLING_USE_CLIENT_LLM=1** so the MCP host runs sampling."
        if has_tools
        else (
            "Start **Ollama** or point **PLEX_SAMPLING_BASE_URL** at your LAN inference server. "
            "Localhost / private LAN typically needs no API key. "
            "Or set **PLEX_SAMPLING_USE_CLIENT_LLM=1** for host-side sampling."
        )
    )
    return (
        "[PlexMCP sampling — HTTP LLM unreachable]\n\n"
        f"{tool_note}\n\n"
        "Portmanteau tools still work without sampling: plex_library, plex_media, plex_search, "
        "plex_streaming, plex_rag (after sync_metadata). "
        "For multi-step LLM orchestration, fix the endpoint then call **agentic_plex_workflow**."
    )


class PlexSamplingHandler:
    """
    OpenAI-compatible chat/completions (default: local Ollama).

    Callable as ``(messages, params, request_context)`` per FastMCP.
    """

    def __init__(self, config: PlexSamplingConfig | None = None) -> None:
        self.config = config or PlexSamplingConfig.from_env()
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        messages: list[SamplingMessage],
        params: SamplingParams,
        request_context: RequestContext[ServerSession, Any],
    ) -> CreateMessageResult | CreateMessageResultWithTools | str:
        _ = request_context  # reserved for tracing / future use
        cfg = self.config
        api_key = cfg.sampling_api_key
        base_url = cfg.sampling_base_url.rstrip("/")
        default_model = cfg.sampling_model or "llama3.2"
        model = _hint_model(params, default_model)
        max_tokens = params.maxTokens
        temperature = params.temperature
        sdk_tools = params.tools
        has_tools = bool(sdk_tools)

        openai_messages = _sampling_messages_to_openai(messages, params.systemPrompt)
        if not _sampling_http_enabled(api_key, base_url):
            last_user = ""
            for m in reversed(messages):
                if m.role == "user":
                    for b in m.content_as_list:
                        if isinstance(b, TextContent):
                            last_user = b.text
                            break
                    if last_user:
                        break
            text = _plex_degraded_response_text(last_user, has_tools)
            if has_tools:
                return CreateMessageResultWithTools(
                    role="assistant",
                    model="none",
                    content=TextContent(type="text", text=text),
                    stopReason="endTurn",
                )
            return CreateMessageResult(
                role="assistant",
                model="none",
                content=TextContent(type="text", text=text),
                stopReason="endTurn",
            )

        url = f"{base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        oa_tools = _mcp_tools_to_openai(sdk_tools)
        if oa_tools:
            payload["tools"] = oa_tools
            payload["tool_choice"] = _tool_choice_openai(params.toolChoice)

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key.strip()}"
        oa_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if "openai.com" in base_url.lower() and oa_key and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {oa_key}"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPStatusError as e:
            err_body = ""
            try:
                err_body = e.response.text[:2000]
            except Exception as ex:
                self.logger.debug("Could not read error body: %s", ex)
            msg = (
                f"[PlexMCP sampling] HTTP {e.response.status_code} from {url}. "
                f"Check Ollama or LM Studio, PLEX_SAMPLING_MODEL is available, URL/base path, "
                f"and API key if using a cloud endpoint. Body: {err_body}"
            )
            self.logger.warning(msg)
            return CreateMessageResult(
                role="assistant",
                model=model,
                content=TextContent(type="text", text=msg),
                stopReason="endTurn",
            )
        except Exception as e:
            msg = f"[PlexMCP sampling] Request failed: {e!s}"
            self.logger.exception("Sampling fallback failed")
            return CreateMessageResult(
                role="assistant",
                model=model,
                content=TextContent(type="text", text=msg),
                stopReason="endTurn",
            )

        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        finish = (choice.get("finish_reason") or "stop") or "stop"
        tool_calls = msg.get("tool_calls") or []
        content_text = msg.get("content") or ""

        if tool_calls:
            blocks: list[TextContent | ToolUseContent] = []
            if isinstance(content_text, str) and content_text.strip():
                blocks.append(TextContent(type="text", text=content_text))
            for tc in tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name") or "unknown_tool"
                raw_args = fn.get("arguments") or "{}"
                try:
                    parsed: Any = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    if not isinstance(parsed, dict):
                        parsed = {"value": parsed}
                except json.JSONDecodeError:
                    parsed = {"_raw": raw_args}
                tid = tc.get("id") or str(uuid.uuid4())
                blocks.append(ToolUseContent(type="tool_use", name=name, id=tid, input=parsed))
            return CreateMessageResultWithTools(
                role="assistant",
                model=str(data.get("model") or model),
                content=blocks,
                stopReason="toolUse",
            )

        if isinstance(content_text, list):
            # Some APIs return multipart content
            text_parts = []
            for part in content_text:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text") or "")
                else:
                    text_parts.append(str(part))
            content_text = "\n".join(text_parts)

        stop_reason = "endTurn"
        if finish in ("length", "max_tokens", "maxTokens"):
            stop_reason = "maxTokens"
        return CreateMessageResult(
            role="assistant",
            model=str(data.get("model") or model),
            content=TextContent(type="text", text=str(content_text)),
            stopReason=stop_reason,
        )

    async def check_health(self) -> dict[str, Any]:
        cfg = self.config
        base = cfg.sampling_base_url.rstrip("/") if cfg else ""
        key = cfg.sampling_api_key if cfg else None
        model = cfg.sampling_model if cfg else None
        http_ok = _sampling_http_enabled(key, base) if base else bool(key and str(key).strip())
        return {
            "status": "healthy",
            "server_side_llm_configured": http_ok,
            "sampling_base_url": base or None,
            "sampling_fallback_model": model,
            "config_loaded": cfg is not None,
        }

    def get_available_models(self) -> list[str]:
        """Configured sampling model when HTTP LLM is enabled (local or cloud)."""
        if not self.config:
            return []
        base = self.config.sampling_base_url.rstrip("/")
        key = self.config.sampling_api_key
        if not _sampling_http_enabled(key, base):
            return []
        return [self.config.sampling_model or "llama3.2"]

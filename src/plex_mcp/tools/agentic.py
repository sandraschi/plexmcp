"""
FastMCP 3.1 — SEP-1577 agentic tools for PlexMCP.

Uses Context.sample_step (tools) and Context.sample (single-turn text). Requires
sampling support (local Ollama via PlexSamplingHandler or client-side sampling).
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import Context

logger = logging.getLogger(__name__)


def _ok(**kwargs: Any) -> dict[str, Any]:
    return {
        "success": True,
        "operation": kwargs.get("operation", "unknown"),
        "message": kwargs.get("message", ""),
        "result": kwargs.get("result", {}),
        "recommendations": kwargs.get("recommendations", []),
    }


def _err(
    *,
    error: str,
    error_code: str,
    message: str,
    recovery_options: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "error": error,
        "error_code": error_code,
        "message": message,
        "recovery_options": recovery_options or [],
    }


def register_agentic_plex_tools(app: Any) -> None:
    """Register real sampling-based tools on the FastMCP app."""

    @app.tool()
    async def agentic_plex_workflow(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int = 8,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """
        Multi-step Plex workflows via FastMCP sampling with tool execution (SEP-1577).

        The model chooses plex_* tool calls; the server runs them and feeds results back
        until the model returns a final text answer or max_iterations is reached.

        Args:
            workflow_prompt: Natural-language goal (e.g. "List movie libraries, then search for Nolan films").
            available_tools: Tool names registered on this server (e.g. plex_library, plex_search, plex_media).
            max_iterations: Maximum sample_step rounds (default 8).

        Returns:
            success, result with final_output, iterations, executed_tools, or structured error.
        """
        if not workflow_prompt.strip():
            return _err(
                error="Missing workflow_prompt",
                error_code="MISSING_PROMPT",
                message="workflow_prompt is required",
                recovery_options=["Describe the Plex task in natural language"],
            )
        if not available_tools:
            return _err(
                error="No tools specified",
                error_code="EMPTY_TOOLS",
                message="available_tools must name at least one registered tool",
                recovery_options=[
                    "Example: ['plex_library', 'plex_search', 'plex_media']",
                ],
            )
        if context is None:
            return _err(
                error="No MCP context",
                error_code="NO_CONTEXT",
                message="Agentic workflow requires a FastMCP Context (run from an MCP client)",
                recovery_options=["Invoke this tool from a client that passes Context"],
            )
        if not hasattr(context, "sample_step"):
            return _err(
                error="Sampling unavailable",
                error_code="SAMPLING_UNAVAILABLE",
                message="Context has no sample_step (need FastMCP 3.1+ with sampling)",
                recovery_options=[
                    "Install fastmcp>=3.1",
                    "Configure PLEX_SAMPLING_BASE_URL / Ollama or PLEX_SAMPLING_USE_CLIENT_LLM=1",
                ],
            )

        try:
            all_tools = await app.list_tools()
        except Exception as e:
            logger.exception("list_tools failed")
            return _err(
                error="list_tools failed",
                error_code="LIST_TOOLS_FAILED",
                message=str(e),
                recovery_options=["Check server logs"],
            )

        name_to_tool = {t.name: t for t in all_tools if getattr(t, "name", None)}
        tools_for_sampling = [name_to_tool[n] for n in available_tools if n in name_to_tool]
        missing = [n for n in available_tools if n not in name_to_tool]
        if missing:
            logger.warning("agentic_plex_workflow: unknown tool names: %s", missing)
        if not tools_for_sampling:
            return _err(
                error="No matching tools",
                error_code="TOOLS_NOT_FOUND",
                message=f"None of available_tools matched. Registered include: {sorted(name_to_tool.keys())[:40]}",
                recovery_options=["Use exact portmanteau names: plex_library, plex_media, plex_search, ..."],
            )

        system_prompt = (
            "You are a Plex Media Server assistant with access to the listed tools only. "
            "Call tools to inspect libraries, browse or search media, sessions, users, etc. "
            "When done, reply with a concise summary for the user and any follow-up suggestions."
        )
        messages: list = [{"role": "user", "content": workflow_prompt}]
        executed_tools: list[str] = []
        iterations = 0
        step: Any = None

        while iterations < max_iterations:
            iterations += 1
            logger.info("agentic_plex_workflow step %s/%s", iterations, max_iterations)
            step = await context.sample_step(
                messages,
                system_prompt=system_prompt,
                tools=tools_for_sampling,
                execute_tools=True,
                max_tokens=4096,
            )
            if hasattr(step, "history") and step.history:
                messages = list(step.history)
            if hasattr(step, "tool_calls") and step.tool_calls:
                for tc in step.tool_calls:
                    name = getattr(tc, "name", None) or getattr(tc, "tool_name", str(tc))
                    if name:
                        executed_tools.append(str(name))
            is_tool_use = getattr(step, "is_tool_use", True)
            if not is_tool_use:
                final_text = getattr(step, "text", "") or ""
                return _ok(
                    operation="agentic_plex_workflow",
                    message="Workflow completed.",
                    result={
                        "final_output": final_text,
                        "iterations": iterations,
                        "executed_tools": list(dict.fromkeys(executed_tools)),
                        "missing_tool_names": missing,
                    },
                    recommendations=["Narrow available_tools for faster runs or raise max_iterations."],
                )

        return _ok(
            operation="agentic_plex_workflow",
            message="Stopped at max_iterations without a final non-tool reply.",
            result={
                "final_output": getattr(step, "text", "") if step else "",
                "iterations": iterations,
                "executed_tools": list(dict.fromkeys(executed_tools)),
                "missing_tool_names": missing,
            },
            recommendations=["Increase max_iterations or simplify the workflow_prompt."],
        )

    @app.tool()
    async def plex_natural_assistant(
        user_query: str,
        context: Context | None = None,
        detail_level: str = "standard",
    ) -> dict[str, Any]:
        """
        Single-turn natural-language help about Plex (sampling, no tool execution).

        Uses the configured sampling endpoint (Ollama / client). For actions that
        change server state or need live data, use portmanteau tools or agentic_plex_workflow.

        Args:
            user_query: User question.
            detail_level: brief | standard | detailed — adjusts system instructions.

        Returns:
            success and assistant reply text, or structured error.
        """
        if not user_query.strip():
            return _err(
                error="Empty query",
                error_code="EMPTY_QUERY",
                message="user_query is required",
            )
        if context is None or not hasattr(context, "sample"):
            return _err(
                error="Sampling unavailable",
                error_code="SAMPLING_UNAVAILABLE",
                message="plex_natural_assistant requires Context.sample (FastMCP 3.1+)",
                recovery_options=["Configure PLEX_SAMPLING_* or use portmanteau tools directly"],
            )

        level = (detail_level or "standard").lower()
        if level == "brief":
            sys = "You are a concise Plex Media Server expert. Answer in short bullets. If unsure, say what info you need."
        elif level == "detailed":
            sys = (
                "You are an expert on Plex Media Server: libraries, agents, transcoding, "
                "remote access, users, and discovery. Give structured, accurate answers. "
                "If the user needs live server data, say they should use MCP tools (plex_library, plex_search, etc.)."
            )
        else:
            sys = (
                "You are a helpful Plex Media Server assistant. Be clear and accurate. "
                "For live library or playback data, remind the user that tools like plex_library "
                "or plex_search must be used via the agentic workflow or client."
            )

        try:
            result = await context.sample(
                user_query.strip(),
                system_prompt=sys,
                max_tokens=2048,
            )
            text = getattr(result, "text", None) or str(result)
            return _ok(
                operation="plex_natural_assistant",
                message=text,
                result={"reply": text, "detail_level": level},
                recommendations=[
                    "For real library/search data, call agentic_plex_workflow with plex_* tools.",
                ],
            )
        except Exception as e:
            logger.exception("plex_natural_assistant failed")
            return _err(
                error="Sampling failed",
                error_code="SAMPLING_FAILED",
                message=str(e),
                recovery_options=["Verify Ollama or PLEX_SAMPLING_BASE_URL", "See server logs"],
            )

# plexmcp — Claude Code Guide

## Overview
SOTA April 2026 industrialized FastMCP 3.2.0 server for Plex Media Server management with conversational AI, sampling, and agentic workflows

## Entry Points
- `uv run plex-mcp` → `plex_mcp.server:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `AGENTS.md` — OpenAI Codex agent context (if present)

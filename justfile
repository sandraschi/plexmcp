# PlexMCP — fleet tasks (https://github.com/casey/just)
# Windows: install `just` and `uv`; run from repo root.

set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @just --list

# Resolve and write uv.lock from pyproject.toml
lock:
    uv lock

# Install project + deps from uv.lock
sync:
    uv sync

# MCP server (transport from env: MCP_TRANSPORT=stdio|http, default stdio via CLI in transport)
run:
    uv run python -m plex_mcp.server

# Lint
lint:
    uv run ruff check src tests

# Format
fmt:
    uv run ruff format src tests

# Tests (clear pytest addopts so cov extras are not required)
test:
    uv run pytest tests -q --override-ini "addopts="

# Lint + test
check: lint test

# FastAPI backend + Next.js frontend (ports 10740 / 10741)
webapp:
    powershell -NoProfile -ExecutionPolicy Bypass -File webapp/start.ps1

# Optional: Claude Desktop .mcpb (requires mcpb CLI)
pack-mcpb:
    mcpb pack . dist/plex-mcp.mcpb

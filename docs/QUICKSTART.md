# Quick start (~60 seconds)

Assumes **Plex Media Server** is already running and you have an [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/). More detail: [PLEX.md](PLEX.md) · full install: [INSTALL.md](INSTALL.md).

---

## A — MCP only (agents / Cursor / Claude Desktop)

1. `git clone https://github.com/sandraschi/plex-mcp.git` then `cd plex-mcp`
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then `uv sync`
3. Set `PLEX_TOKEN` and `PLEX_URL` (often `http://127.0.0.1:32400`)
4. Run: `uv run plex-mcp-advanced`
5. Point your MCP client at **stdio** for that process

Done. Next: [TOOLS.md](TOOLS.md) · [CONFIGURATION.md](CONFIGURATION.md)

---

## B — Browser UI (dashboard, search, chat)

1. Do **A** through `uv sync` (same repo, same env vars)
2. `cd webapp` — set `webapp/backend/.env` with at least `PLEX_TOKEN` and `PLEX_URL` (see [WEBAPP.md](WEBAPP.md))
3. `powershell -ExecutionPolicy Bypass -File .\start.ps1`
4. Open **http://127.0.0.1:10741** — API docs: **http://127.0.0.1:10740/docs**

Done. Next: [WEBAPP.md](WEBAPP.md) · [SELF_HOSTING.md](SELF_HOSTING.md) before exposing to the internet

---

## C — Semantic search (RAG)

Optional. Requires extra `PYTHONPATH` setup for shared vector code — [RAG.md](RAG.md). Paths **A** and **B** work without RAG.

---

## Video walkthrough

No official video yet. This page plus [WEBAPP.md](WEBAPP.md) are the best quick references. (If a narrated tour is published later, it will be linked from here.)

## Stuck?

[TROUBLESHOOTING.md](TROUBLESHOOTING.md) (diagnostic order at the top) · [documentation hub](README.md) · [ops todo / roadmap](plans/OPERATIONAL_IMPROVEMENTS.md)

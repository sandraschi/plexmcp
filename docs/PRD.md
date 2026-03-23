# PlexMCP — product requirements

**Package:** `plex-mcp-advanced` · **Framework:** FastMCP **3.1+** · **Python:** **3.12+**  
**Status:** Alpha — see [CHANGELOG.md](../CHANGELOG.md) and root [README.md](../README.md).

## Purpose

Provide a **Model Context Protocol** server for **Plex Media Server** so AI assistants (Claude, Cursor, fleet tools) can query libraries, search media, inspect server health, manage playlists and users (where APIs allow), and optionally run **semantic search** over indexed metadata and **agentic** flows with sampling.

## In scope

| Area | Requirement |
|------|-------------|
| **MCP** | Portmanteau tools (`operation` + typed args), structured success/error payloads, stdio; HTTP app for inspector / fleet. |
| **Plex** | Libraries, media browse/search, server status, sessions/clients, playlists, users, reporting, metadata refresh patterns supported by `plexapi` / Plex HTTP API. |
| **Sampling** | Server-side OpenAI-compatible LLM (`PLEX_SAMPLING_*`) for `plex_natural_assistant` and `agentic_plex_workflow` when the host does not sample; optional client LLM via `PLEX_SAMPLING_USE_CLIENT_LLM=1`. |
| **RAG** | `plex_rag`: LanceDB index from Plex metadata (`sync_metadata`, `semantic_search`); optional bridge to **mcp-central-docs** `docs_mcp.backend.rag_core` when on `PYTHONPATH`. |
| **Webapp** | FastAPI backend (**10740**) + Next.js frontend (**10741**): dashboard, libraries, movies, keyword + semantic search, chat with preprompt, settings (Plex, LLM, *arr). FastMCP mounted at **`/mcp`**. |
| ***arr** | Read-only HTTP status for Radarr / Sonarr / Lidarr when URLs and API keys are configured (`arr_stack` + UI cards). |
| **Install** | **uv**-first workflow; `uv.exe` on PATH (Windows). **PyPI** install documented as **conditional** until the package is published there. |

## Out of scope / known gaps

- **Playback control** (`plex_streaming` play/pause/stop): **not reliable** across client types; treat as best-effort / diagnostic only until Plex client APIs behave consistently. See [CHANGELOG.md](../CHANGELOG.md) Known Issues.
- **PyPI one-liner** as the only install path: blocked until **PyPI registration** and release are complete; repo + `uv sync` remains primary.

## Non-functional

- Lint/format: **Ruff**; tests: **pytest** (see [DEVELOPMENT.md](DEVELOPMENT.md)).
- Ports: webapp **10740** / **10741** per fleet [WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/operations/WEBAPP_PORTS.md).
- Secrets: `.env` / `webapp/backend/data/settings.json` — not committed.

## References

- [INSTALL.md](INSTALL.md) · [CONFIGURATION.md](CONFIGURATION.md) · [TOOLS.md](TOOLS.md) · [RAG.md](RAG.md) · [WEBAPP.md](WEBAPP.md) · [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [webapp/README.md](../webapp/README.md) · [webapp/SETUP.md](../webapp/SETUP.md)

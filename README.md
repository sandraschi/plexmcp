<div align="center">

# PlexMCP

**Talk to your library.** An open [Model Context Protocol](https://modelcontextprotocol.io/) server for [Plex Media Server](https://www.plex.tv/) — plus an optional glass-style web app for browsing, search, and chat.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-0c4a6e?style=flat-square)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.2-6366f1?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Quick start](docs/QUICKSTART.md) · [Install](docs/INSTALL.md) · [Web app](docs/WEBAPP.md) · [All docs](docs/README.md) · [Changelog](CHANGELOG.md)

</div>

---

## Why PlexMCP?

| You want… | PlexMCP gives you… |
|-----------|---------------------|
| **Agents that “see” your Plex** | MCP tools for libraries, media, search, playlists, playback helpers, server health |
| **Semantic search over your titles** | Optional RAG (`plex_rag`) when vector dependencies are configured |
| **A real UI** | FastAPI + Next.js web app — libraries, movies, keyword + semantic search, chat, settings |
| **One server, many clients** | stdio for Claude / Cursor; HTTP + `/mcp` when using the bundled backend |

---

## Quick start (MCP over stdio)

```powershell
git clone https://github.com/sandraschi/plex-mcp.git
cd plex-mcp
uv sync
$env:PLEX_TOKEN = "your-x-plex-token"
$env:PLEX_URL = "http://127.0.0.1:32400"
uv run plex-mcp-advanced
```

Point your MCP client at that process. **Even shorter path** → [docs/QUICKSTART.md](docs/QUICKSTART.md). **Tokens, URLs, and clients** → [docs/INSTALL.md](docs/INSTALL.md).

**Browser UI** → [docs/WEBAPP.md](docs/WEBAPP.md) (ports **10740** / **10741**).

---

## Documentation map

| Read this… | When you care about… |
|------------|------------------------|
| [**docs/README.md**](docs/README.md) | **Hub** — every guide in one place |
| [**docs/QUICKSTART.md**](docs/QUICKSTART.md) | **~60s** — MCP only, web UI, RAG pointer |
| [**docs/INSTALL.md**](docs/INSTALL.md) | uv, clone, run, Claude Desktop |
| [**docs/PLEX.md**](docs/PLEX.md) | What Plex is, tokens, remote access (plain language) |
| [**docs/ARCHITECTURE.md**](docs/ARCHITECTURE.md) | How the MCP server, backend, and UI fit together |
| [**docs/SELF_HOSTING.md**](docs/SELF_HOSTING.md) | Home lab: HTTPS, reverse proxy, secrets, hardening |
| [**docs/DOCKER.md**](docs/DOCKER.md) | Optional Docker Compose example |
| [**docs/CONFIGURATION.md**](docs/CONFIGURATION.md) | Environment variables, sampling, RAG, *arr |
| [**docs/TOOLS.md**](docs/TOOLS.md) | Tool surface (portmanteaus and what they do) |
| [**docs/WEBAPP.md**](docs/WEBAPP.md) | Web app ports, startup, feature pointers |
| [**docs/RAG.md**](docs/RAG.md) | Semantic search and indexing |
| [**docs/ENRICHMENT.md**](docs/ENRICHMENT.md) | Wikipedia-style enrichment |
| [**docs/TROUBLESHOOTING.md**](docs/TROUBLESHOOTING.md) | Auth, connection, RAG, common errors |
| [**docs/DEVELOPMENT.md**](docs/DEVELOPMENT.md) | Tests, lint, layout for contributors |
| [**docs/PRD.md**](docs/PRD.md) | Product scope and constraints |
| [**docs/plans/OPERATIONAL_IMPROVEMENTS.md**](docs/plans/OPERATIONAL_IMPROVEMENTS.md) | **Phased doc/DX/ops todo** (checklist) |
| [**docs/plans/ROADMAP.md**](docs/plans/ROADMAP.md) | Feature specs and product roadmap |

---

## Stack (at a glance)

Python **3.12+** · **FastMCP** 3.2 · **plexapi** · optional **LanceDB** RAG (see [docs/RAG.md](docs/RAG.md) for `PYTHONPATH` notes) · web app **FastAPI** + **Next.js**

---

## License & credits

**MIT** — [LICENSE](LICENSE).  
[Plex](https://www.plex.tv/), [FastMCP](https://github.com/jlowin/fastmcp), and contributors.

Fleet standards cross-link: [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) (e.g. [SOTA requirements](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/SOTA_REQUIREMENTS.md)).

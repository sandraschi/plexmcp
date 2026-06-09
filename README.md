<div align="center">

# PlexMCP

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

**Talk to your library.** An open [Model Context Protocol](https://modelcontextprotocol.io/) server for [Plex Media Server](https://www.plex.tv/) — plus an optional glass-style web app for browsing, search, and chat.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-0c4a6e?style=flat-square)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.2-6366f1?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Quick start](docs/QUICKSTART.md) · [Install](docs/INSTALL.md) · [Web app](docs/WEBAPP.md) · [All docs](docs/README.md) · [Changelog](CHANGELOG.md)

</div>

---

## Quick Start

Download **`Plex MCP_*_x64-setup.exe`** from [Releases](https://github.com/sandraschi/plex-mcp/releases/latest) → double-click → launch **Plex MCP**. [Install guide](docs/INSTALL.md).

Developers from source:

```powershell
git clone https://github.com/sandraschi/plex-mcp
cd plex-mcp
just install
just webapp
```

## Documentation map

| Read this… | When you care about… |
|------------|------------------------|
| [**docs/README.md**](docs/README.md) | **Hub** — every guide in one place |
| [**docs/QUICKSTART.md**](docs/QUICKSTART.md) | **~60s** — MCP only, web UI, RAG pointer |
| [**docs/INSTALL.md**](docs/INSTALL.md) | Tauri desktop (primary), uv, clone, MCPB, Claude Desktop |
| [**docs/TAURI.md**](docs/TAURI.md) | Maintainer: build installer, production pitfalls |
| [**docs/DOCUMENTATION_INDEX.md**](docs/DOCUMENTATION_INDEX.md) | Full doc map + archival paths |
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

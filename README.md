<div align="center">

# PlexMCP

**FastMCP 3.2 MCP server for Plex Media Server**  portmanteau tools, optional sampling and agentic workflows, optional RAG, universal connect pattern support, and a glassmorphism webapp (FastAPI + Next.js).

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.2+](https://img.shields.io/badge/FastMCP-3.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Installation](docs/INSTALL.md)  [Configuration](docs/CONFIGURATION.md)  [Tools](docs/TOOLS.md)  [Webapp](docs/WEBAPP.md)  [RAG](docs/RAG.md)

</div>

---

> **Alpha**  APIs and behavior may change. See [CHANGELOG.md](CHANGELOG.md) (Unreleased) and [docs/PRD.md](docs/PRD.md) for scope and shipped features.

## Table of contents

- [What you get](#what-you-get)
- [Quick start](#quick-start)
- [Documentation](#documentation)
- [License](#license)

## What you get

- **MCP tools**  Plex libraries, media, search, playlists, streaming/session helpers, server health, reporting, optional *arr read-only status, RAG (`plex_rag`), `agentic_plex_workflow`, `plex_natural_assistant` (sampling).
- **Webapp**  Dashboard, libraries, movies, keyword + semantic search, chat (local LLM), settings (Plex, LLM, *arr). Backend **10740**, frontend **10741**; MCP at `/mcp` on the backend.
- **Universal Connect**  FastMCP 3.2+ support for simultaneous stdio + HTTP access from multiple clients.
- **Stack**  `plexapi`, LanceDB + embeddings for RAG (requires shared `docs_mcp` vector code from [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) on `PYTHONPATH`).

## Quick start

### Prerequisites
- Python 3.12+
- Plex Media Server running
- Plex authentication token

### Installation

```powershell
# Clone and setup
git clone https://github.com/sandraschi/plex-mcp.git
cd plex-mcp
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

# Configure environment
copy .env.example .env
# Edit .env with your Plex token and URL
```

### Environment Setup

Create `.env` file:
```env
# Plex server connection
PLEX_BASE_URL=http://localhost:32400
PLEX_TOKEN=your-x-plex-token

# Optional: LLM sampling (Ollama recommended)
PLEX_SAMPLING_USE_CLIENT_LLM=1
# OR for server-side LLM:
# PLEX_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
# PLEX_SAMPLING_MODEL=llama3.2
```

### Start Server

**STDIO mode (Claude Desktop/MCP clients):**
```powershell
.venv\Scripts\python.exe -m plex_mcp.server --stdio
```

**HTTP mode (webapps):**
```powershell
.venv\Scripts\python.exe -m plex_mcp.server --http --port 10740
```

**Webapp (full UI):**
```powershell
.\start.ps1
```

### Verify Installation

```powershell
# Run test suite
.venv\Scripts\python.exe tests\test_server_startup.py

# Should show:  All tests passed! PlexMCP is ready.
```

Point Claude Desktop, Cursor, or any MCP client at that process (stdio). For the browser UI, see [docs/WEBAPP.md](docs/WEBAPP.md).

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/INSTALL.md](docs/INSTALL.md) | Clone, `uv`, PyPI, Claude Desktop |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Env vars, sampling, RAG, *arr, webapp overrides |
| [docs/TOOLS.md](docs/TOOLS.md) | Portmanteau tools overview |
| [docs/RAG.md](docs/RAG.md) | Semantic search dependency and indexing |
| [docs/WEBAPP.md](docs/WEBAPP.md) | Webapp ports and pointers |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Tests, lint, layout |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Auth, connection, RAG, *arr |
| [docs/PRD.md](docs/PRD.md) | Product scope (in/out), constraints |
| [docs/README.md](docs/README.md) | Documentation hub index |
| [webapp/README.md](webapp/README.md) | Full webapp feature list |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |

## License

MIT  see [LICENSE](LICENSE).

## Acknowledgments

[Plex](https://www.plex.tv/), [FastMCP](https://github.com/jlowin/fastmcp) 3.2.0+, and contributors.

## Stack:

Python 3.12+  [FastMCP](https://github.com/jlowin/fastmcp) 3.2.0+  FastAPI  React (`web_sota`)

# Documentation index (canonical)

**Start here:** [docs/README.md](README.md) — curated hub for **plex-mcp**.

Root overview and install: [README.md](../README.md), [INSTALL.md](INSTALL.md).

---

## Core (read these)

| Doc | Purpose |
|-----|---------|
| [QUICKSTART.md](QUICKSTART.md) | ~60s — MCP stdio, web UI, RAG pointer |
| [INSTALL.md](INSTALL.md) | Tauri desktop (primary), uv, MCPB, Claude Desktop |
| [TAURI.md](TAURI.md) | Maintainer build, ports, fleet Tauri pitfalls |
| [PLEX.md](PLEX.md) | Plex tokens, LAN vs remote |
| [ARCHITECTURE.md](ARCHITECTURE.md) | MCP vs backend vs Next.js |
| [CONFIGURATION.md](CONFIGURATION.md) | Environment variables, sampling, RAG |
| [TOOLS.md](TOOLS.md) | Portmanteau MCP tools |
| [WEBAPP.md](WEBAPP.md) | Browser UI (**10740** / **10741**) |
| [RAG.md](RAG.md) | LanceDB semantic search |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Auth, connection, RAG |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Tests, Ruff, Biome, Playwright |
| [PRD.md](PRD.md) | Product scope |

## Ecosystem & ops

| Doc | Purpose |
|-----|---------|
| [PLEX_ECOSYSTEM.md](PLEX_ECOSYSTEM.md) | Plex + *arr landscape |
| [ARR_SCENE.md](ARR_SCENE.md) | Radarr, Sonarr, Prowlarr |
| [SELF_HOSTING.md](SELF_HOSTING.md) | HTTPS, reverse proxy |
| [DOCKER.md](DOCKER.md) | Optional Compose example |
| [ENRICHMENT.md](ENRICHMENT.md) | Wikipedia-style enrichment |

## Sub-readmes (maintainers)

| Directory | Topic |
|-----------|--------|
| [mcp-technical/](mcp-technical/README.md) | Production checklist, FastMCP debugging, A2A fleet |
| [mcpb-packaging/](mcpb-packaging/README.md) | MCPB bundle |
| [development/](development/README.md) | Contributor notes |
| [glama-platform/](glama-platform/README.md) | Glama.ai catalog (historical) |
| [repository-protection/](repository-protection/README.md) | Branch protection, backups |
| [plans/](plans/ROADMAP.md) | Roadmap and operational todos |

---

## Stale or archival material

Do **not** treat these as plex-mcp source of truth:

| Path | Note |
|------|------|
| [notepadpp/](notepadpp/README.md) | Fleet import — Notepad++ editor reference, not PlexMCP API |
| [windsurf_assessment.md](windsurf_assessment.md) | Aug 2025 snapshot — superseded by current FastMCP 3.2 stack |
| [WINDSURF_IMPROVEMENTS_ASSESSMENT.md](WINDSURF_IMPROVEMENTS_ASSESSMENT.md) | Historical Windsurf notes |
| [COMPLETE_FIX_GUIDE.md](COMPLETE_FIX_GUIDE.md) | One-off fix log |
| [STATUS_REPORT_2025_11_03.md](STATUS_REPORT_2025_11_03.md) | Point-in-time status |
| [index.md](index.md), [installation.md](installation.md), [configuration.md](configuration.md), [development.md](development.md), [troubleshooting.md](troubleshooting.md) | Redirect stubs → UPPERCASE canonical files |

Fleet Tauri installer pitfalls: [mcp-central-docs TAURI_PRODUCTION_PITFALLS](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/TAURI_PRODUCTION_PITFALLS.md).

When in doubt: [README.md](../README.md) → [docs/README.md](README.md) → [TOOLS.md](TOOLS.md).

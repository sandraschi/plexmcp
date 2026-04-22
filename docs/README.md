# PlexMCP documentation

Everything below links from the [project README](../README.md). Pick a path by **what you are trying to do**.

---

## Start here

| Guide | Purpose |
|-------|---------|
| [**QUICKSTART.md**](QUICKSTART.md) | **~60 seconds** — MCP stdio, then optional web UI and RAG pointer |
| [**INSTALL.md**](INSTALL.md) | Install **uv**, clone the repo, set `PLEX_TOKEN` / `PLEX_URL`, run the MCP server, Claude Desktop |
| [**PLEX.md**](PLEX.md) | **Plain-language Plex** — what the server is, how tokens work, remote vs LAN |
| [**WEBAPP.md**](WEBAPP.md) | Start the **browser UI** (ports **10740** / **10741**), where features live |
| [**TROUBLESHOOTING.md**](TROUBLESHOOTING.md) | Auth errors, connection refused, RAG, *arr |

---

## Understand the system

| Guide | Purpose |
|-------|---------|
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | stdio MCP vs web backend vs Next.js — **diagram** and layout |
| [**CONFIGURATION.md**](CONFIGURATION.md) | All **environment variables**, sampling, RAG path, *arr, web overrides |
| [**TOOLS.md**](TOOLS.md) | **MCP tools** (portmanteaus, search, RAG, streaming, …) |

---

## Features in depth

| Guide | Purpose |
|-------|---------|
| [**RAG.md**](RAG.md) | Semantic search, LanceDB, indexing, `PYTHONPATH` |
| [**ENRICHMENT.md**](ENRICHMENT.md) | Wikipedia-style enrichment |
| [**PRD.md**](PRD.md) | Product scope — in / out of scope |

---

## Run it like a service

| Guide | Purpose |
|-------|---------|
| [**SELF_HOSTING.md**](SELF_HOSTING.md) | HTTPS, reverse proxy, secrets, Docker mental model |
| [**DOCKER.md**](DOCKER.md) | Optional **Docker Compose** example (API-focused; see repo root `docker-compose.example.yml`) |

---

## Contribute

| Guide | Purpose |
|-------|---------|
| [**DEVELOPMENT.md**](DEVELOPMENT.md) | Tests, Ruff, `just e2e` (Playwright), Semgrep vs optional Bandit/safety, repo layout |

---

## Other material

- [**plans/ROADMAP.md**](plans/ROADMAP.md) — product roadmap and feature specs  
- [**plans/OPERATIONAL_IMPROVEMENTS.md**](plans/OPERATIONAL_IMPROVEMENTS.md) — **concrete doc/DX/ops todo list** (phased checklist)  
- [**CHANGELOG.md**](../CHANGELOG.md) — release history  
- [**webapp/README.md**](../webapp/README.md) — UI feature list and API index  

Legacy and deep technical folders (`mcp-technical/`, `github/`, `glama-platform/`, …) still exist under `docs/` for maintainers; the table above is the **curated** user path.

- [**mcp-technical/README.md**](mcp-technical/README.md) — MCP server ops index (production checklist, debugging, **A2A fleet briefing**, [**A2A rollout plan**](mcp-technical/A2A_FLEET_ROLLOUT_PLAN.md) Plex → Calibre → Memory → supervisors)

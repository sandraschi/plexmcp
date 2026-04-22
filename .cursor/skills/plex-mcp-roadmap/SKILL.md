---
name: plex-mcp-roadmap
description: Master orchestration skill for implementing plex-mcp v2.5+ roadmap projects. Use when the user asks about building deep metadata enrichment, subtitle RAG, taste modelling, mood-based nightly picker, episode intelligence, or cross-library linking for plex-mcp. Directs work to the appropriate per-project SKILL and enforces shared conventions across all six projects.
---

# plex-mcp Roadmap — Orchestrator

You are implementing features for `plex-mcp`, a FastMCP 3.2 server
for Plex Media Server. Roadmap in `docs/plans/ROADMAP.md` with six
child projects in the same directory.

## Activate this skill when

The user asks to build any of:
- Deep metadata enrichment (Wikipedia + TMDB + Letterboxd + IMDB + RT + Metacritic + Criterion)
- Subtitle RAG (semantic search across all subtitles, with Whisper fallback)
- Taste modelling (user preference profile from watch history)
- Mood-based nightly picker (taste-aware "what to watch tonight")
- Episode intelligence (per-episode summaries, character arcs, "recap before watching")
- Cross-library linking (director/cast/adaptation/making-of pairs)

For any of these: read `docs/plans/ROADMAP.md`, then the
per-project spec, then use the matching per-project skill.

## Shared conventions

### Layout
- Main package: `src/plex_mcp/`
- Tools: `src/plex_mcp/tools/`
- Services: `src/plex_mcp/services/`
- RAG: `src/plex_mcp/rag/`
- Webapp backend: `webapp/backend/app/`
- Webapp frontend: `webapp/frontend/app/` (Next.js App Router)

### Ports (never change)
- Backend FastAPI + MCP HTTP: **10741**
- Frontend Next.js: **10742**
- Plex: 32400 (external)
- Ollama: 11434 (external)

### Tool patterns
All tools use `@mcp.tool()` via the global `plex_mcp.server.mcp`
instance. New portmanteau tools: `src/plex_mcp/tools/{category}/
manage_{thing}.py` with Literal `operation` parameter.

### REST pattern
Endpoints in `webapp/backend/app/api/{feature}.py`. Routers
registered in `webapp/backend/app/main.py`. Frontend catch-all
rewrite `/api/:path* → :10741/api/:path*` is already in place.

### PlexAPI usage
All Plex interaction via `plexapi` (already a dep). Never make
raw HTTP calls to Plex. Use the central `PlexService` singleton
in `src/plex_mcp/services/plex_service.py`.

### State DB
All user-state tables in the plex-mcp SQLite DB (not Plex's own
metadata.db — NEVER write to that). New tables: include
`created_at`, `updated_at` TIMESTAMP columns.

### LLM preference
Ollama (`gemma3:12b` default) for all routine sampling. Escalate
to frontier models (via webapp, not MCP server) only for
genuinely hard synthesis (deep film essays, 200-episode show arcs).

### Scale awareness
50,000+ video items is the target scale. Every background job
needs:
- Progress reporting (SSE-compatible)
- Graceful interruption (cancel flag checked between items)
- Resumability (survive restart, pick up where left off)
- Rate-limited external calls (respect Letterboxd/IMDB/RT bot policies)

### Honesty rules (from user preferences, non-negotiable)
- No stubs marked complete; if placeholder, explicit TODO + NotImplementedError
- No mock fallbacks disguised as real features
- External scraping: cache aggressively (90-day default), rate-limit
  (1 req/sec per domain), fail gracefully
- Accurate effort estimates — days not weeks
- Bulk operations always show progress; user knows if something is going
  to take overnight

### Dependencies already available
`plexapi`, `httpx`, `lancedb`, `fastembed`, `lxml`, `beautifulsoup4`,
`fastmcp`, `pydantic`, `sqlalchemy`.

### Frontend deps
Next.js 15, React 19, Tailwind, lucide-react, recharts.

## Workflow for any project

1. Read `docs/plans/ROADMAP.md`
2. Read `docs/plans/{PROJECT}.md`
3. Load per-project skill
4. Build phase by phase; commit after each verified phase
5. On ship: update CHANGELOG, docs/plans/README.md, FLEET_INDEX.md

## Do not

- Don't modify Plex's own database
- Don't scrape aggressively (bot detection on Letterboxd/IMDB/RT/MC)
- Don't introduce port changes
- Don't build features that duplicate upstream Plex roadmap items
  (Plex Sonic, built-in intro detection — not our territory)
- Don't add mock data that looks real
- Don't commit API keys (TMDB key in env var, never in code)

## Reference files

- `src/plex_mcp/server.py` — FastMCP instance
- `src/plex_mcp/services/plex_service.py` — PlexAPI wrapper
- `src/plex_mcp/rag/` — existing LanceDB integration
- `webapp/backend/app/main.py` — FastAPI router registration
- `webapp/backend/app/api/rag.py` — template for new API modules
- `webapp/frontend/common/api.ts` — typed API client

---

*Roadmap by Claude Opus 4.7 (Anthropic), April 2026.*

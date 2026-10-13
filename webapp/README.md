# PlexMCP Webapp

Browser UI for PlexMCP: connects to the MCP server via the backend (FastAPI), which calls PlexMCP tools in-process. Ports **10740** (backend) and **10741** (frontend) per [mcp-central-docs WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/operations/WEBAPP_PORTS.md).

## Stack

- **Backend**: FastAPI, plex_mcp portmanteau tools in-process; LLM (Ollama/LM Studio/OpenAI-compat), RAG context, workflows
- **Frontend**: Next.js 15 (pinned 15.2.0), Tailwind CSS, glassmorphism, retractable sidebar, topbar

## Features

- **Layout**: Glassmorphism panels, retractable sidebar (collapse toggle at the top, logo + version, live backend/Plex indicator), topbar (Help + Logs buttons, Webapps dropdown)
- **Pages**: Overview (hero + KPIs + quick actions, via `GET /api/dashboard/`), Libraries, **Movies**, **Search** (keyword + advanced multi-filter), **Semantic search** (RAG), **Media** (dossier + AI context + files/art + playback), **Enrichment** (bulk + theme + person search), **Taste** (profile + rank/score/temporal), **Chat** (agentic + workflow runner), **Repair**, **RAG**, Server (info + diagnostics), Settings, API docs
- **Movies**: Plex poster images (via `/api/image/...` proxy, fixed `follow_redirects` for Plex 307 redirects), library filter, pagination, card/list view. **Click a movie** to open detail modal: poster, metadata (year, duration, rating, genres, directors, tagline, summary), **Play in Plex** button (opens Plex Web in new tab when Plex URL is set in Settings)
- **Prefab cards in chat**: when a tool call returns a Prefab card, the backend surfaces it as `prefabs[]` on `POST /api/llm/agentic` and the chat renders it inline under the assistant message. Renderer: `components/prefab/prefab-renderer.tsx` (Div, Row, Grid, Card/CardHeader/CardTitle/CardDescription/CardContent, H2-H4, P, Text, Small, Metric, Badge, Separator, Image; unknown types fall through to their children). Preview route: `/dev/prefab` (static fixtures, no Plex needed). Plain tool-call API responses still carry `_prefab` (Prefab wire JSON from tool `structured_content`).
- **Settings**: Plex API key and URL; LLM provider, base URL, API key (per-provider keystore, removable), onboarding card, GPU target select, VRAM panel, default model; **RAG / Indexing** section with "Reindex metadata" button (same as Semantic search sync); saved to backend data/settings.json (overrides .env when set)
- **Modals**: Logger (log tail, level/filter), Help (tiered content)
- **Chat**: Local LLM (Ollama/LM Studio) with **live system preprompt** (MCP server tools, webapp pages, Plex server name/version, media libraries list, integrations). Personalities, prompt refining, export (MD/JSON). Use `use_context: true` (default) in POST /api/llm/chat to inject context. **Search + summarize** workflow runner (`POST /api/workflows/run`) sits above the message list.
- **RAG**: Keyword context for chat (`GET /api/rag/context`, with a try-it box on the RAG page); semantic search (`GET /api/rag/semantic?query=...`); vector stats (`GET /api/rag/stats`); **index from UI** (`POST /api/rag/sync`) or via MCP `plex_rag(operation='sync_metadata')`. Requires mcp-central-docs source on path (see root README RAG dependency).
- **Backend APIs**: `/api/dashboard/` (aggregate), `/api/llm` (providers, onboarding, models, chat, agentic, refine, keys incl. DELETE, gpus, loaded, unload), `/api/search/` + `/api/search/advanced` (POST), `/api/taste` (status, profile, temporal, shifts, score, rank, rebuild, sync), `/api/media` (detail, ai-context, stream-url, file, art), `/api/playback` (clients, play), `/api/enrichment/*` (incl. by-theme, by-person), `/api/rag` (stats, sync, semantic, context), `/api/repair` (probe, execute), `/api/server` (status, info), `/api/system` (settings, plex test/pin, diagnostics, api-docs-info), `/api/arr/status`, `/api/workflows/run`, `/api/logs`, `/api/help`, `/api/movies`, `/api/libraries/` (+ single + items). Legacy `/api/v1/search`, `/api/v1/chat` are deprecated.
- **Frontend contract**: all browser calls go through `frontend/utils/api.ts` (no raw `fetch("/api/...")` outside it, except chat streaming and the topbar launcher).

## Start

```powershell
cd webapp
# Set PLEX_TOKEN (and optional LLM_BASE_URL) in backend\.env
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

- Frontend: http://localhost:10741
- Backend: http://localhost:10740
- API docs: http://localhost:10740/docs

See [SETUP.md](SETUP.md) for details.

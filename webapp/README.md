# PlexMCP Webapp

Browser UI for PlexMCP: connects to the MCP server via the backend (FastAPI), which calls PlexMCP tools in-process. Ports **10740** (backend) and **10741** (frontend) per [mcp-central-docs WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/operations/WEBAPP_PORTS.md).

## Stack

- **Backend**: FastAPI, plex_mcp portmanteau tools in-process; LLM (Ollama/LM Studio/OpenAI-compat), RAG context, workflows
- **Frontend**: Next.js 15 (pinned 15.2.0), Tailwind CSS, glassmorphism, retractable sidebar, topbar

## Features

- **Layout**: Glassmorphism panels, retractable sidebar, topbar (Help + Logs buttons, Webapps dropdown)
- **Pages**: Overview (server status), Libraries, **Movies**, **Search** (keyword), **Semantic search** (RAG), **Chat**, Server (raw JSON), Settings
- **Movies**: Plex poster images (via `/api/image/...` proxy), library filter, pagination, card/list view. **Click a movie** to open detail modal: poster, metadata (year, duration, rating, genres, directors, tagline, summary), **Play in Plex** button (opens Plex Web in new tab when Plex URL is set in Settings)
- **Settings**: Plex API key and URL; LLM provider, base URL, API key, default model; **RAG / Indexing** section with "Reindex metadata" button (same as Semantic search sync); saved to backend data/settings.json (overrides .env when set)
- **Modals**: Logger (log tail, level/filter), Help (tiered content)
- **Chat**: Local LLM (Ollama/LM Studio) with **live system preprompt** (MCP server tools, webapp pages, Plex server name/version, media libraries list, integrations). Personalities, prompt refining, export (MD/JSON). Use `use_context: true` (default) in POST /api/llm/chat to inject context.
- **RAG**: Keyword context for chat (`GET /api/rag/context`); semantic search (`GET /api/rag/semantic?query=...`); **index from UI** (`POST /api/rag/sync`) or via MCP `plex_rag(operation='sync_metadata')`. Requires mcp-central-docs source on path (see root README RAG dependency).
- **Backend APIs**: `/api/llm` (models, chat with optional preprompt, refine), `/api/rag/context`, `/api/rag/semantic`, `/api/rag/sync` (POST), `/api/fleet/launch` (POST), `/api/v1/search`, `/api/v1/chat`, `/api/workflows/run`, `/api/logs`, `/api/help`, `/api/movies`, `/api/system/settings` (GET/PATCH)

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

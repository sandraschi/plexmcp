# PlexMCP Webapp

Browser UI for PlexMCP: connects to the MCP server via the backend (FastAPI), which calls PlexMCP tools in-process. Ports **10740** (backend) and **10741** (frontend) per [mcp-central-docs WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/operations/WEBAPP_PORTS.md).

## Stack

- **Backend**: FastAPI, plex_mcp portmanteau tools in-process; LLM (Ollama/LM Studio/OpenAI-compat), RAG context, workflows
- **Frontend**: Next.js 15 (pinned 15.2.0), Tailwind CSS, glassmorphism, retractable sidebar, topbar

## Features

- **Layout**: Glassmorphism panels, retractable sidebar, topbar (Help + Logs buttons, Webapps dropdown)
- **Pages**: Overview (server status), Libraries, Search (keyword + RAG/semantic note), Movies, Settings, Chat, Server (raw JSON)
- **Movies**: Library filter, pagination (page/limit in URL), card vs list view toggle (persisted in browser)
- **Settings**: Plex API key and URL; LLM provider (ollama/lmstudio/openai), base URL, API key, default model (from backend); saved to backend data/settings.json and applied at runtime (overrides .env when set)
- **Modals**: Logger (log tail, level/filter), Help (tiered content)
- **Chat**: Local LLM (Ollama/LM Studio), personalities, prompt refining, export (MD/JSON)
- **Backend APIs**: `/api/llm` (models, chat, refine), `/api/rag/context`, `/api/workflows/run`, `/api/logs`, `/api/help`, `/api/movies` (library_id, limit, offset), `/api/system/settings` (GET/PATCH)

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

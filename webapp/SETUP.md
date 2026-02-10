# PlexMCP Webapp Setup

## Prerequisites

- Python 3.10+ with `plex-mcp` installed: `pip install -e ".[dev]"` from repo root
- Node.js 18+
- PLEX_TOKEN (from Plex Web App → Account → Authorized Devices)
- PLEX_URL (e.g. http://localhost:32400)

## Reservoir ports (mcp-central-docs)

- Backend: 10740
- Frontend: 10741
- start.ps1 clears ports with kill-port, then starts both

## Quick start

```powershell
cd webapp
# Copy backend env and set PLEX_TOKEN
copy backend\env.example backend\.env
# Edit backend\.env: PLEX_TOKEN=your-token, PLEX_URL=...

powershell -ExecutionPolicy Bypass -File .\start.ps1
```

- Frontend: http://localhost:10741
- Backend: http://localhost:10740
- API docs: http://localhost:10740/docs

## Manual run

```powershell
# Terminal 1 - backend
cd webapp\backend
$env:PYTHONPATH = "..\..\src"
$env:PLEX_TOKEN = "your-token"
$env:PLEX_URL = "http://localhost:32400"
python -m uvicorn app.main:app --reload --port 10740

# Terminal 2 - frontend
cd webapp\frontend
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:10740"
$env:NEXT_PUBLIC_APP_URL = "http://127.0.0.1:10741"
npm run dev
```

## Backend .env and Settings

The backend loads `.env` from `webapp/backend/` (path relative to the app), so the token is found regardless of working directory.

Required for Plex:

```
PLEX_TOKEN=your-token
PLEX_URL=http://localhost:32400
```

Optional (Chat, Refine, AI workflows):

```
LLM_PROVIDER=ollama
LLM_BASE_URL=http://127.0.0.1:11434
# LLM_API_KEY=  # for OpenAI-compatible
# RAG_INDEX_ENABLED=false
# RAG_EMBED_MODEL=nomic-embed-text
```

Settings saved in the webapp (Settings page) are stored in `backend/data/settings.json` and override these env vars at runtime. The `data/` folder is in `.gitignore` so tokens are not committed.

## Frontend .env.local

For manual frontend start, create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:10740
NEXT_PUBLIC_APP_URL=http://127.0.0.1:10741
```

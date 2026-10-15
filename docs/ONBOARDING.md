# Onboarding — PlexMCP first-time setup

Get from zero to a green dashboard in ~5 minutes. You need a Plex Media Server
(free software, running anywhere reachable: same PC, LAN, or Tailscale) and
nothing else. No credit card, no paid account, no cloud key for the core flow.

## What costs money (and what does not)

| Feature | Cost |
|---|---|
| Plex Media Server, this repo, dashboard, MCP tools, RAG, taste, enrichment (Wikipedia + JustWatch) | Free |
| TMDB enrichment layer | Free API key (optional; enrichment works without it) |
| Local LLM chat (Ollama / LM Studio) | Free, runs on your machine |
| Cloud LLM chat (OpenAI / Anthropic / DeepSeek / OpenRouter) | Their per-token billing (optional; skip it and use local) |

## Steps

1. **Start the app.** Double-click `start.bat` (or `.\start.ps1` from PowerShell).
   Backend: `http://127.0.0.1:10740`, frontend: `http://127.0.0.1:10741`.
2. **Open the dashboard.** A big red **Complete onboarding — connect Plex** button
   sits under the hero until Plex is reachable. That button is the whole todo list.
3. **Connect Plex** (Settings → Plex, or follow the red button):
   - **Easiest:** click **Get a new token**, approve at app.plex.tv, done — the
     token saves itself. No copy-paste.
   - **Manual:** paste `PLEX_URL` (usually `http://127.0.0.1:32400` for a local
     server) and your `X-Plex-Token`, then **Test connection**.
4. **Sanity check.** The red button disappears, KPI cards fill in, and
   `http://127.0.0.1:10740/health` returns `{"status":"ok", ...}`.
5. **Optional next:** RAG page → Reindex (semantic search), Taste page → Rebuild
   (recommendations), Settings → LLM (chat provider: local Ollama is free).

## Where settings live (read this before editing .env files)

Three `.env` files exist because three different processes read config.
They are **not** interchangeable — set each value where its process looks:

| File | Read by | Holds |
|---|---|---|
| `webapp/backend/.env` | FastAPI backend + MCP tools (in-process) | `PLEX_URL`, `PLEX_TOKEN`, `CORS_ORIGINS`, `HOST`/`PORT`, LLM vars |
| `.env` (repo root) | MCP stdio server, CLIs, scripts | `PLEX_BASE_URL`, `PLEX_TOKEN` |
| `webapp/frontend/.env` + `.env.local` | Next.js at **build time** (`NEXT_PUBLIC_*` only) | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL` |

Precedence inside the backend: real process environment > `webapp/backend/data/settings.json`
(Settings page writes here) > `webapp/backend/.env`. If a value you set seems
ignored, check Settings → Plex first — a saved override there wins over the file.
Full variable reference: [CONFIGURATION.md](CONFIGURATION.md).

## Pitfalls that bite every first-timer

- **Wrong Plex URL.** Local server = `http://127.0.0.1:32400` (or `localhost`).
  `https://` or a plex.tv URL will not work here.
- **Revoked/foreign token.** Tokens from another server or a signed-out session
  give 401. Regenerate via the PIN flow instead of recycling old tokens.
- **First MCP mount takes ~90s.** The webapp API is instant; `/mcp` appears
  about a minute later (`/mcp/status` tells you). Not an error.
- **Posters blank in a fresh clone.** The image proxy follows Plex 307 redirects;
  if you touched httpx settings, keep `follow_redirects=True`.
- **Settings page says saved but backend ignores it.** Restart the backend —
  `settings.json` merges into the environment at startup.

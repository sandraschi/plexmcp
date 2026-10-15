# Configuration

## Where .env files live (single source of truth per process)

Three `.env` files exist because three different processes read config.
Set each value where its process looks — they are not interchangeable:

| File | Read by | Holds |
|---|---|---|
| `webapp/backend/.env` | FastAPI backend + MCP tools (in-process) | `PLEX_URL`, `PLEX_TOKEN`, `CORS_ORIGINS`, `HOST`/`PORT`, LLM vars |
| `.env` (repo root) | MCP stdio server, CLIs, scripts | `PLEX_BASE_URL`, `PLEX_TOKEN` |
| `webapp/frontend/.env` + `.env.local` | Next.js at **build time** (`NEXT_PUBLIC_*` only) | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL` |

Precedence inside the backend: real process environment >
`webapp/backend/data/settings.json` (Settings page writes here) >
`webapp/backend/.env`. A saved Settings override wins over the file every time.
First-time setup walkthrough: [ONBOARDING.md](ONBOARDING.md).

## Plex (required)

| Variable | Description |
|----------|-------------|
| `PLEX_TOKEN` | X-Plex-Token (required) |
| `PLEX_URL` / `PLEX_SERVER_URL` | Base URL of Plex (default `http://127.0.0.1:32400`) |

## Sampling (optional)

Server-side LLM for `plex_natural_assistant` / agentic flows when the host does not sample:

| Variable | Description |
|----------|-------------|
| `PLEX_SAMPLING_BASE_URL` | OpenAI-compatible API base (e.g. Ollama `http://127.0.0.1:11434/v1`) |
| `PLEX_SAMPLING_USE_CLIENT_LLM` | Set to `1` to prefer the MCP client’s LLM when supported |

## LLM providers (chat, agentic tool-calling)

Set via **Settings → LLM** (recommended) or environment variables. Local engines (Ollama, LM Studio, vLLM) need no key, just a running instance. Cloud providers work on a GPU-less machine and need a key, saved per-provider to a 0600 keystore file (`webapp/backend/data/llm_keys.json`), never `settings.json`.

| Variable | Provider |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `DEEPSEEK_API_KEY` | DeepSeek |
| `OPENROUTER_API_KEY` | OpenRouter |

An env var always wins over the keystore. Settings also has a **GPU/VRAM panel** (Ollama residents + an "Evict all" button) so an AI task doesn't just fail when VRAM is already full — free it there, or switch to a cloud provider.

## Deep media enrichment (optional)

`plex_media_enrichment`'s `enrich`/`bulk_enrich` operations use:

| Variable | Description |
|----------|-------------|
| `TMDB_API_KEY` | Official TMDB v3 API key. Without it, enrichment still runs on Wikipedia + JustWatch alone. Get one free at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api). |

No key is needed for Wikipedia or JustWatch. LLM synthesis of the critical
dossier (vs. raw sources) uses whichever provider/model is picked in the
webapp's Enrichment/media pages — no separate env var, it reuses the LLM
provider settings above. See [ENRICHMENT.md](ENRICHMENT.md).

## Taste modelling (optional)

| Variable | Description |
|----------|-------------|
| `TASTE_SYNC_INTERVAL_SEC` | How often the webapp backend folds new Plex viewing into the taste profile (default `600`; `0` disables). It does nothing until a profile has been built once from the Taste page or `plex_taste(operation="rebuild_from_history")`, so a fresh install never starts reading Plex on its own. |

Only reads from Plex; derived data is stored in `data/taste.db` (gitignored). See [plans/TASTE_MODELLING.md](plans/TASTE_MODELLING.md).

## RAG / semantic search

The `plex_rag` tool (LanceDB + embeddings) needs shared vector code importable as `docs_mcp.backend.rag_core` (e.g. clone [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) and add its `src` to `PYTHONPATH`). See [RAG.md](RAG.md).

## *arr stack (optional)

Read-only HTTP status for Radarr / Sonarr / Lidarr when set:

| Variable | Description |
|----------|-------------|
| `RADARR_URL`, `RADARR_API_KEY` | Base URL + API key |
| `SONARR_URL`, `SONARR_API_KEY` | Same |
| `LIDARR_URL`, `LIDARR_API_KEY` | Same |

Usually set via the **webapp Settings** page (stored in `webapp/backend/data/settings.json` and applied to the process environment).

## Webapp overrides

The FastAPI backend loads `webapp/backend/data/settings.json` at startup and merges Plex, LLM, and *arr keys into `os.environ`. See [WEBAPP.md](WEBAPP.md).

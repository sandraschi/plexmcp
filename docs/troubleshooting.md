# Troubleshooting

## Diagnose in this order

1. **Plex itself** — In a browser, open your server with a token:  
   `http://YOUR_PLEX:32400/?X-Plex-Token=YOUR_TOKEN`  
   If this fails, fix Plex URL, token, or network before debugging PlexMCP.
2. **Environment** — `PLEX_TOKEN` and `PLEX_URL` (or `PLEX_SERVER_URL`) set in the same shell or `.env` that runs the MCP / backend.
3. **MCP stdio** — Run `uv run plex-mcp-advanced` and watch for import errors. If RAG is optional, ignore `docs_mcp` import messages until you follow [RAG.md](RAG.md).
4. **Web app** — Backend **10740** up before the UI matters: `http://127.0.0.1:10740/docs`. Then open **10741** for the Next.js app. See [WEBAPP.md](WEBAPP.md).
5. **RAG** — [RAG.md](RAG.md) + run `sync_metadata` before expecting semantic search.

Faster path: [QUICKSTART.md](QUICKSTART.md).

| Symptom or error | Go to section |
|------------------|---------------|
| 401 / “unauthorized” from Plex | [Plex authentication](#plex-authentication) |
| `Connection refused` to `:32400` or Plex URL | [Connection refused](#connection-refused) |
| `NullLogger` / logging crash in stdio | [Startup issues (stdio / non-TTY)](#startup-issues-stdio--non-tty) |
| Libraries empty, search returns nothing (but Plex app works) | [Empty libraries or search](#empty-libraries-or-search) |
| “RAG not available” / semantic search empty | [RAG / semantic search unavailable](#rag--semantic-search-unavailable) |
| Radarr/Sonarr read errors | [*arr status unreachable](#arr-status-unreachable) |
| Webapp log file / terminal noise | [Logging](#logging) |

---

## Plex authentication

- Regenerate the token from Plex Web (**Settings → Account → Authorized devices**) if requests return 401.  
- Test in a browser: `http://YOUR_PLEX:32400/?X-Plex-Token=YOUR_TOKEN`

## Connection refused

- Confirm Plex Media Server is running and the URL/port are correct (default **32400**).  
- Check firewalls and VPN/Tailscale if Plex is not on localhost.

## Startup issues (stdio / non-TTY)

- **AttributeError: `NullLogger` has no attribute `handlers`:** Some FastMCP 3.1+ environments break logging when no TTY is attached. Use **PlexMCP v2.3.1+** (hardened logging) or set logging env vars as in [DEVELOPMENT.md](DEVELOPMENT.md) / tests.

## Empty libraries or search

- Confirm libraries exist in Plex and scans have completed.  
- Verify the token has access to that server.

## RAG / semantic search unavailable

- Ensure `docs_mcp.backend.rag_core` is importable ([RAG.md](RAG.md)).  
- Run **`sync_metadata`** once before **`semantic_search`**.

## *arr status unreachable

- Use the same base URL the browser uses to open Radarr/Sonarr/Lidarr.  
- From Docker, the backend must reach the container (host port, LAN IP, or reverse proxy).  
- API keys: each app → **Settings → General → Security**.

## Logging

Webapp backend logs: `logs/webapp.log` (rotating). Set `PLEXMCP_ALLOW_LOGGING` as documented in tests if FastMCP logging conflicts with your terminal.

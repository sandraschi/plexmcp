# Troubleshooting

## Plex authentication

- Regenerate the token from Plex Web (**Settings → Account → Authorized devices**) if requests return 401.  
- Test in a browser: `http://YOUR_PLEX:32400/?X-Plex-Token=YOUR_TOKEN`

## Connection refused

- Confirm Plex Media Server is running and the URL/port are correct (default **32400**).  
- Check firewalls and VPN/Tailscale if Plex is not on localhost.

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

# Self-hosting PlexMCP

Running PlexMCP at home (or on a VPS) for **your** library. This is practical guidance, not legal advice.

---

## Threat model (keep it simple)

- Your **Plex token** is a **bearer credential**. Anyone who can call your Plex URL with that token can act as you toward Plex (within API limits).
- Exposing **PlexMCP** or the **web app** to the internet without TLS and auth means anyone who finds the port could abuse **your** automation surface.

**Default posture:** run MCP and the web UI on **localhost** or **private LAN** only. Add HTTPS + access control before you open WAN ports.

---

## Network layout

| Service | Default port (this repo) | Notes |
|---------|--------------------------|--------|
| Plex Media Server | **32400** | Plex’s own port |
| PlexMCP web backend | **10740** | FastAPI, `/api`, `/docs`, `/mcp` |
| PlexMCP web frontend | **10741** | Next.js |

Only **bind to all interfaces** (`0.0.0.0`) if you intend LAN/WAN access and have firewalls in place.

---

## Reverse proxy and HTTPS

For a **public** hostname:

1. Terminate **TLS** at a reverse proxy (Caddy, nginx, Traefik, etc.).
2. Proxy to `127.0.0.1:10741` (UI) and/or `127.0.0.1:10740` (API).
3. Prefer **WebSockets** if your MCP client uses streaming over HTTP (check your proxy timeouts).

The Next.js app may call the API with a **relative** `/api` path or a configured base URL — set `NEXT_PUBLIC_*` or your proxy paths so the browser never sends tokens to the wrong origin.

### Caddy (automatic HTTPS)

Example `Caddyfile` fragment — replace `plexmcp.example.com` and add your own auth (Caddy has `basicauth`, OAuth plugins, or IP allowlists via `remote_ip` matchers):

```text
plexmcp.example.com {
    reverse_proxy 127.0.0.1:10741
}
api.plexmcp.example.com {
    reverse_proxy 127.0.0.1:10740
}
```

If the UI and API share one origin, prefer **one hostname** and proxy path prefixes (e.g. `/api` to 10740, everything else to 10741) so `NEXT_PUBLIC_*` matches production.

### nginx (manual TLS)

Example `server` blocks after you have certificates (e.g. `certbot`):

```nginx
server {
    listen 443 ssl;
    server_name plexmcp.example.com;
    ssl_certificate     /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:10741;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

server {
    listen 443 ssl;
    server_name plexmcp-api.example.com;
    ssl_certificate     /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:10740;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

---

## Secrets and configuration

- Prefer **environment variables** or a **private** `.env` file never committed to git.
- The web app can persist settings under `webapp/backend/data/settings.json` — **back up** and **restrict file permissions** on shared servers.
- Rotate your **Plex token** if it leaks (sign out devices / regenerate per Plex’s docs).

---

## Docker and stacks

Many homelabs run Plex in **Docker**. PlexMCP can run on the host or in another container:

- Use the **container-reachable** Plex URL (service name or bridge IP), not always `127.0.0.1`.
- Mount the same **data** directory if you persist LanceDB / caches.

There is no single “official” Docker Compose in this repo for the full stack; treat compose as **your** integration layer.

---

## MCP over the internet

If you expose **HTTP MCP**:

- Use **TLS**, **authentication**, and ideally **allowlists** (IP or VPN).
- stdio-based desktop clients are **not** exposed by default — they spawn a local process.

---

## Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — components and data flow  
- [CONFIGURATION.md](CONFIGURATION.md) — env vars and settings file  
- [INSTALL.md](INSTALL.md) — local install  
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — when nothing connects  

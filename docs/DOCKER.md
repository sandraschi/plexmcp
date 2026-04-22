# Docker (optional)

PlexMCP is developed and run **natively** with [uv](https://docs.astral.sh/uv/) and `webapp/start.ps1`. Docker is **optional** for advanced deployments.

## Example compose

See the repo root **[`docker-compose.example.yml`](../docker-compose.example.yml)**. It:

- Mounts the repository into a Python **3.12** container
- Exposes the FastAPI **backend** on **10740**
- Shows where you would set **`PLEX_TOKEN`** and **`PLEX_URL`**
- Includes a **commented** `PYTHONPATH` for [RAG.md](RAG.md) when mcp-central-docs is mounted

It does **not** build a production-optimized image; adjust `command`, add a `Dockerfile`, or use host networking for your OS.

## Plex from a container

If Plex runs on the **host** and the API container must reach it, use:

- **Docker Desktop (Windows / macOS):** `http://host.docker.internal:32400` as `PLEX_URL`
- **Linux:** the host’s LAN IP or [extra_hosts](https://docs.docker.com/compose/compose-file/compose-file-v3/#extra_hosts) mapping

## Next.js in Docker

The example focuses on the **API** only. The Next.js frontend is normally started on the **host** (`webapp/frontend` / `start.ps1`) to avoid a heavy multi-stage image in this repository. You can add a `node:20` service to the same compose file and copy the pattern from the official [Next.js Docker](https://nextjs.org/docs/app/building-your-application/deploying#docker-image) documentation.

## Related

- [SELF_HOSTING.md](SELF_HOSTING.md) — TLS and reverse proxy  
- [WEBAPP.md](WEBAPP.md) — ports and startup  
- [INSTALL.md](INSTALL.md) — supported install path (uv)  

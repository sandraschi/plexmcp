# Tauri 2.0 Native Desktop App

> **End users:** download `Plex MCP_*_x64-setup.exe` from [Releases](https://github.com/sandraschi/plex-mcp/releases/latest) and double-click. This page is for **maintainers** building the installer.

Plex MCP ships with a Tauri 2.0 native wrapper — **one** installer, **one** shortcut. Python backend embedded in the bundle (not `externalBin`).

## Build (maintainers)

```powershell
just build-native
```

```text
native/target/release/bundle/nsis/Plex MCP_2.4.1_x64-setup.exe
```

## Production pitfalls (fleet)

Installer-only failures (`Failed to fetch`, missing posters, backend spawn, **install hang**, silent backend) — see **mcp-central-docs** [`standards/TAURI_PRODUCTION_PITFALLS.md`](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/TAURI_PRODUCTION_PITFALLS.md). Run the **Fleet rollout protocol (§B–M)** before every NSIS release.

Maintainer shortcut: `scripts/update-tauri-starts-link.ps1` → `D:\Dev\Tauri starts\plex-mcp-setup.lnk`

## Architecture

| Layer | Port | Notes |
|-------|------|-------|
| Tauri operator | — | Single install shortcut |
| Embedded Python backend | **10740** | FastAPI via `uvicorn app.main:app` |

Production UI uses `API_BASE = http://127.0.0.1:10740` (see `webapp/frontend/utils/api.ts`).

## Dev mode

```powershell
cd native
npm install
npx @tauri-apps/cli dev
```

Frontend dev: `http://localhost:10741` with Next rewrites to the backend.

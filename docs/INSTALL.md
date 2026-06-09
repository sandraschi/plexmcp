# Installing plex-mcp

Fast path: [**QUICKSTART.md**](QUICKSTART.md). New to Plex or tokens: [**PLEX.md**](PLEX.md). Full map: [**README.md**](README.md) (hub).

## Option A — Desktop app (recommended)

**Download, double-click, done.** No Git, no Python, no `just`, no build step.

1. Go to [Releases](https://github.com/sandraschi/plex-mcp/releases/latest)
2. Download **`Plex MCP_*_x64-setup.exe`**
3. Double-click the installer → finish the wizard
4. Set your [Plex token](PLEX.md) if prompted (or in Windows env / app config)
5. Launch **Plex MCP** from the Start menu

That's it. Backend **10740** starts with the app.

**Requirements:** Windows 10/11, a running Plex Media Server, and an X-Plex-Token. [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) if prompted.

---

## Other install paths

### Prerequisites (Options B–E only)

| Tool | Purpose |
|------|---------|
| Git, uv | Clone and run from source |
| Node.js | Webapp dev |
| just | Optional dev shortcuts |
| Plex + [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) | API access |

Python **3.12+** for source installs.

---

## Option B — MCPB drag and drop

When published on [Releases](https://github.com/sandraschi/plex-mcp/releases/latest):

1. Download `plex-mcp*.mcpb`
2. Claude Desktop → Settings → MCP Servers → Install from file

Or build locally: `just build` (see [webapp/README.md](../webapp/README.md)).

---

## Option C — Fastest from source (webapp)

```powershell
git clone https://github.com/sandraschi/plex-mcp
cd plex-mcp
copy .env.example .env
# Edit .env — set PLEX_TOKEN, PLEX_URL
.\start.ps1
```

Or: `just webapp` — backend **10740**, frontend **10741**.

---

## Option D — MCP stdio only

```powershell
git clone https://github.com/sandraschi/plex-mcp
cd plex-mcp
uv sync
$env:PLEX_TOKEN = "your-token"
$env:PLEX_URL = "http://127.0.0.1:32400"
uv run plex-mcp-advanced
```

Claude Desktop:

```json
{
  "mcpServers": {
    "plex-mcp": {
      "command": "uv",
      "args": ["run", "plex-mcp-advanced"],
      "cwd": "D:/path/to/plex-mcp",
      "env": {
        "PLEX_TOKEN": "your-token",
        "PLEX_URL": "http://127.0.0.1:32400"
      }
    }
  }
}
```

---

## Option E — Developer mode

```powershell
winget install Casey.Just
git clone https://github.com/sandraschi/plex-mcp
cd plex-mcp
just install
just webapp
```

Other recipes: `just start`, `just test`, `just lint`. List all: `just --list`.

**Build the Windows installer** (maintainers only): `just build-native` → [TAURI.md](./TAURI.md).

---

## Install uv (Windows)

If `uv` is not on PATH:

```powershell
$uvInstall = Join-Path $env:TEMP "uv-install.ps1"
Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $uvInstall
powershell -ExecutionPolicy Bypass -File $uvInstall
Remove-Item $uvInstall
```

Confirm: `where.exe uv`

---

## Verify installation

1. Desktop app running — health shows backend on **10740**
2. `GET http://127.0.0.1:10740/health` → OK
3. MCP prompt: *List libraries on my Plex server.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Desktop app won't start | Install [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) |
| Plex auth errors | Set `PLEX_TOKEN` — [PLEX.md](PLEX.md) |
| Port 10740/10741 in use | Stop other fleet service on that port |
| `just` not found | Use Option A (no just) or Option C without just |

---

*Feature overview: [README.md](../README.md)*

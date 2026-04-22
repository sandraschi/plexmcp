# Installation

Fast path: [**QUICKSTART.md**](QUICKSTART.md). New to Plex or tokens: [**PLEX.md**](PLEX.md). Full map: [**README.md**](README.md) (hub).

## Prerequisites

- Python **3.12+**
- **uv** with `uv.exe` available on your **PATH** (see [Install uv](#install-uv-windows) below)
- A running **Plex Media Server** and an [X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

## Install uv (Windows)

Install the standalone uv toolchain (official script; no pipe):

```powershell
$uvInstall = Join-Path $env:TEMP "uv-install.ps1"
Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $uvInstall
powershell -ExecutionPolicy Bypass -File $uvInstall
Remove-Item $uvInstall
```

Alternatively, follow [uv installation](https://docs.astral.sh/uv/getting-started/installation/) (including the one-line installer if you prefer).

Close and reopen the terminal (or sign out and back in) so **PATH** updates apply.

Confirm `uv.exe` is on PATH:

```powershell
where.exe uv
```

You should see a path such as `...\uv.exe` (often under your user profile). If `where.exe` finds nothing, add the directory that contains `uv.exe` to **PATH** in Environment Variables, or see [uv installation](https://docs.astral.sh/uv/getting-started/installation/) for manual options.

After that, `uv sync`, `uv run`, and `uv pip` work the same whether you type `uv` or `uv.exe`.

## From the repo (development)

```powershell
git clone https://github.com/sandraschi/plex-mcp.git
cd plex-mcp
uv sync
```

Set environment variables (or use a `.env` file in the project root):

| Variable | Purpose |
|----------|---------|
| `PLEX_TOKEN` | Required — Plex authentication |
| `PLEX_URL` or `PLEX_SERVER_URL` | Plex base URL (default `http://127.0.0.1:32400`) |

Run the MCP server (stdio, for Claude Desktop / Cursor):

```powershell
uv run plex-mcp-advanced
```

Equivalent: `python -m plex_mcp` if your environment has the package on `PYTHONPATH`.

## Claude Desktop

Add a server entry that runs the command above with `PLEX_TOKEN` and `PLEX_URL` in `env`. Example (uses `uv.exe` if that is what resolves on PATH):

```json
{
  "mcpServers": {
    "plex-mcp": {
      "command": "uv",
      "args": ["run", "plex-mcp-advanced"],
      "cwd": "D:/Dev/repos/plex-mcp",
      "env": {
        "PLEX_TOKEN": "your-token",
        "PLEX_URL": "http://127.0.0.1:32400"
      }
    }
  }
}
```

Adjust `cwd` and paths for your machine. If the client requires a full path to the executable, use the path reported by `where.exe uv` (the `uv.exe` file).

## PyPI

**Only after** the project is registered on PyPI and a release is published (check [CHANGELOG.md](../CHANGELOG.md) or PyPI for `plex-mcp-advanced`):

```powershell
uv pip install plex-mcp-advanced
```

or:

```powershell
pip install plex-mcp-advanced
```

Until then, install **from the repo** ([From the repo](#from-the-repo-development)) or from a **local wheel / sdist** built with `uv build`, or `pip install` / `uv pip install` from a `git+https://...` URL if you publish tags.

## Webapp (browser UI)

See [webapp/README.md](../webapp/README.md) and [webapp/SETUP.md](../webapp/SETUP.md). From repo root:

```powershell
cd webapp
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Backend **10740**, frontend **10741** (fleet range). MCP is also mounted at `/mcp` on the backend.

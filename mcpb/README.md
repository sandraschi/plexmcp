# plex-mcp MCPB Bundle

Plex Media Server MCP server — comprehensive media management via FastMCP 3.4+.

## Usage

Install via Claude Desktop:
```json
{
  "mcpServers": {
    "plex-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "${PWD}", "python", "-m", "plex_mcp.main"],
      "env": {
        "PLEX_URL": "http://localhost:32400",
        "PLEX_TOKEN": "<your-token>"
      }
    }
  }
}
```

## Contents

- `src/plex_mcp/` — server source
- `assets/prompts/` — system prompt, user instructions, examples
- `manifest.json` — MCPB bundle manifest v0.2

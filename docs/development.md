# Development

```powershell
uv sync
uv run ruff check src tests
uv run ruff format src tests
uv run pytest tests -q
```

Use **`just`** if you use the repo [justfile](../justfile): `just check`, `just test`, etc.

## Layout

- `src/plex_mcp/` — MCP server, tools, services
- `webapp/backend/` — FastAPI app
- `webapp/frontend/` — Next.js app

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) if present.

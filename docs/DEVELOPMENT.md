# Development

**Release version (single source of truth):** `pyproject.toml` under `[project] version`. Print it with:

```powershell
just version
```

When you cut a release, update the version there and match the **Version** badge in the [root README](../README.md).

```powershell
uv sync
uv run ruff check src tests
uv run ruff format src tests
uv run pytest tests -q
```

Use the [justfile](../justfile) for the usual tasks: `just test`, `just fix`, `just version`, `just e2e` (Playwright in `webapp/frontend`), and `just --list` for everything.

## Security checks in CI

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs **Semgrep** on every push and pull request. There is no separate **Bandit** or **safety** job in CI today; you can run them locally if you want extra Python dependency and pattern coverage:

```powershell
uv tool run bandit -r src
uv tool run safety check
```

Ruff and Biome cover style and a large class of issues; Semgrep adds broader SAST rules for the whole tree.

### Biome (frontend)

[`webapp/frontend/biome.json`](../webapp/frontend/biome.json) turns **off** a few **recommended** rules that were noisy on this codebase without changing runtime behavior (for example `useKeyWithClickEvents` on modal backdrops, `noArrayIndexKey` on search results, `useButtonType` project-wide, `noExplicitAny` while types are gradually tightened). Security-sensitive issues are still fixed in code where it matters (e.g. **no** `eval` in the repair probe view).

## Layout

- `src/plex_mcp/` — MCP server, tools, services
- `webapp/backend/` — FastAPI app
- `webapp/frontend/` — Next.js app

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) if present.

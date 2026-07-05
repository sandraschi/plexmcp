# plex-mcp — Build Log

> **Purpose:** Track build failures, regressions, and fixes during NSIS/PyInstaller builds.
> This is NOT a changelog (functional changes) — it records build-process issues.

## 2026-06-23 v2.4.1

### Stale `out/` directory — 404 page served instead of SPA

**Symptom:** Frontend rendered the Next.js 404 page (black text on white, "This page could not be found"). All API calls worked, JS/CSS files existed.
**Root cause:** Multiple partial rebuilds left stale `out/` with a corrupted build. The HTML was the pre-rendered 404 page.
**Fix:** `Remove-Item out/ -Recurse -Force`, disable API routes (`app/api/`, `app/tools/`), clean rebuild with `TAURI_BUILD=1`.
**Detection:** After build, check `out/index.html` contains the app content (contains "Plex" and dark theme classes), not "pagePath":"/404".

### LLM API: missing `/v1/` prefix for LMStudio

**Symptom:** Chat returns `"Unexpected endpoint or method. (POST /chat/completions)"`. Models endpoint returns empty list with `"provider":"openai-compatible"`.
**Root cause:** Backend sends `/chat/completions` but LMStudio (OpenAI-compatible) serves at `/v1/chat/completions`. Ollama accepts both, LMStudio doesn't.
**Fix:** Changed `{url}/chat/completions` to `{url}/v1/chat/completions` and `{url}/models` to `{url}/v1/models` in `api/llm.py` and `api/media.py`.
**Fleet:** Documented in BUGS_DEPOT.md and TAURI_PRODUCTION_PITFALLS.md symptom table.
**Detection:** Check `/api/llm/models` returns models; check `/api/llm/chat` succeeds with LMStudio provider.

### installerHooks not wired in tauri.conf.json

**Symptom:** `hooks.nsh` file existed but `tauri.conf.json` had `"nsis": {}` (empty). NSIS would not invoke the kill hooks, causing install hang on upgrade when backend.exe is file-locked.
**Root cause:** `installerHooks` key missing from `bundle.windows.nsis` in tauri.conf.json.
**Fix:** Added `"nsis": { "installerHooks": "./windows/hooks.nsh" }`.

### Missing `import mcp.types` eager import

**Symptom:** Pitfalls doc §E requires `import mcp.types` in `run_server.py` to freeze the `mcp` bootstrap before `fastmcp` touches it. Without this, `fastmcp.utilities.types.Image` can crash with `module 'mcp' has no attribute 'types'` in frozen exe.
**Fix:** Added `import mcp.types  # noqa: F401` to `run_server.py` after the `_strptime`/`_datetime` imports.

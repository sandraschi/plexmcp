# PlexMCP Testing Standards (v13.1)

This document outlines the "Dual Mode" testing architecture implemented for PlexMCP to ensure high-fidelity verification in both CI/CD and local integration environments.

## Architecture

We use a dual-mode verification scaffold that automatically switches between high-fidelity mocks and live integration depending on the environment context.

### 1. Mocked Mode (CI/CD)
Designed for GitHub Actions and environments without a live Plex server or heavy dependencies (LanceDB/SentenceTransformers).

- **Mock RAG Engine**: Found in `tests/fixtures/mock_rag_engine.py`. It provides deterministic vector search logic using Python dictionaries, bypassing the need for native libraries.
- **Mock Plex Service**: Found in `tests/fixtures/mock_plex_service.py`. It simulates a full Plex library (Movies, Shows, Music) with recursive metadata traversal.
- **FastAPI TestClient**: Used in `tests/test_api_industrial.py` to exercise the webapp backend endpoints (/rag, /repair) against mocked MCP tools.

### 2. Live Integration Mode (Local)
Designed for local development against a real Plex server.

- **Trigger**: tests are gated by the presence of `PLEX_TOKEN` and `PLEX_URL` environment variables.
- **Tool Validation**: Directly exercises `plex_search`, `plex_rag`, and `plex_ffmpeg_mgr` against real media assets.

## Running Tests

### Prerequisites
Ensure the environment is managed via `uv`:
```powershell
uv venv
source .venv/Scripts/activate
uv pip install -e ".[dev,rag]"
```

### Execution Commands

**Run industrial unit/API tests (Mocked):**
```powershell
uv run pytest -v tests/test_rag_service_unit.py tests/test_rag_tool_unit.py tests/test_repair_tool_unit.py tests/test_api_industrial.py
```

**Run full integration suite ( requires PLEX_URL/PLEX_TOKEN):**
```powershell
uv run pytest -v tests/
```

## Test Structure

| File | Purpose |
|------|---------|
| `tests/conftest.py` | Shared fixtures (mock_rag_engine, webapp_app, mock_plex_service). |
| `tests/test_rag_service_unit.py` | Validates recursive metadata indexing for RAG (Shows/Albums). |
| `tests/test_rag_tool_unit.py` | Unit tests for the `plex_rag` portmanteau tool. |
| `tests/test_repair_tool_unit.py` | Unit tests for the `plex_ffmpeg_mgr` tool (probing/sync). |
| `tests/test_api_industrial.py` | FastAPI TestClient validation of webapp endpoints. |
| `tests/test_integration_real_plex.py` | Live integration validation. |

## SOTA v13.1 Compliance
- [x] High-fidelity mocks for complex dependencies.
- [x] Dual-mode switching (Mocked/Live).
- [x] Webapp endpoint coverage using `TestClient`.
- [x] Documentation of test commands and architecture.

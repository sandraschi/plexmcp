# Operational improvements (plan and todo)

**Purpose:** Track **docs, DX, and operations** work that is not product roadmap (see [`ROADMAP.md`](ROADMAP.md) for feature specs).

**Status legend:** `todo` → `in progress` → `done` (date in PR or commit when closing).

---

## Phase 0 — Shipped in repo (bootstrap)

| ID | Item | Status |
|----|------|--------|
| 0.1 | User-facing README + doc hub + `QUICKSTART.md` | done |
| 0.2 | `PLEX.md`, `ARCHITECTURE.md`, `SELF_HOSTING.md` | done |
| 0.3 | Troubleshooting: ordered “diagnose first” flow | done |
| 0.4 | `SELF_HOSTING.md`: Caddy + nginx copy-paste samples | done |
| 0.5 | `RAG.md`: verify `docs_mcp` import (one-liner, Windows + POSIX) | done |
| 0.6 | `plans/README.md`: link to this file | done |

---

## Phase 1 — First-run and support load

| ID | Item | Status |
|----|------|--------|
| 1.1 | `TROUBLESHOOTING.md`: table of symptoms → section | done |
| 1.2 | `docs/assets/`: **SVG** wireframes for Overview, Search, Settings + [WEBAPP.md](../WEBAPP.md) gallery | done |
| 1.3 | **Link checker** in CI — `lychee` job ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)), `continue-on-error: true` while external URLs evolve | done |
| 1.4 | **E2E smoke** (Playwright): `webapp/frontend/e2e/`, `npm run test:e2e`, `just e2e` | done |
| 1.5 | `just version` + README badge policy | done |

---

## Phase 2 — Hardening and scale

| ID | Item | Status |
|----|------|--------|
| 2.1 | **Docker** — [`docker-compose.example.yml`](../../docker-compose.example.yml) + [DOCKER.md](../DOCKER.md) | done |
| 2.2 | `TOOLS.md`: “suggested agent flows” | done |
| 2.3 | Web UI: **BackendStatusBanner** when `/api/health` fails; quieter proxy logging (`NEXT_DEBUG_PROXY=1`) | done |
| 2.4 | **PR template** | done |

---

## Phase 3 — Nice to have

| ID | Item | Status |
|----|------|--------|
| 3.1 | **Video** for `QUICKSTART` — [QUICKSTART.md](../QUICKSTART.md) “Video walkthrough” section (placeholder until a real link exists) | done |
| 3.2 | **i18n** for webapp | cancelled (out of scope until product demand) |
| 3.3 | **Security in CI** — [DEVELOPMENT.md](../DEVELOPMENT.md) documents Semgrep vs optional Bandit/safety | done |

---

## How to use this file

- Pick a row, set **in progress** in your branch, then **done** when merged.
- For feature work (RAG quality, new tools), use [`ROADMAP.md`](ROADMAP.md) and the per-project specs in this folder.
- Keep this file **practical** — if an item is obsolete, delete it with a one-line note in the table or `CHANGELOG.md`.

**Last updated:** 2026-04-22

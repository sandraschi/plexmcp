# A2A fleet rollout plan (Plex → Calibre → Memory → supervisors)

**Status:** Adopted fleet sequence (operator intent, 2026).  
**Scope:** Where we implement A2A first, what “done” means per repo, and how **supervisor-style** MCP servers (e.g. **meta-mcp**, **universal-actuator-mcp**) fit.

**MCP central docs (two layers):**

| Layer | Role |
|-------|------|
| **Cross-repo policy / ports / fleet tables** | [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs): **[A2A fleet rollout stub](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/A2A_FLEET_ROLLOUT.md)** (pointer + phase table), [WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md), operations standards. Update when **port ranges** or org-wide A2A policy changes. |
| **This directory — `docs/mcp-technical/`** | PlexMCP-local **MCP technical hub**: canonical **A2A briefing**, **this rollout plan** (full checklists). mcp-central-docs mirrors a short summary only. |

---

## Principles (all phases)

1. **MCP stays primary** for IDE hosts (Cursor, Claude Desktop, Windsurf): tools, resources, prompts.
2. **A2A is additive**: agent card + JSON-RPC surface **alongside** MCP HTTP (composite ASGI or reverse-proxy paths), not a replacement for stdio where hosts require it.
3. **Pin protocol version** (`A2A-Version` / spec version per deployment); document in runbooks.
4. **Adapter first**: A2A message → existing tool/service function → A2A artifact; avoid duplicating business logic.
5. **Security**: A2A endpoints are **internet-shaped** even on LAN — authn/z, rate limits, optional mTLS or reverse proxy.

---

## Phase 0 — Shared prerequisites (once)

- [ ] Choose normative A2A spec / SDK version and record it in mcp-central-docs + each repo `README` / `CONFIGURATION`.
- [ ] Define **public base URL** for agent cards (`https://…` or internal `http://host:port`) per deployment.
- [ ] Add minimal **contract tests** (golden JSON-RPC samples) in CI for the first `tasks/send` / `tasks/get` shapes you support.
- [ ] Observability: correlate **task id** with MCP `call_tool` logs / trace ids (A2A does not replace OpenTelemetry).

---

## Phase 1 — **plex-mcp** (start here)

**Why first:** This repo already has **HTTP Streamable MCP** (`mcp.http_app()`, fleet backend **10740**, path `/mcp` per [WEBAPP.md](../WEBAPP.md)), and **long-running** work (RAG metadata / subtitle indexing, progress reporting) — ideal for task lifecycle and later push.

**Deliverables (incremental):**

1. [ ] Composite ASGI (or equivalent): existing FastMCP HTTP app **unchanged** + `GET /.well-known/agent.json` + A2A JSON-RPC route (path per pinned spec).
2. [ ] **Agent card** describing Plex specialist skills (align names with stable tool operations, e.g. `plex_rag` sync vs search).
3. [ ] **Pilot adapter**: one **fast** skill (e.g. semantic search) + one **long** skill (e.g. metadata sync) mapped to task states.
4. [ ] Runbook: env vars, version header, how to curl the card and send a test task.

**Exit criteria:** Another process (or manual curl) can discover the card and complete a **fast** task without the IDE; **long** task reaches `working` → `completed` or `failed` with structured errors.

---

## Phase 2 — **calibre-mcp**

**Goal:** Same pattern as Plex after **HTTP capability exists**.

### 2.1 HTTP readiness (mandatory before A2A)

Audit calibre-mcp:

- [ ] If it already exposes **FastMCP `http_app` / `run_http_async`** (or Starlette/FastAPI mounting MCP): proceed to A2A shell (mirror Plex).
- [ ] If it is **stdio-only**: add HTTP using the **same fleet conventions** as Plex ([transport.py](../../src/plex_mcp/transport.py) pattern: `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `MCP_PATH`; register a dedicated port in [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) `WEBAPP_PORTS` or equivalent).

**Calibre-specific notes:**

- Batch operations (library scan, bulk convert, metadata fetch) map naturally to **tasks**.
- Keep **low-latency** single-book queries on the fast path; avoid forcing every MCP call through A2A.

**Exit criteria:** Agent card live; at least one long and one short task path tested; port and TLS documented centrally.

---

## Phase 3 — **advanced-memory-mcp**

**Goal:** First **horizontal** fleet service: other agents (and supervisors) delegate memory via A2A without embedding memory implementation.

- [ ] Agent card skills: e.g. store, retrieve, search, consolidate (exact names match your tool API).
- [ ] **Rate limits** and payload caps (memory calls can be chatty).
- [ ] Optional: push or polling for **long consolidation / embedding rebuild** jobs.

**Exit criteria:** Plex (or a test harness) can address memory agent by URL + card; MCP remains available for in-process / IDE use.

---

## Phase 4 — **Supervisor / controller MCP servers** (meta-mcp, universal-actuator-mcp)

These are **not** necessarily the third or fourth *implementation* of an A2A **server**; they are often the **best place to centralize A2A client logic**.

| Role | MCP | A2A |
|------|-----|-----|
| **Human / IDE** talks to supervisor | Supervisor exposes **tools** that plan, route, summarize | Usually **no** (MCP into Cursor, etc.) |
| **Supervisor delegates to specialists** | May use stdio MCP to local helpers | Prefer **A2A to remote agent cards** (Plex, Calibre, Memory) for discovery, tasks, cancellation |

**Recommended shapes:**

1. **Supervisor as A2A client only**  
   - Implements MCP for the host.  
   - Fetches `/.well-known/agent.json` from Plex / Calibre / Memory; sends `tasks/send`, polls `tasks/get` (or streaming per spec).  
   - *Easiest:* no new A2A server on supervisor until needed for *inbound* delegation.

2. **Supervisor as A2A server (optional, later)**  
   - Exposes an agent card so **other machines** can delegate *to* the controller (“run this cross-library workflow”).  
   - Use when you have **peer orchestrators** or unattended runners, not only IDE sessions.

**meta-mcp** (example): policy, routing, fan-out to fleet members — ideal owner for **card cache**, **timeouts**, **retry**, and **task cancellation** across Plex + Calibre + Memory.

**universal-actuator-mcp** (example): if it executes **side effects** on diverse systems, keep **dangerous tools** MCP-gated to trusted hosts; use A2A only where the actuator is a **remote agent** with its own card and auth.

**Exit criteria (phase 4):** Documented diagram: which components speak MCP vs A2A; supervisor README lists downstream agent base URLs and auth secrets layout (vault / env).

---

## Dependency graph (summary)

```text
Phase 1  plex-mcp     (A2A server pilot — reference implementation)
    │
    ▼
Phase 2  calibre-mcp  (HTTP if missing, then A2A server — copy Plex shell)
    │
    ▼
Phase 3  advanced-memory-mcp (A2A server — horizontal consumer)
    │
    ▼
Phase 4  meta-mcp / universal-actuator-mcp (A2A client → fleet; optional A2A server)
```

---

## Checklist: “HTTP capability” for Calibre (copy to calibre-mcp issue/PR)

- [ ] `MCP_TRANSPORT=http` supported alongside stdio.
- [ ] Bind address and port registered in mcp-central-docs fleet table.
- [ ] Health or readiness endpoint (if using FastAPI wrapper) for orchestration.
- [ ] CORS / auth only as needed (default deny for anonymous A2A).
- [ ] stdio path unchanged for Claude Desktop users who do not need HTTP.

---

## Related docs (this repo)

- [A2A_PROTOCOL_FLEET_BRIEFING.md](A2A_PROTOCOL_FLEET_BRIEFING.md) — standard background, pros/cons, links.  
- [README.md](README.md) — MCP technical index.

---

*Rollout order: Plex → Calibre (HTTP + A2A) → advanced-memory → supervisor MCPs as A2A clients (then optional A2A servers). Update mcp-central-docs when ports and org-wide defaults are finalized.*

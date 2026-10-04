# plex-mcp — Gap Analysis & Improvement Plan

**Status:** planning, 2026-09-11
**Author:** Claude (Sonnet 5), following a live assess-and-fix session with Sandra
**Repository:** `D:\Dev\repos\plex-mcp`
**Current version:** 2.4.1

---

## Why this doc exists

During one session we found and fixed: a Settings page with no way to test or
refresh a Plex token (dead end on fresh install), a webapp launcher pointed at
the wrong backend, a data-bridge bug that silently broke Movies/Libraries, two
leaked API tokens in source, a `just build-native` recipe that silently built
an unrelated Zed extension instead of the Tauri app, and a smoke-test script
that printed "ALL PHASES PASSED" while a phase had failed.

None of these were exotic. They were all **gaps between "the code exists" and
"a person can actually use it without already knowing the internals."** That's
the theme of this doc: not just new features, but the class of gap the token
facility was — quietly missing plumbing that only becomes visible when someone
hits the dead end.

This is a plan, not a commitment. Sections are independent — pick what's worth
doing.

---

## Part 1 — Foundation debt still open

From the 2026-09-11 assess report (`reports/assess-2026-09-11.md`), fixed
today: the leaked-token/CORS/data-bridge/launcher-config/mcpb-bloat items.
**Not yet fixed**, roughly in priority order:

| Gap | Why it matters | Effort |
|---|---|---|
| ~~CORS middleware silently dropped on the raw `--http` transport path~~ | **Fixed 2026-09-11** — `transport.py` now serves the CORS-wrapped app directly via `uvicorn.Server`; verified live with a real preflight request. | Done |
| ~~Root-level `plex/` package, `server_minimal.py`, `server_fixed_head.py`, `main.bak`, `server.py.bak`, stray tracked `.bak` files~~ | **Fixed 2026-09-11** — deleted; verified imports still work, tests pass, `ruff check` clean, mcpb bundle still builds. | Done |
| ~~Root `Cargo.toml`/`build.ps1` was an undocumented Zed IDE extension colliding with `native/`~~ | **Fixed 2026-09-11** — it's a legitimate Zed context-server integration (launches plex-mcp via stdio, same idea as the Claude Desktop config), not unrelated cruft as first assumed. Moved to `zed-extension/` with its own README; also fixed a real bug in it (`--mcp` isn't a real CLI flag — never `--stdio`, so it likely never worked in actual Zed). | Done |
| `S105/S106/S311/S314/S324/S603/S607` still in the ruff ignore list (only `S110/S112/T201` were removed) | Lower-severity but real: hardcoded-secret patterns, weak randomness, subprocess-without-shell checks are all silenced. Fixing this properly means auditing each flagged call site, not just toggling config — bigger than "Small" as first estimated. | Medium |
| ~75% of tool docstrings missing `## Return Format` / `## Examples` (fleet standard) | Directly hurts LLM/agent callers guessing at a tool's actual output shape | Medium (mechanical, ~65 tools) |
| 3 live `.env` files (root, `webapp/backend/`, `webapp/frontend/`) | Multiple sources of truth for secrets/config — the exact class of bug already fixed once in July and partially regressed | Small |
| No `pyright` installed/wired into CI — the Python type gate is dev-eyeballing only | Type errors ship silently | Medium |
| ~~11/117 tests failing pre-session (`ToolResult` API-contract mismatch in RAG tests, a `test_backend_health` status-string mismatch)~~ | **Fixed 2026-10-04** - all stale test expectations (not tool bugs), verified live against a real Plex server. See `CHANGELOG.md`. | Done |
| GitHub repo is `sandraschi/plexmcp` but local folder / fleet convention is `plex-mcp` (links fixed today, repo itself not renamed) | Cosmetic but a recurring source of broken links; your call | Trivial if you say yes |

---

## Part 2 — More "token extraction"-class gaps (the UX/onboarding kind)

These are places where the underlying capability exists but a person hits a
wall with no path forward — same shape as the Plex-token gap.

- ~~**No connection diagnostics page.**~~ **Done 2026-09-11** — `Settings → Diagnostics` runs Plex/LLM/RAG/*arr at once as a traffic-light list. `GET /api/system/diagnostics`, verified live with real data.
- ~~**No first-run wizard.**~~ **Done 2026-09-11** — 3-step overlay (Plex sign-in → optional LLM provider → done), `localStorage`-gated, mounted in the root layout. Verified live that it correctly stays silent for an already-working setup (auto-marks onboarded rather than nagging); the "shows when Plex isn't configured" path was verified via code review + the already-tested diagnostics error responses rather than a live repro, to avoid risking the real saved Plex token in the process.
- **RAG index has no "build it for me" button visible from where it's needed.**
  It exists in Settings, but if Search returns nothing because the index was
  never built, the Search page itself should say so with a direct link/button,
  not just return empty results.
- **No "what changed" surfacing.** *arr-stack read-only status exists, but
  there's no page that says "3 new episodes since you last opened this" —
  the data is there, the UI moment isn't.
- **`.env` sync direction is one-way and undocumented in the UI.** Settings
  writes to `settings.json`; `.env` is a separate file that `load_dotenv`
  reads once at startup. If someone edits `.env` after first run expecting it
  to take effect, it silently won't (env wins on first load, then
  `settings.json` wins after any Settings save). This is exactly the kind of
  thing that produces a confused bug report — a one-line note in the Settings
  page ("changes here override `.env`") would close it.

---

## Part 3 — Multi-user

`docs/plans/ROADMAP.md` explicitly ruled out **"Sharing / social — personal
library. No."** — worth respecting that as a deliberate decision, not an
oversight. But "multi-user" as you're asking it now probably means something
narrower than public sharing. Two genuinely different asks hide under that
word:

**A. Household profiles (Plex "Home" users).** Plex already supports managed
users under one server. Right now plex-mcp treats the server as having one
identity (`plex_token`). A **"who's watching" switcher** in the webapp —
pick a Plex home user via `myPlexAccount().switchHomeUser()`, remember the
choice per browser — would make watch history, "continue watching," and
(once the Roadmap's taste-modelling ships) recommendations actually
per-person instead of one blended profile for the whole household. This
doesn't violate the "no sharing" decision — it's the same household, same
server, just not pretending everyone has identical taste. Effort: small–medium
(the plexapi call exists; it's mostly webapp state + a settings toggle).

**B. Webapp access control.** Separately: right now anyone on the LAN who can
reach port 10741 can see/change Settings, including *arr API keys and the
Plex token. A lightweight local-only PIN or password gate on Settings (not
full auth — this is a home server, not SaaS) would close that. Effort: small.

**C. Actual multi-tenant / friends' servers.** Supporting someone else's
separate Plex server from the same install is the closest to what ROADMAP.md
ruled out, and I'd leave it out unless your thinking has genuinely changed —
happy to be told otherwise.

---

## Part 4 — AI tools & webpages

**First: the six projects specced in `docs/plans/`** (deep metadata
enrichment - shipped 2026-09-13, taste modelling, mood picker, subtitle RAG,
episode intelligence, cross-library linking) are the highest-leverage thing
sitting on the shelf — they're designed, estimated, and sequenced already.
Nothing below should jump the queue ahead of the remaining five without a
reason.

New ideas, beyond that roadmap:

- **Watch Party Concierge.** `prompts/3_movie_night_decision_maker.txt`
  exists today only as a static prompt file for manual chat use. Turn it into
  an actual page: everyone picks mood/available time/who's watching, the AI
  proposes 3 options with a one-line justification each, one click starts
  playback on the target Plex client. This is the mood picker (already
  specced) plus a group-decision UI layer on top.
- **"Recap me."** Before resuming a show after a gap, generate a short,
  spoiler-safe recap of everything watched so far, built from your own watch
  history + enrichment data. Natural extension of the already-specced
  Episode Intelligence project — worth folding in rather than building
  separately.
- **Ambient "Now Playing" kiosk mode.** A fullscreen, big-cover-art display
  for a spare tablet/TV showing current sessions across the household.
  `useZoom()` and Tauri fullscreen are already in place; this is mostly a
  new route + a "kiosk" flag.
- **AI-curated collections, written back to Plex.** Once taste modelling
  exists, generate smart collections ("90s cyberpunk," "cozy rainy-day
  movies") and actually create them as real Plex collections — `plex_library`
  already has create/update operations, this just wires taste data to them.
- **Library dedupe / health assistant.** You have 83 libraries (`M - Misc`,
  `M - Horror`, `Anime - Series`, etc.) — a very plausible source of
  near-duplicate titles across sections. An enrichment+RAG pass that flags
  likely duplicates or low-bitrate files worth a Radarr/Sonarr upgrade
  request (surfaced as a suggestion, never auto-acted — consistent with
  ROADMAP.md's "no automated acquisition" line) turns existing infrastructure
  into a proactive, occasional-use tool.

---

## Part 5 — Fleet cross-linking

Concrete, not generic:

- **`speech-mcp`** — the fleet already has a voice command bus. Wiring
  playback control ("play something funny," "pause") through it is a small
  integration on plex-mcp's side and a genuinely nice payoff.
- **`discord-mcp` / `email-mcp`** — a weekly or on-recently-added digest
  ("12 new episodes, 3 new movies this week") pushed to a family Discord
  channel or email. Both repos already exist in the fleet; this is a
  scheduled job + one webhook call.
- **`tvtropes-mcp`** — a genuinely fun, differentiated enrichment source
  beyond generic TMDB/Wikipedia (enrichment project #1 in the roadmap
  explicitly plans to expand past Wikipedia-only). "This show leans hard on
  these five tropes" is delightful and nobody else in the fleet has this
  angle.
- **Deeper `arr_stack` integration.** Current integration is read-only
  status. The library-health-assistant idea above is the natural next step:
  surface a suggestion, let the user approve, then hand off to Radarr/Sonarr
  — still no automated acquisition, just closing the "I noticed, now what"
  gap.
- **Fleet Apps Hub.** `GET /api/fleet/apps` dynamic discovery (the
  fleet-standard "what else is running" widget) isn't implemented in this
  webapp at all — confirmed via grep, not assumed. This is a small, standards-
  mandated gap that would let plex-mcp show up in and link out to the rest of
  the fleet's dashboards, and vice versa.

---

## Suggested sequencing

1. ~~**Part 1's small items**~~ **Done 2026-09-11.**
2. ~~**Diagnostics page + first-run wizard**~~ **Both done 2026-09-11.**
3. ~~**Deep metadata enrichment**~~ **Done 2026-09-13** — Wikipedia + TMDB
   (deep) + JustWatch, LLM-synthesised critical dossier, library-wide
   cross-references, `/media` detail page + `/enrichment` bulk-run page. Full
   detail: `DEEP_METADATA_ENRICHMENT.md`. ~~**Taste modelling**~~ **Done
   2026-10-04** - learned from watch history and scored as lift against the
   library rather than the spec's capped EMA, which saturated every dimension at
   +1 on real data (see `TASTE_MODELLING.md`, "What actually shipped").
4. **Household profiles** (Part 3A) — small effort, meaningfully changes who
   the recommendations are actually for.
5. Everything else, roughly in the order it's written above.

## Addendum 2026-09-11 — LLM local + cloud provider registry (not originally in this plan)

Vendored the fleet's proven local+cloud LLM provider registry and Ollama VRAM
management (Anthropic/DeepSeek/OpenRouter join Ollama/LM Studio/vLLM/OpenAI;
0600 per-provider keystore; a Settings VRAM panel with an Evict-all button so
an AI task doesn't just fail when VRAM is full and no cloud fallback is
configured). This wasn't in the original gap analysis above — it came out of
a follow-up conversation, not the initial audit — but it's the same spirit as
Part 4's AI-tools ideas and is now done. Full detail in `CHANGELOG.md` and
`OPERATIONAL_IMPROVEMENTS.md` Phase 4.

Not a mandate — say which of these you actually want and I'll turn it into
real work instead of a document.

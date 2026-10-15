# PlexMCP User Instructions (Claude Desktop bundle)

This bundle gives your assistant 24 tools for your Plex Media Server:
browsing, search, playback, users, playlists, metadata, performance,
reports, semantic search, taste recommendations, enrichment dossiers,
*arr status, help, and server lifecycle. Install once, then talk normally.

## 1. Installation

1. Install the `.mcpb` bundle in Claude Desktop (or wire the MCP server
   manually with `uv run --directory <repo> python -m plex_mcp.main`).
2. Set two values when prompted: `plex_url` (usually
   `http://localhost:32400` for a local server) and `plex_token`
   (your X-Plex-Token — get it via the webapp Settings → Plex → Get a new
   token PIN flow; no copying strings out of browser sessions).
3. Say "check my Plex server status". If it answers with versions and
   libraries, you are done. If it reports 401, regenerate the token; if it
   reports connection refused, Plex is not running or the URL is wrong.

Optional environment: `PLEX_SAMPLING_BASE_URL` (Ollama
`http://127.0.0.1:11434/v1`) enables agentic multi-step workflows when your
MCP host cannot sample; `TMDB_API_KEY` (free) unlocks the TMDB enrichment
layer; `RADARR_URL`/`RADARR_API_KEY` (plus Sonarr/Lidarr pairs) enable the
*arr snapshot. None are required for core use.

## 2. How to ask (phrasebook)

- "What's playing right now?" → streaming sessions with device, progress, bandwidth.
- "Find 4K movies rated below 5." → advanced search, multi-clause filter.
- "Fix the match for Inception." → metadata re-anchor plus refresh.
- "What should I watch tonight?" → taste profile scoring over your library.
- "Movies with slow-burn dread about memory?" → semantic RAG search.
- "Who said 'I'll be back' and in what scene?" → subtitle search.
- "Build me a Nolan shelf." → search, then a saved collection.
- "Who watches the most?" → user activity report.
- "Is Radarr keeping up?" → *arr queue snapshot.
- "Stop the server." → confirmation first, then lifecycle shutdown.

You never need operation names — describe the goal and the assistant picks
the tool and operation. The phrases below exist so power users can be
precise when they want to be.

## 3. Per-tool guide

### plex_library — your shelves
`list` shows every section with type and size — the universal first step on
an unfamiliar server. `get` details one section. `list_items` pages its
contents. `scan` picks up files you just added to disk; `refresh` re-reads
metadata for everything in the section. `create` adds a section (`movie`,
`show`, `music`, `photo` plus a folder path Plex can read). `add_location`
and `remove_location` adjust the folders a section watches. `optimize`
defragments and `clean_bundles` prunes orphaned metadata. `empty_trash`
permanently drops items whose files vanished — confirm it, there is no undo.
`update` renames or retunes a section; `delete` removes the whole section
from Plex (files stay on disk, library record does not) — always confirm.

### plex_media — individual titles
`browse` walks a library page by page. `search` is keyword search, global or
scoped to one library. `get_details` on a `rating_key` returns the complete
record: cast, crew, posters, parts, codecs, subtitles. `get_recent` lists
fresh additions — the same feed the webapp Inbox page shows. `get_stream_url`
resolves a playable URL for a client. `update_metadata` writes corrected
fields (title, tagline, tags) once you know what is wrong.

### plex_search — precision finding
`search` for typed queries with ranking. `advanced_search` for filters like
"unwatched sci-fi after 2010 in 4K with DTS audio". `suggest` completes a
half-typed title. `recent_searches` recalls what you looked for.
`save_search` persists a filter you reuse ("kids movies under 90 minutes").

### plex_streaming — the living room
`list_sessions` shows every active playback: who, what, where, progress,
direct play vs transcode, bandwidth. `list_clients` shows controllable
devices. `play`, `pause`, `stop`, `seek`, `skip_next`, `skip_previous` drive
a chosen client. `set_quality` and `set_volume` tune a session. `control`
sends anything else the player accepts. Stopping another person's stream is
a social act — the assistant confirms first.

### plex_server — the machine
`status` (reachable? version? how busy?), `info` (configuration and
capabilities), `health` (transcoder, storage, library depth). `maintenance`
runs housekeeping. `restart` and `update` interrupt all playback — the
assistant announces downtime and confirms before either.

### plex_user — the household
`list` everyone with access, `get` one account in depth. `create` invites
with a role: `owner`, `admin`, `user`, `managed` (kids profiles), `shared`
(guests). `update_permissions` adjusts libraries per user. `delete` revokes —
check `user_activity` first so you do not strand someone mid-season.

### plex_playlist — mixes
`list` and `get` to inspect, `create` with a title plus `rating_key` items,
`add_items`/`remove_items` to evolve, `update` to rename, `delete` to drop.
`get_analytics` profiles a playlist (decades, genres, runtime) before you
share it or split it in two.

### plex_collections — shelves and franchises
Like playlists but for library-level grouping: franchises, moods, staff
picks, "unwatched 4K". Same verbs: `list`, `get`, `create`, `update`,
`delete`, `add_items`, `remove_items`.

### plex_metadata — fixing wrong data
Plex mismatches a title (wrong year, wrong show)? `match` lists candidate
agent hits, `fix_match` anchors the right one, `refresh` pulls art and cast.
`analyze` explains why an item looks wrong. `update` hand-edits fields and
locks them against future refreshes. `refresh_all` re-pulls a whole library
— slow, scoped, announced in advance. `organize` applies naming and
agent consistency fixes.

### plex_organization — whole-library hygiene
`analyze` audits a library: duplicates, naming drift, missing matches,
empty trash candidates. `organize` and `fix_issues` apply the findings.
`clean_bundles` and `optimize_database` are janitor passes for metadata
bloat — run in maintenance windows; the database locks briefly.

### plex_performance — smooth playback
Three getters before any setter: `get_transcode_settings`,
`get_transcoding_status`, `get_bandwidth`, plus `get_server_status`,
`get_server_info`, `get_health`. Then, if needed: `update_transcode_settings`,
`set_quality`, `get_throttling`/`set_throttling`, and profile management
(`list_profiles`, `create_profile`, `delete_profile`). Raising quality on an
underpowered host buffers every concurrent stream — change, then watch one
session before calling it done.

### plex_quality — conversion targets
Profiles are resolution/bitrate ladders for optimized versions.
`list_profiles`, `get_profile`, `create_profile`, `update_profile`,
`delete_profile`, `set_default` for what new conversions target.

### plex_reporting — know your library
`library_stats` (sizes, types, growth), `content_report` (codecs,
resolutions, genres — finds "everything still in 720p"),
`user_activity` (who watches what, peak concurrency), `usage_report` and
`performance_report` (load over time), `export_report` to `json`, `csv`, or
`html` for spreadsheets and sharing.

### plex_rag — ask in plain language
`status` tells you whether the semantic index exists and how big it is.
First run needs `sync_metadata` (minutes to hours on big libraries — start
it and come back). Then `semantic_search` understands intent: "slow-burn
sci-fi about memory", "cozy mysteries set in villages". `sync_subtitles`
indexes SRT/VTT tracks; `search_subtitles` then finds exact quotes and
scenes ("the 'friendship' speech in episode 4").

### plex_taste — recommendations from your history
`status` shows whether a profile exists. `rebuild_from_history` builds it
once from Plex watch history (reads only, changes nothing). `sync` folds in
new watches. `profile` and `temporal_profile` show what the model believes
about you; `recent_shifts` catches drift ("you suddenly watch a lot of
horror"). `dimensions_for`, `score_item`, and `score_library` rank
candidates — ask "what should I watch?" and get reasons, not just titles.

### plex_media_enrichment — deep dossiers
`enrich` (one item) or `bulk_enrich` (a library, overnight) fuse Wikipedia,
TMDB, JustWatch, and optional LLM synthesis into a dossier cached 90 days.
`get_enrichment` reads it back, `get_related` suggests the double feature,
`search_by_theme` ("heist films about jazz") and `search_by_person` widen
the net, `stale_report` lists dossiers due for refresh.
`get_external_metadata` pulls one provider layer raw. Type filters `movie`
and `show` scope bulk runs.

### plex_integration — beyond Plex
`list_integrations` shows wired bridges. `vienna_recommendations` and
`european_content` curate regional picks. `anime_season_info` takes
`winter`, `spring`, `summer`, or `fall` for seasonal charts. `configure`
and `sync` manage export/import and watch-state bridges.

### plex_audio_mgr — music
`list_streams` and `select_stream` for multi-track audio, `get_volume` /
`set_volume` / `mute` / `unmute` for levels, `handover` to move music
between clients without stopping it.

### plex_ffmpeg_mgr — surgery
`probe` first (streams, codecs, offsets), then `sync_audio`,
`sync_subtitles`, `extract_subtitles`, `extract_audio`, `extract_clip`,
`set_aspect`. `revert` undoes. Originals stay until you approve deletion —
transcodes are a choice, not an accident.

### arr_stack — the download shelf
`status` returns version, reachability, and queue depth for each configured
Radarr/Sonarr/Lidarr. Unconfigured apps return setup hints, not errors.
Read-only by design: queue surgery happens in each app's own UI.

### plex_help — when lost
`help` overviews the ecosystem, `list_tools` enumerates (filter by
`category`), `tool_info` needs a `tool_name` for syntax and operations,
`examples` shows few-shot usage, `api_docs` returns the running backend's
Swagger/ReDoc/OpenAPI URLs.

### plex_shutdown — stopping
`status` reports the server process and daemon probe URL. `shutdown` exits
~500 ms after responding. Only on explicit request.

### Sampling tools — multi-step autonomy
`agentic_plex_workflow` takes a `workflow_prompt`, an `available_tools`
allow-list of exact tool names, and `max_iterations` (5–10 typical) and
executes real plans ("organize my library", "fix all missing posters").
`plex_natural_assistant` answers single questions with no tools. Both need
host sampling or a local endpoint (`PLEX_SAMPLING_BASE_URL`); without
either, the assistant says so and works step by step with you instead.

## 4. Fifteen end-to-end scenarios

1. **Movie night, no scrolling.** "Pick something." Taste scores the library,
   RAG cross-checks the mood ("not horror"), collections saves the shortlist.
2. **The wrong-year twin.** Two films share a title; `match` lists both
   years, `fix_match` anchors, `refresh` restores art.
3. **New drive day.** Files land on disk → `scan` → `refresh` → `get_recent`
   confirms → `bulk_enrich` overnight for dossiers.
4. **Buffering complaint.** `get_transcoding_status` + `get_bandwidth` during
   the stutter → lower `set_quality` or `set_throttling`, verify one session.
5. **Guest weekend.** `create` a `shared` user with two libraries, `update`
   restrictions; `delete` after checkout.
6. **Kids shelf.** `advanced_search` (animation, under PG, under 100 min) →
   `create` collection → pin it in their client.
7. **Quote hunt.** "The speech about the ocean in episode 4" →
   `search_subtitles` → timestamp → `play` with seek.
8. **Franchise order.** "Bond in order" → `search_by_person` + `get_related`
   → collection in release order.
9. **Dead weight audit.** `content_report` (720p, unwatched 2 years) →
   confirm → upgrade or remove.
10. **Viewing report.** `user_activity` monthly → peak concurrency → decide
    whether the host needs more CPU or the `shared` accounts need pruning.
11. **Anime season.** `anime_season_info` for the current season → cross-check
    against libraries → shopping list for Sonarr's own UI.
12. **Music migration.** `list_streams` across the music library →
    `select_stream` FLAC where available → `handover` to the living-room client.
13. **Subtitle rescue.** Out-of-sync subs → `sync_subtitles` with offset →
    `extract_subtitles` for the archive.
14. **Pre-holiday maintenance.** `analyze` → `fix_issues` → `optimize_database`
    → `empty_trash` (confirmed) → `update` PMS after everyone sleeps.
15. **Fresh install.** Status → list → PIN token → test → sync_metadata →
    rebuild taste → first recommendation. (Full walkthrough:
    webapp `docs/ONBOARDING.md`.)

## 5. Troubleshooting

| Symptom | Likely cause | Ask for |
|---|---|---|
| 401 / unauthorized | Token wrong, revoked, or for another server | Token regeneration via PIN flow |
| Connection refused | PMS down, wrong URL, firewall on 32400 | `status`, then URL check |
| Empty search, full library | RAG index missing/stale | `plex_rag status`, then sync |
| Wrong posters/titles | Agent mismatch | `match` + `fix_match` + `refresh` |
| Buffering on one client | Transcode overload or weak network | Transcoding status + bandwidth |
| Slow first answer | Cold MCP mount (~90s) or cold index | Patience once, then `/mcp/status` |
| Tool says NOT_IMPLEMENTED | Plex API has no such path | Nearest working alternative |
| "I can't do multi-step" | No sampling available | Step-by-step mode or set `PLEX_SAMPLING_BASE_URL` |

## 6. FAQ

**Do you delete my files?** Library `delete` removes the Plex record, not
files; `empty_trash` drops vanished items after confirmation. File deletion
is never implicit.

**Do you watch my history?** Taste reads watch history only to recommend.
It never modifies, shares, or exports it. `sync` only folds in new watches.

**Why confirm destructive actions?** Because `empty_trash`, `restart`,
`update`, and bulk rewrites cannot be undone from inside Plex. Reads and
searches never ask — only mutations with blast radius do.

**Webapp or chat?** Same backend, same tools. The dashboard (Overview,
Inbox, Tools, Skills, Chat, Settings, Help, Logs) visualizes what chat
does in words. Use whichever fits the moment.

**Which endpoints are current?** Canonical REST lives under `/api/*`
(`/api/status`, `/api/capabilities`, `/api/diagnostics`, `/api/skills`).
`/api/v1/diagnostics` is kept for smoke tests, `/api/system/diagnostics`
for the rich Settings check, and `/api/v1/search` + `/api/v1/chat` are
deprecated in favor of `/api/rag/*` and `/api/llm/*`.

## 7. Webapp tour (every page, what it shows)

- **Overview** — hero, red onboarding button (until Plex connects), six KPI
  cards (libraries, server, enriched dossiers, semantic index, taste, LLM),
  quick actions, library preview, *arr card.
- **Inbox** — now-playing sessions plus a filterable library list. The
  "what needs attention" view; check it first when something feels off.
- **Libraries / Movies / Media** — browse sections and items down to the
  per-title dossier with posters, cast, parts, and actions.
- **Search** — keyword search with library scope; **Semantic search** needs
  the RAG index and understands intent.
- **RAG Management** — index status, `sync_metadata` / `sync_subtitles`
  triggers, vector counts. Start here when semantic answers go thin.
- **Enrichment** — single and bulk dossiers, theme/person search, stale
  report. Overnight bulk runs live here.
- **Taste** — profile status, rebuild, sync, ranked picks, recent shifts.
- **Chat** — local or cloud LLM with skill-first prompts, personalities,
  refine-before-send, Markdown/JSON export.
- **Tools** — the raw MCP surface: categories, canonical REST index, legacy
  aliases. What agents see, visualized.
- **Skills** — the four prompts and two resources chat loads first, with
  "use when" guidance.
- **Server** — PMS info plus raw JSON for power users.
- **Logs** — backend log tail with substring filter, level picker, and line
  cap. Paste the red lines back into chat when reporting a bug.
- **API Docs** — Swagger UI / ReDoc iframes plus a quick-ref strip of every
  current endpoint.
- **Settings** — Plex (URL, token, PIN flow, test), LLM (providers, keys,
  models, GPU residents), *arr URLs and keys, RAG controls. Saved overrides
  beat `.env` files — restart the backend after changing them.
- **Help** — this manual's sibling: MCP, webapp, Plex, ecosystem, and *arr
  primers in one tabbed page.

## 8. Settings reference

**Plex group.** `plex_url` (base URL, no trailing path), `plex_token`
(X-Plex-Token). Buttons: Test connection (live `/identity` probe with a
plain-language verdict), Get a new token (PIN flow: code → approve at
app.plex.tv → token saves itself). Status line shows configured vs missing.

**LLM group.** Provider cards: local engines (Ollama default
`http://127.0.0.1:11434`, LM Studio, vLLM — no key, just running) versus
cloud (OpenAI, Anthropic, DeepSeek, OpenRouter — key per provider, Test
button, saved to the 0600 keystore, never to chat logs). Model dropdown
lists live models with a curated fallback offline. GPU panel shows Ollama
residents and VRAM with an Evict-all button for when a big job needs room.

**\*arr group.** Base URL plus API key per app (Radarr, Sonarr, Lidarr).
Enter the same URL you open in a browser from the backend machine. Keys
live under each app's Settings → General → Security. Unreachable-but-
configured apps report warn, not error — check the app itself.

**RAG group.** Reindex buttons (metadata, subtitles), index stats, embed
model note. Reindex after adding large batches of files.

## 9. Tokens and security

Your Plex token is a password-equivalent: anyone holding it can browse and
control your server. Rules the bundle enforces: tokens travel in environment
variables and the backend keystore only; the PIN flow exists so you approve
access at app.plex.tv without ever displaying the token; the assistant never
prints tokens and never asks you to paste one into chat when the webapp flow
is available; `.env` files are gitignored and the Tauri bundle ships
`.env.example`, never a real `.env`. Rotate (regenerate) the token if it was
ever posted anywhere — assume shared means compromised. Cloud LLM keys get
the same treatment: per-provider keystore, Test buttons, env override wins.

## 10. RAG indexing guide

Semantic search only answers from the index. Build it once per library set:
RAG page → Reindex metadata (progress bar, phase readout) → verify counts
in `status` → try three of your own phrases before trusting it. Subtitles
are a second, separate index (`sync_subtitles`) for quote-level search.
Reindex when: you add hundreds of files, semantic answers feel thin, or
`stale` counts climb. Big libraries index over hours — queue overnight and
check the phase in the morning. Keyword search never needs the index, so
nothing else stops while it builds.

## 11. Taste guide

Taste learns from what you finished, rewatched, abandoned, and rated — plus
when (late-night horror vs Sunday documentaries). Build once
(`rebuild_from_history`), then `sync` weekly or let the backend interval do
it. `recent_shifts` is the interesting view: it catches phases before you
notice them. `score_library` answers "tonight" with reasons tied to
dimensions you can inspect (`dimensions_for`). A profile is a mirror, not a
cage: browse outside it freely; it only ranks, it never hides. Rebuild from
scratch after a household change (kids' viewing swamps yours) rather than
fighting the old signal.

## 12. Glossary

- **rating_key** — Plex's id for one item; every detail/enrich/score call needs it.
- **library_id / section** — one shelf (Movies, TV, Music); types movie/show/music/photo.
- **Portmanteau** — one tool per domain with an `operation` switch (this bundle's shape).
- **Direct play** — client plays the file as-is; **transcode** — server converts live.
- **Dossier** — fused Wikipedia/TMDB/JustWatch (+LLM) record per title, cached 90 days.
- **PIN flow** — approve-at-plex.tv token grant; no copy-paste.
- **RAG** — retrieval-augmented search over your indexed metadata and subtitles.
- **Taste profile** — learned preference model from watch history.
- **\*arr** — Radarr/Sonarr/Lidarr download organizers (optional companions).
- **Prefabs** — interactive cards some tools return alongside text answers.

## 13. Twenty questions, answered in one line each

1. "Is Plex up?" → status call, version plus load in reply.
2. "What libraries exist?" → section list with sizes.
3. "Add my new drive." → add_location, then scan, then count check.
4. "Where did my movie go?" → search, then trash/duplicate audit.
5. "Play it in the living room." → clients list, then play with ids.
6. "Pause everything." → sessions list, pause each with confirmation.
7. "Who is watching?" → sessions plus user activity.
8. "Make a workout mix." → search tracks, create playlist, analytics check.
9. "Franchise shelf?" → search titles, create collection, file them in.
10. "Wrong movie shown." → match candidates, anchor, refresh, verify art.
11. "No subtitles." → list streams, select or extract, sync offset.
12. "It buffers." → transcoding status plus bandwidth, lower quality, verify.
13. "What is new?" → recent additions feed.
14. "Surprise me." → taste scoring with stated reasons.
15. "More like this." → related plus theme search.
16. "How much do we watch?" → monthly activity and concurrency peaks.
17. "Is Sonarr stuck?" → arr queue snapshot, then Sonarr's own UI.
18. "Clean up." → analyze, fix, optimize, confirmed empty-trash.
19. "Back it up?" → settings and database locations, copy while stopped.
20. "Start over." → rebuild taste, reindex RAG, rescan libraries — in that order.

## 14. Address and shortcut cheat sheet

- Backend API `http://127.0.0.1:10740`, docs at `/docs`, health at `/health`.
- Frontend `http://127.0.0.1:10741`; sidebar reaches every page.
- Canonical discovery: `/api/capabilities` (tools plus endpoint index),
  `/api/status` (rich status), `/api/diagnostics` (machine checks),
  `/api/skills` (prompts plus resources).
- Settings PIN flow beats token paste; Test buttons beat assumptions; the
  red onboarding button beats guessing what is missing.
- Overnight jobs: bulk enrich, subtitle sync, metadata sync. Maintenance
  window jobs: optimize, empty trash, PMS update. Anytime jobs: everything
  read-only.

## 15. Ten household playbooks

1. **New parents.** Create `managed` profiles for night feeds, cap libraries
   to animation plus comfort shows, save a "90 minutes or less" search, set a
   tablet quality profile as default. Revisit in six months.
2. **Film club.** One collection per month ("October: paranoia thrillers"),
   usage report after each screening for attendance, taste scoring for the
   next pick, export the season to HTML for the group chat.
3. **Server move.** Add the new drive location alongside the old, scan,
   verify counts match, then remove the old location and empty trash. Never
   remove-then-add; the gap orphans watch state.
4. **In-law visit.** Temporary `shared` user, two libraries, Kids shelf
   pinned, delete on departure. Check sessions once so nothing buffers at
   dinner.
5. **4K upgrade.** Content report for 720p titles you actually rewatch (taste
   score plus play counts), upgrade those first, set the 4K profile default
   only after the host proves it transcodes one stream cleanly.
6. **Music household.** Audit streams for FLAC, hand the living-room client
   over at parties, mute versus pause etiquette for doorbells.
7. **Anime season.** Seasonal chart, cross-check owned versus missing, shopping
   list out (Sonarr handles acquisition elsewhere), seasonal collection in.
8. **Horror October.** Theme search for dread, sub-genres split across two
   collections (supernatural, slashers), recent-shifts watch so November can
   revert to comfort viewing.
9. **Data cap month.** Throttle remote quality, prefer direct play on LAN,
   postpone bulk enrichment and subtitle sync to next cycle, check bandwidth
   weekly.
10. **Spring cleaning.** Analyze every library, fix matches, dedupe, optimize
    the database, confirm empty-trash with counts, export a before/after
    library-stats pair. One evening, once a year, done.

## 16. Power-user reference (every tool, every operation)

Ask with these verbs when you want zero ambiguity. Destructive operations
are marked with (!) — the assistant confirms those before running them.

- **plex_library** — list, get, list_items, create, update, delete (!),
  scan, refresh, optimize, empty_trash (!), add_location, remove_location
  (!), clean_bundles.
- **plex_media** — browse, search, get_details, get_recent, get_stream_url,
  update_metadata.
- **plex_search** — search, advanced_search, suggest, recent_searches,
  save_search.
- **plex_streaming** — list_sessions, list_clients, play, pause, stop,
  seek, skip_next, skip_previous, set_quality, set_volume, control.
- **plex_server** — status, info, health, maintenance, restart (!),
  update (!).
- **plex_user** — list, get, create, update, delete (!),
  update_permissions.
- **plex_playlist** — list, get, create, update, delete (!), add_items,
  remove_items, get_analytics.
- **plex_collections** — list, get, create, update, delete (!), add_items,
  remove_items.
- **plex_metadata** — analyze, match, fix_match, refresh, refresh_all
  (slow), update, organize.
- **plex_organization** — analyze, organize, fix_issues, clean_bundles,
  optimize_database (maintenance window).
- **plex_performance** — get_server_status, get_server_info, get_health,
  get_transcode_settings, update_transcode_settings, get_transcoding_status,
  get_bandwidth, set_quality, get_throttling, set_throttling, list_profiles,
  create_profile, delete_profile.
- **plex_quality** — list_profiles, get_profile, create_profile,
  update_profile, delete_profile, set_default.
- **plex_reporting** — library_stats, content_report, user_activity,
  usage_report, performance_report, export_report (json, csv, html).
- **plex_rag** — status, sync_metadata (slow, once), sync_subtitles,
  semantic_search, search_subtitles.
- **plex_taste** — status, rebuild_from_history (once), sync, profile,
  temporal_profile, recent_shifts, dimensions_for, score_item,
  score_library.
- **plex_media_enrichment** — enrich, enrich_item, get_enrichment,
  get_external_metadata, get_related, search_by_theme, search_by_person,
  analyze_trends, bulk_enrich (overnight), stale_report.
- **plex_integration** — list_integrations, vienna_recommendations,
  european_content, anime_season_info (winter, spring, summer, fall),
  configure, sync.
- **plex_audio_mgr** — list_streams, select_stream, get_volume, set_volume,
  mute, unmute, handover.
- **plex_ffmpeg_mgr** — probe (always first), sync_audio, sync_subtitles,
  extract_subtitles, extract_audio, extract_clip, set_aspect, revert.
- **arr_stack** — status (read-only snapshot, never downloads).
- **plex_help** — help, list_tools, tool_info, examples, api_docs.
- **plex_shutdown** — status, shutdown (!) (explicit request only).
- **agentic_plex_workflow** — orchestrate (needs sampling or local LLM
  endpoint; allow-list exact tool names; 5–10 iterations typical).
- **plex_natural_assistant** — answer (concepts and explanations, no tools).

Pair the verb with its object ("plex_library scan on library 1", "taste
score_library for tonight") and the assistant executes without follow-up
questions unless a (!) confirmation applies.

## 17. Chat versus dashboard (when to switch)

Chat wins for intent ("something like Dark but funnier"), cross-domain plans
("audit then clean"), and anything you would say out loud. The dashboard
wins for browsing (posters beat filenames), comparing (KPI cards side by
side), long jobs (progress bars beat polling), and evidence (export the CSV,
screenshot the chart). Practical splits: pick tonight's film in chat, build
the shelf in Collections; diagnose buffering in chat, watch the bandwidth
graph on Server; ask for the dossier in chat, read it on the media page;
plan cleanup in chat, run it from Inbox and Repair with filters. Logs belong
to the dashboard (tail, filter, level), verdicts belong to chat ("the 401 at
21:04 is a revoked token — regenerate via PIN"). Neither replaces the other:
the Tools page shows exactly what chat can call, and the Skills page shows
what chat loads first — check both when an answer surprises you.

Start every fresh install the same way: status, library list, PIN token,
test connection, overnight index. Everything after that is preference.
Keep tokens in the keystore, confirmations before destruction, and curiosity
before assumptions — the library rewards all three.

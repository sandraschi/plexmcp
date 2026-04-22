# plex-mcp — Roadmap (Next Phase)

**Status:** planning, April 2026
**Author:** Claude Opus 4.7 (Anthropic), in collaboration with Sandra Schipal
**Repository:** `D:\Dev\repos\plex-mcp`
**Current version:** 2.4.1

---

## Where we are

As of v2.4.1 (April 2026), plex-mcp is a FastMCP 3.2 server with:

- 19 portmanteau tools covering libraries, media, search, streaming,
  performance, playlists, users, server health, reporting
- Simultaneous stdio + HTTP transport
- LanceDB semantic search (`plex_rag`) indexed against Plex metadata
- Wikipedia enrichment (`plex_media_enrichment`)
- Sampling-based natural assistant (`plex_natural_assistant`)
- Webapp on ports 10741/10742 with dashboard, library browsing,
  search, chat
- Optional *arr stack read-only integration

Used nightly by Sandra against a library of ~50,000+ video items
(movies, TV episodes, documentaries, misc).

## Where Plex itself falls short

Plex is sluggish in the AI department. What it has:

- Plex Sonic (music)
- Some ML-based thumbnail selection
- Intro/outro detection (partial, only some shows)
- Related-title row via TMDB genre/tag similarity

What it doesn't have, and at 50k videos needs:

1. **Semantic browsing.** Keyword search only. No "that French heist
   film from the 70s with the jazz soundtrack."
2. **Deep metadata.** TMDB/TVDB dump. No critical context, no
   production trivia, no "why this matters in film history."
3. **Cross-library intelligence.** Movies and TV are isolated. No
   "documentaries about the director of this fiction film."
4. **Subtitle search.** Doesn't exist usefully. "Find the episode
   where X says Y" — impossible.
5. **Mood and taste routing.** Can't filter by "no graphic violence
   tonight" beyond blunt MPAA rating.
6. **Taste modelling.** Watch history exists but isn't used to infer
   what Sandra actually likes versus tolerates.
7. **Context-aware recommendations.** "What should I watch next" is
   TMDB-similar, not library-state-aware.
8. **Episode-level intelligence.** 200 episodes of a show is opaque.
   Can't ask "which episode introduces the antagonist."

Plex itself is not going to close these gaps soon. That's our opening.

## The projects

Each project has its own spec in `docs/plans/`. Each is independent.

| # | Project                         | Spec                                  | Effort | Daily-use impact |
|---|---------------------------------|---------------------------------------|--------|------------------|
| 1 | Deep metadata enrichment        | `DEEP_METADATA_ENRICHMENT.md`         | 3–4 d  | High             |
| 2 | Subtitle RAG                    | `SUBTITLE_RAG.md`                     | 4–5 d  | Very high        |
| 3 | Taste modelling                 | `TASTE_MODELLING.md`                  | 2–3 d  | High             |
| 4 | Mood-based nightly picker       | `MOOD_PICKER.md`                      | 1–2 d  | High             |
| 5 | Episode-level intelligence      | `EPISODE_INTELLIGENCE.md`             | 3–4 d  | Medium           |
| 6 | Cross-library linking           | `CROSS_LIBRARY_LINKS.md`              | 2 d    | Medium           |

**Recommended order:** 1 → 3 → 4 → 2 → 5 → 6.

Rationale: metadata enrichment (1) and taste modelling (3) are
foundations — they produce the data that makes everything else
smarter. Mood picker (4) is the daily-use payoff and uses both.
Subtitle RAG (2) is high-value but genuinely hard (transcription
storage, chunking, alignment to timecodes); fit it in after the
foundations ship. Episode intelligence (5) and cross-library (6)
are polish tier.

## Why this order

**Deep metadata enrichment first** because everything downstream
improves when metadata is richer. Plex stores genre tags and
synopses; we want cast roles with context, production background,
critical reception, thematic description, content warnings beyond
MPAA. Every other feature benefits.

**Taste modelling next** because it's a small project (2-3 days) and
it unlocks proper recommendations. Watch history + ratings + implicit
signals (rewatching, completing vs abandoning, time-of-day preferences)
feeds a per-user taste profile that downstream features consume.

**Mood-based nightly picker** because that IS the daily use case.
Sandra watches something most nights. The question "what should I
put on tonight" is the feature that earns its keep fastest. With
enrichment + taste in place, this becomes good instead of
heuristic.

**Subtitle RAG** comes fourth because it's ambitious and touches
infrastructure the others don't (Whisper transcription of untitled
video, subtitle file ingestion, alignment to timecodes, search UI
that surfaces clips with seek links). Worth doing, not first.

**Episode intelligence** adds per-episode summaries, character
arcs, continuity maps for long-running shows. High value for
specific users (re-watchers, analysts) but not a nightly-driver
feature.

**Cross-library linking** is connective tissue: surface that the
director of movie X also made documentary Y that you also own.
Uses existing enrichment data, adds no new infrastructure.

## What's deliberately not in this roadmap

**Transcoding optimization.** Plex does this. We're not in the
codec business.

**Replacing the Plex clients.** The Plex apps on TV/phone/web are
what they are. We don't build clients; we build intelligence that
a Plex client (via the webapp or direct MCP) can surface.

**Live TV / DVR features.** Not Sandra's use case. Scope creep.

**Sharing / social.** Personal library. No.

**Piracy tooling.** Legal grey-area stuff (automated acquisition
pipelines beyond the *arr read-only status we already have) stays
out.

**Deep learning on video content itself.** Computer vision on
frames, automatic scene detection, face recognition across the
library. Would need enormous GPU time on the 4090 that's already
serving Ollama + TTS. Maybe someday; not this roadmap.

## Assumptions and constraints

- FastMCP 3.2 framework
- SQLite for all persistent state (alongside LanceDB for vectors)
- Ollama primary (Gemma 3 12B default), webapp escalates to
  Gemini/Claude for hard work
- No new required external deps without strong justification
- Ports 10741/10742 stay
- Budget: Sandra's ~€100/month covers Gemini API for occasional
  deep synthesis; bulk work runs locally

## Success criteria

One month after all six ship:

- Sandra runs the nightly picker at least 15/30 nights and finds
  the suggestion acceptable
- Semantic browse queries (not just keyword) produce useful
  results
- Sandra rediscovers at least 5 library items she'd forgotten
- Subtitle search answers "which episode was that scene" for at
  least 3 actual queries
- Metadata pages feel as rich as IMDB/Letterboxd for any given
  film, without leaving Plex

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

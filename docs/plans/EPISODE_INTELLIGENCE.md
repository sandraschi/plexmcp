# Episode-Level Intelligence — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 3–4 days
**Priority:** 5 of 6

---

## The problem

Series have a scale issue. A 200-episode show has 200 summaries to
absorb, 50-100 characters to track, plot arcs that span seasons,
and continuity that's easy to lose. Plex treats each episode as an
opaque item with synopsis + thumbnail.

Sandra re-watches shows. She also abandons shows mid-run and
returns years later. Both cases want per-episode intelligence that
Plex doesn't provide:

- Rich per-episode summaries (non-spoiler AND spoiler versions)
- Character arc tracking: when does each character appear, what's
  their arc
- Continuity notes: "this episode references events from S02E04"
- "Best episode to introduce someone" / "best stand-alone episode"
- Episode ratings consolidated (IMDB, TVDB, fan opinion)
- "What do I need to remember to watch this" after a long break

## Data sources

- **TVDB** — per-episode basic metadata already
- **IMDB** — per-episode ratings and summaries
- **Wikipedia** — per-episode pages for major shows
- **Fan wikis** — Fandom pages for show-specific wikis
  (Game of Thrones, Breaking Bad, etc.)

Fan wikis are gold for long-running shows. They have:
- Per-episode summaries with continuity flags
- Character-episode appearance matrices
- Location tracking, prop tracking, callback documentation
- Fan episode rankings

## Data model

```sql
CREATE TABLE IF NOT EXISTS episode_enrichment (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    plex_rating_key         TEXT NOT NULL UNIQUE,
    show_rating_key         TEXT NOT NULL,
    season_number           INTEGER,
    episode_number          INTEGER,
    title                   TEXT,
    summary_short           TEXT,       -- non-spoiler
    summary_full            TEXT,       -- spoiler
    continuity_references   TEXT,       -- JSON array of {type, target_ep, detail}
    characters_present      TEXT,       -- JSON array of character names
    characters_introduced   TEXT,       -- JSON array
    characters_last_seen    TEXT,       -- JSON array
    key_plot_beats          TEXT,       -- JSON array
    fan_rating              REAL,
    imdb_rating             REAL,
    production_notes        TEXT,
    fetched_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_episode_show
    ON episode_enrichment(show_rating_key, season_number, episode_number);

CREATE TABLE IF NOT EXISTS show_characters (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    show_rating_key     TEXT NOT NULL,
    character_name      TEXT NOT NULL,
    actor_name          TEXT,
    first_episode       TEXT,       -- rating_key
    last_episode        TEXT,
    episode_count       INTEGER,
    arc_summary         TEXT,       -- LLM-generated arc
    UNIQUE(show_rating_key, character_name)
);
```

## Implementation

### Phase 1 — Episode enrichment pipeline (1-2 days)

`src/plex_mcp/services/episode_enrichment.py`:

```python
async def enrich_episode(rating_key: str) -> EpisodeEnrichment:
    """Enrich a single episode with external sources + LLM synthesis."""

    plex_meta = get_plex_episode_metadata(rating_key)
    show_meta = get_plex_show_metadata(plex_meta.show_rating_key)

    # Fetch
    tvdb = fetch_tvdb_episode(show_meta, plex_meta)
    imdb = fetch_imdb_episode(show_meta, plex_meta)
    wiki = fetch_wikipedia_episode(show_meta, plex_meta)
    fandom = fetch_fandom_episode(show_meta, plex_meta)

    raw = merge_sources(tvdb, imdb, wiki, fandom)

    # LLM synthesis — generates the structured fields
    synthesis = await synthesise_episode(plex_meta, show_meta, raw)

    save_episode_enrichment(rating_key, synthesis, raw)
    return synthesis
```

Fan wiki detection: try common Fandom URLs based on show title,
cache hits, gracefully miss.

### Phase 2 — Show-level arc synthesis (1 day)

After all episodes of a season are enriched, synthesise
season-level metadata:

- Season arc summary
- Character arc per season (who rises, who falls)
- "Best episode of this season" recommendation

After all seasons, synthesise show-level:

- Overall quality arc (season 1 vs season 5)
- "Where does this show peak"
- "Stand-alone episodes" list for introducing newcomers

### Phase 3 — MCP tools (half day)

Add `plex_episode_intelligence` portmanteau:

| Operation                     | Purpose                                   |
|------------------------------|-------------------------------------------|
| `enrich_episode`             | Single episode enrichment                  |
| `enrich_season`              | All episodes of a season                   |
| `enrich_show`                | Full show, careful about scale             |
| `get_episode`                | Cached enrichment                          |
| `character_arc`              | Arc for specific character                 |
| `recap_before_watching`      | "What do I need to remember to watch E12"  |
| `best_episode_for_newcomer`  | Recommend stand-alone intro episode        |
| `compare_seasons`            | Which season is best, by various metrics   |

### Phase 4 — "Recap before watching" (half day)

Specific LLM-powered feature worth calling out. User is about to
watch S04E07 after a long gap. Query:

```python
def recap_before_watching(rating_key: str,
                           since_last_watched_days: int = None) -> str:
    """Generate a 'what you need to remember' summary."""

    episode = get_episode_enrichment(rating_key)
    show = get_show_context(episode.show_rating_key)

    # Recent episodes user has watched in this show
    recent = get_recent_watched(episode.show_rating_key, limit=5)

    context = {
        'upcoming_episode': episode,
        'recent_user_watches': recent,
        'show_so_far': show.summary_up_to(episode),
        'active_plot_threads': show.active_threads_at(episode),
    }

    return llm_generate_recap(context)
```

Output is a 2-3 paragraph primer: "Last time in {show}: {plot
state}. Active threads: {...}. Characters to remember: {...}."

### Phase 5 — REST + frontend (1 day)

```
POST /api/episodes/enrich/{rating_key}
POST /api/episodes/enrich-season/{show}/{season}
POST /api/episodes/enrich-show/{show}
GET  /api/episodes/{rating_key}
GET  /api/episodes/{rating_key}/recap
GET  /api/shows/{show}/character/{name}
GET  /api/shows/{show}/best-newcomer-episode
GET  /api/shows/{show}/arc
```

Frontend: enhance show/season/episode detail pages with:
- Episode cards showing short summary + fan rating badge
- "Recap before watching" button on episode detail
- Character arc page linked from show detail
- Season-quality sparkline for long shows

## Gotchas

- **Spoiler containment.** Two summary fields (short non-spoiler,
  full spoiler). UI defaults to non-spoiler; explicit toggle for
  full. Content warnings when toggling.

- **Fandom wiki scraping is brittle.** URLs change, structure
  varies. Tolerate failures gracefully.

- **LLM cost for long shows.** A 200-episode show is 200 LLM
  synthesis calls plus season summaries. Prioritize: user's
  currently-watching shows first, completed shows only when
  requested.

- **Characters with common names.** "John" in Breaking Bad vs
  "John" in Better Call Saul. Namespace character tracking by
  show.

- **Cross-show references.** Some shows reference others
  (spin-offs, shared universes). Out of scope for this project —
  the cross-library project (#6) handles that.

- **Data stale for ongoing shows.** Weekly shows need
  incremental updates. Run enrichment for newly-aired episodes on
  a schedule (if Sandra has any currently-airing shows).

- **Storage.** 50k video items probably includes maybe 30k
  episodes if TV-heavy. 30k episode rows with ~10KB JSON each =
  300MB. Fine.

## Testing

1. Enrich a well-documented show (Breaking Bad, Game of Thrones)
2. Spot-check per-episode summaries against Wikipedia
3. Run recap feature on an episode in the middle of a season after
   simulating a "year gap" — is the recap useful?
4. Character arc for a main character — is it accurate?

## Update on completion

- CHANGELOG
- docs/plans/README.md
- FLEET_INDEX.md

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

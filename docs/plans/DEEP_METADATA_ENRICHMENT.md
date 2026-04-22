# Deep Metadata Enrichment — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 3–4 days
**Priority:** 1 of 6 — build this first

---

## The problem

Plex stores metadata from TMDB/TVDB: title, year, genre, synopsis,
cast list, poster. That's it. For a library of 50k items, every
page looks the same and every synopsis reads the same — competent
marketing copy, no substance.

The experience of "pointing at a video" on Plex gives you no more
than "pointing at a video" on Netflix. For a personal library of
50k curated items, that's a waste. Sandra has chosen these films
deliberately. She wants more when she lands on one.

## What we want instead

When Sandra selects a movie in Plex (or in the webapp), she sees:

- The TMDB synopsis (what we have)
- A 3-4 paragraph critical overview: context, significance, legacy,
  what makes this film worth watching
- Director's filmography with other films she owns highlighted
- Primary cast members with their roles in THIS film (not a flat
  list) and other roles in films she owns
- Production trivia: budget, critical reception at release, major
  awards, any notable behind-the-scenes
- Thematic description beyond genre tags: what this film is
  actually about
- Honest content warnings (violence intensity, explicit content,
  specific triggers if applicable) beyond MPAA
- For TV series: season-by-season quality arc, "best episode to
  introduce someone," recurring themes across seasons
- Related films the library owns (cross-reference via shared
  personnel, themes, era, movement)

This exists for famous films via Letterboxd / MUBI / Criterion /
Metacritic / Wikipedia. It doesn't exist in one place for most
films, and it certainly doesn't exist inside Plex.

## Approach

Mirror what `media_research_book` does for calibre-mcp: concurrent
multi-source fetching, local-data merging, LLM synthesis. The
calibre-mcp pattern is proven — adapt it for video.

### Sources in priority order

1. **Wikipedia** — already integrated via `plex_media_enrichment`.
   Always fetch. Structured enough to be reliable.
2. **TMDB (deep)** — we already hit TMDB for basic metadata. Deep
   mode fetches full cast+crew, production companies, release
   history, collection context, keywords.
3. **Letterboxd** — no official API. Scrape the film page for
   average rating, reviews (top reviews only), related films list.
   Rate-limit aggressively; cache heavily.
4. **IMDB** — for release-year trivia, box office, parents guide
   (content warnings). No official API; use their public JSON-LD
   on film pages.
5. **Rotten Tomatoes** — critic score and consensus only. Scrape
   carefully, cache.
6. **Metacritic** — score + top critic snippets.
7. **Criterion Collection** — if the film has a Criterion entry,
   fetch the essay excerpt. Gold-tier context for the films that
   have it.
8. **Wikipedia categories** — for thematic grouping ("films about
   X," "films from the Y movement").
9. **JustWatch** — for "where else this is available," useful
   context even though Sandra owns the file.

### What NOT to use

- **Goodreads-equivalent social sites** where the content is user
  reviews en masse. Low signal-to-noise, taste-mob affected.
- **Trakt** — overlaps with what we're building. No point.
- **Amazon/streaming-specific pages** beyond JustWatch.

## Data model

```sql
CREATE TABLE IF NOT EXISTS media_enrichment (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    plex_rating_key      TEXT NOT NULL UNIQUE,
    media_type           TEXT NOT NULL,  -- 'movie' | 'show' | 'season' | 'episode'
    title                TEXT NOT NULL,
    year                 INTEGER,
    enrichment_version   INTEGER NOT NULL DEFAULT 1,
    report               TEXT,            -- synthesised markdown
    report_sections      TEXT,            -- JSON: named sections for rendering
    sources_fetched      TEXT,            -- JSON array
    sources_failed       TEXT,            -- JSON array
    raw_data             TEXT,            -- JSON blob of raw per-source data
    fetched_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_warnings     TEXT,            -- JSON structured warnings
    themes               TEXT,            -- JSON array of thematic tags
    related_rating_keys  TEXT             -- JSON: items in library related to this
);
CREATE INDEX IF NOT EXISTS idx_enrichment_rating_key
    ON media_enrichment(plex_rating_key);
CREATE INDEX IF NOT EXISTS idx_enrichment_updated
    ON media_enrichment(updated_at);

CREATE TABLE IF NOT EXISTS person_credits (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name          TEXT NOT NULL,
    tmdb_person_id       INTEGER,
    imdb_person_id       TEXT,
    wikipedia_url        TEXT,
    bio                  TEXT,
    credits_cached_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_person_name ON person_credits(person_name);

CREATE TABLE IF NOT EXISTS enrichment_cross_refs (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    source_rating_key    TEXT NOT NULL,
    target_rating_key    TEXT NOT NULL,
    relation_type        TEXT NOT NULL,
    -- 'director' | 'shared_cast' | 'writer' | 'same_collection'
    -- | 'thematic' | 'influenced_by' | 'same_year' | 'genre_adjacent'
    relation_detail      TEXT,
    confidence           REAL DEFAULT 1.0
);
CREATE INDEX IF NOT EXISTS idx_crossrefs_source
    ON enrichment_cross_refs(source_rating_key);
```

`media_enrichment.report_sections` is the key structure for the UI.
A JSON object with named sections:

```json
{
  "synopsis": "...",
  "critical_overview": "...",
  "why_this_matters": "...",
  "production_notes": "...",
  "reception_at_release": "...",
  "legacy": "...",
  "content_warnings": {
    "violence": "moderate - some stylized action",
    "sexual_content": "none",
    "language": "mild",
    "other_triggers": ["animal harm in chapter 4"]
  },
  "thematic_tags": ["heist", "existential", "70s new wave"],
  "director_context": "...",
  "key_cast_notes": "...",
  "awards": [...],
  "trivia": [...]
}
```

Structured so the frontend renders discrete cards, not a wall of
text. Also queryable: "all films with thematic_tag 'existential'"
becomes a SQL JSON query.

## Implementation

### Phase 1 — Extend `plex_media_enrichment` (1 day)

Current tool fetches Wikipedia only. Extend to a multi-source
fetch orchestrator mirroring `media_research_book`:

**File:** `src/plex_mcp/services/enrichment/orchestrator.py`

```python
async def enrich_media_item(
    rating_key: str,
    force_refresh: bool = False,
    sources: list[str] | None = None,
    ctx: Context | None = None,
) -> EnrichmentReport:
    """Fetch from all configured sources concurrently, merge, synthesise."""

    # Gate: check cache
    if not force_refresh and has_fresh_enrichment(rating_key):
        return load_enrichment(rating_key)

    # Get Plex metadata
    plex_meta = get_plex_metadata(rating_key)

    # Concurrent fetch
    fetchers = select_fetchers(plex_meta, sources)
    results = await asyncio.gather(
        *[fetch(plex_meta) for fetch in fetchers],
        return_exceptions=True,
    )

    # Synthesise with LLM sampling
    raw = merge_source_data(results)
    report = await synthesise_report(plex_meta, raw, ctx)

    # Extract and store cross-references
    extract_cross_references(rating_key, raw)

    # Persist
    save_enrichment(rating_key, report, raw, results)

    return report
```

Per-source fetchers in `src/plex_mcp/services/enrichment/sources/`:
- `tmdb.py` (deep mode)
- `wikipedia.py` (extends current)
- `letterboxd.py` (scrape + cache)
- `imdb.py` (JSON-LD extraction)
- `rotten_tomatoes.py` (scrape + cache)
- `metacritic.py`
- `criterion.py`
- `justwatch.py`

Each fetcher: async httpx, 12s timeout, returns structured dict or
raises. Concurrent gather with return_exceptions so one failure
doesn't kill the whole enrichment.

### Phase 2 — LLM synthesis prompt engineering (half day)

The synthesis prompt is where quality lives. Template:

```
You are a thoughtful film critic preparing a dossier on a specific
film/series for a cinephile's personal library browser.

SOURCE MATERIAL (raw):
{json.dumps(merged_sources, indent=2)}

PLEX METADATA:
{plex_meta_summary}

Produce a structured JSON report with these sections:
- synopsis (2-3 sentences, non-spoiler)
- critical_overview (3-4 paragraphs: what this film is doing, why
  it matters, its position in the filmography/genre/movement)
- why_this_matters (1 paragraph: if a friend asked "should I watch
  this tonight," what's the honest case FOR watching it)
- production_notes (key behind-the-scenes facts)
- reception_at_release
- legacy (if applicable)
- content_warnings (object: violence, sexual_content, language,
  other_triggers — concrete descriptions, not MPAA codes)
- thematic_tags (3-7 short phrases describing what this is ABOUT)
- director_context (brief: director's other notable work, style)
- key_cast_notes (brief: notable performances, cast connections)
- awards (array, brief)
- trivia (array of 3-5 genuinely interesting items, not filler)

Be honest. If the film is mediocre, say so in "why_this_matters."
If content warnings are serious, be specific. Better to over-warn
than miss a trigger.

Return ONLY valid JSON.
```

Gemma 3 12B via Ollama handles this well with `format: "json"` mode.
For weak signal (obscure films with thin sources), the synthesis
is honest about gaps: "Limited critical material available on this
film."

### Phase 3 — Cross-reference extraction (half day)

After enrichment completes, run a cross-ref pass:

```python
def extract_cross_references(rating_key: str, raw: dict) -> None:
    """Identify library items related to this one."""

    # Director-based: every film in the library by same director
    director = raw.get('tmdb', {}).get('director')
    if director:
        other_films = find_library_items_by_person(director, role='director')
        for other in other_films:
            if other != rating_key:
                insert_crossref(rating_key, other, 'director', director)

    # Shared cast: main cast members' other library appearances
    for cast_member in raw.get('tmdb', {}).get('cast', [])[:5]:
        shared = find_library_items_by_person(cast_member['name'])
        for item in shared:
            insert_crossref(rating_key, item, 'shared_cast', cast_member['name'])

    # Same collection: TMDB collections (franchise) membership
    collection_id = raw.get('tmdb', {}).get('collection_id')
    if collection_id:
        for item in find_library_items_by_collection(collection_id):
            insert_crossref(rating_key, item, 'same_collection', None)

    # Thematic: find library items with overlapping thematic_tags
    my_themes = set(raw.get('themes', []))
    if my_themes:
        candidates = find_library_items_with_any_theme(my_themes)
        for item in candidates:
            overlap = my_themes & set(item.themes)
            if len(overlap) >= 2:  # at least 2 shared themes = meaningful
                insert_crossref(
                    rating_key, item.rating_key, 'thematic',
                    ','.join(overlap),
                    confidence=len(overlap) / len(my_themes),
                )
```

At 50k items, this is where the library starts feeling like a
graph rather than a list.

### Phase 4 — MCP tool extension (1 day)

Extend `plex_media_enrichment` portmanteau with operations:

- `enrich(rating_key, force?)` — full enrichment run
- `bulk_enrich(filter?, max_items?)` — queue enrichment for many
  items, track progress
- `get_enrichment(rating_key)` — retrieve cached report
- `get_related(rating_key, relation_type?, limit?)` — fetch cross-refs
- `search_by_theme(theme)` — find library items with thematic tag
- `search_by_person(name, role?)` — find library items by person
- `stale_report(days=90)` — list enrichments older than N days for
  refresh
- `rebuild_crossrefs` — one-shot rebuild of the crossref table

### Phase 5 — REST endpoints (half day)

`webapp/backend/app/api/enrichment.py`:

```
POST /api/enrichment/{rating_key}            body: {force_refresh?, sources?}
GET  /api/enrichment/{rating_key}
GET  /api/enrichment/{rating_key}/related
POST /api/enrichment/bulk                    body: {filter, max_items}
GET  /api/enrichment/bulk/status/{job_id}
GET  /api/enrichment/by-theme?theme=
GET  /api/enrichment/by-person?name=&role=
GET  /api/enrichment/stale?days=90
```

Bulk enrichment is a background job because at 50k items this is
days of work even with concurrent fetching.

### Phase 6 — Frontend (1-2 days)

**Book-like detail page for media** at `/media/[ratingKey]` in the
webapp:

- Header: poster, title, year, director, runtime, trailer button
- Primary column: structured sections rendered as cards
  - Synopsis
  - "Why this matters" (the keeper section)
  - Critical overview
  - Production notes
  - Reception + legacy
  - Content warnings (with visual prominence for serious ones)
- Sidebar: thematic tags (clickable → search), cast cards, director
  card with filmography-in-library
- Bottom: "Related in your library" — cross-ref cards grouped by
  relation type (by director, shared cast, same collection,
  thematic)

Each thematic tag is clickable → search other library items with
that tag. Cast cards same behaviour.

**Enrichment status page** at `/enrichment`:

- How many items have enrichment
- How many are stale (> 90 days)
- Bulk enrichment queue progress
- Cost estimate (API calls, LLM tokens used)

**Book/film modal** (embedded in library view):

Quick enrichment preview in the modal when user hovers/clicks a
film. Shows top-level synopsis + "why this matters" + thematic
tags. Full page is one click away.

### Phase 7 — Plex client awareness (optional polish)

Plex has a "Pre-roll" feature. Nothing stops us from generating a
short text overlay that plays at the start of each film with
our enrichment summary. Niche, probably unwanted, flag for later.

More practical: XBMC-style "Trivia during transcode pause" — when
Plex pauses buffering, the webapp could fetch and display trivia
for the currently-playing item. Requires webapp-Plex integration
we don't have yet. Defer.

## Gotchas

- **Scraping politeness.** Letterboxd, IMDB, RT, Metacritic all
  have bot detection. Request throttling: max 1 request per second
  per domain. User-Agent set correctly. Cache aggressively — once
  we have the data, we don't hit them again for 90 days.

- **TMDB API key.** Already configured if `plex_media_enrichment`
  works today. Don't break anything.

- **Criterion is bespoke.** Their essays are behind paywalls for
  most films. Only the featured-free excerpts are accessible. Set
  expectations accordingly.

- **Content warnings are sensitive.** LLM-generated warnings
  could miss things or be oversensitive. For any film, include a
  "user-reported issues" field that Sandra can add to manually.

- **Bulk enrichment is expensive.** 50k items × 8 sources = 400k
  API hits plus 50k LLM synthesis calls. Even at 10 items/minute
  it's ~83 hours of work. Budget this: run overnight, prioritize
  recently-watched and highly-rated films first, everything else
  can drip.

- **Stale handling.** Films don't age quickly but reviews can
  evolve (e.g., film gets retrospective reappraisal). 90-day
  refresh default; tune later.

- **Sources overlap and contradict.** TMDB says one release year,
  Wikipedia another. LLM synthesis is told: prefer Wikipedia when
  sources disagree on fact; note discrepancies in `trivia`.

- **TV shows vs movies.** Shows need per-season enrichment plus
  show-level overview. Don't try to enrich every episode (that's
  project #5). Show-level and season-level only here.

- **Storage.** 50k reports × ~5KB each = 250MB. Fine. JSON in
  SQLite TEXT is cheap.

## Testing

1. Enrich 5 diverse films: a blockbuster, an obscure foreign film,
   a TV series, a documentary, a cult classic
2. Eyeball each report: is "why this matters" actually interesting?
   Are content warnings accurate? Is the critical overview not
   generic?
3. Run bulk enrichment on one Plex library (e.g., documentaries,
   ~1000 items) overnight
4. Verify cross-ref extraction: pick a director with 5+ films,
   check all show up linked
5. Webapp: the film detail page feels richer than TMDB or Plex
   native

## Update on completion

- Add v2.5.0 entry to CHANGELOG
- Mark shipped in `docs/plans/README.md`
- Update `FLEET_INDEX.md` in mcp-central-docs
- Update `README.md` main repo with screenshot of detail page

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

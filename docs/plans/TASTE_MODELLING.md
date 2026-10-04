# Taste Modelling — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** **Shipped 2026-10-04** (Claude Sonnet 5.5). The scoring model deliberately differs from the design below - see "What actually shipped".
**Effort:** 2–3 days
**Priority:** 2 of 6

---

## What actually shipped (2026-10-04)

The pipeline (watch events -> per-dimension profile -> time-of-week profiles -> taste-fit
scoring) matches this spec, but the **scoring model was changed after a live run showed
the designed one doesn't work on real data.**

**Why the EMA was replaced.** Run against a real library (16,928 history entries, 2021-2026),
the spec's capped EMA scored essentially every dimension +1.00: sci-fi, comedy, every
decade, every country. History is almost all positive events (completed/rewatched) with
very few negatives, so the average saturates at +1 for anything ever touched, and the score
means only "watched". The `MAX_WEIGHT = 100` cap also gave a memory of ~11 days at ~9
events/day. Anti-preferences (the "Comedies, films after 2020" the spec wants to show) are
impossible without something to compare against.

**What replaced it** (`src/plex_mcp/services/taste/`):
- **Lift against the library.** Each dimension accumulates *exponentially decayed attention*
  (1-year half-life). Score = `(watch_share - library_share) / (watch_share + library_share)`,
  bounded in [-1, 1]: 0 = proportional to what's available, -1 = in the library but never
  watched. This needs a one-time survey of the library (`library_dimensions`, ~1-2 minutes
  for ~12k items; section listings already include all tags).
- **Stratified by kind (movie vs show).** Shows have no directors/countries in Plex, use
  TV-specific genre names, and are watched in far larger volume; comparing them against a
  movie-dominated baseline produced artifacts (`country:japan` disliked while `genre:anime`
  was liked). Totals, baselines and scores are per kind.
- **Concave episode weighting.** The k-th episode event of a show weighs `0.25/sqrt(k)`, so a
  200-episode series counts like ~7 movie views, not 50. Abandonment is dampened (0.5); a
  4+ star / 2- star rating is strong (2.0); a middling rating is not evidence.

**Event capture, as verified against Plex:**
- Plex history entries carry **no playback progress**, so a history entry = completed and a
  repeat view of the same item = rewatched. Episodes roll up to their show via
  `grandparentKey` (not `grandparentRatingKey`, which is `None`).
- `abandoned` is derived from On Deck items stopped under 30% / at least 15 minutes in and
  untouched for 14+ days. `on_deck_dismissed` is supported by the scorer but **Plex does not
  expose dismissals, so it is never captured.**
- Ratings are not sparse for this library (992 rated items), contrary to the gotcha below.

**Deliberately not built:**
- `watch_transitions` ("what do I watch after what"): the spec lists the table but no tool
  operation or UI consumes it.
- Theme dimensions are recorded from enrichment but **not scored yet**: they have no library
  baseline until enrichment coverage is broad. Enrichment contributes `theme:` only, because
  mixing TMDB director/country into some items would break baseline consistency.
- Per-account profiles: events store `account_id`, but there is one profile. Household
  profiles (next in the sequence) can rebuild per-account from the stored events.
- The background poll only runs after a profile has been built once (`TASTE_SYNC_INTERVAL_SEC`,
  default 600, `0` disables), so a fresh install never starts hitting Plex on its own.

Surface: `plex_taste` MCP tool (`status`, `rebuild_from_history`, `sync`, `profile`,
`temporal_profile`, `recent_shifts`, `dimensions_for`, `score_item`, `score_library`),
`/api/taste/*`, and the `/taste` webapp page. Data: `data/taste.db` (gitignored).

---

## The problem

Plex knows what Sandra has watched. It does nothing useful with
that data. The "Continue Watching" row is chronological. The
"Recommended For You" row is TMDB-genre-similar.

For a library of 50k items, understanding taste requires:

- Not just "genres user watches" (too coarse)
- Not just "stars of films user watches" (too noisy)
- Thematic preferences, tonal preferences, decade preferences,
  pacing preferences, country-of-origin preferences
- Implicit signals: completing vs abandoning, rewatching,
  time-of-day tendencies, what you watch after what
- Ratings (if any) as ground truth anchors

Build a taste profile that downstream features (mood picker,
recommendations, book-of-the-day-equivalent) can consume.

## Data sources already available

- Plex watch history (via PlexAPI `history()`)
- Plex ratings (1-10 or 5-star where available)
- Plex "on deck" status
- Watch progress (finished vs abandoned)
- Enrichment data (from project 1) — thematic_tags, director,
  decade, country

## The model

Not machine learning in the training sense. Exponential moving
averages over explicit taste dimensions.

### Taste dimensions

```sql
CREATE TABLE IF NOT EXISTS taste_profile (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    dimension     TEXT NOT NULL,  -- 'theme:heist' | 'director:scorsese' |
                                  -- 'decade:1970s' | 'country:japan' |
                                  -- 'pacing:slow' | 'tone:melancholy'
    score         REAL NOT NULL DEFAULT 0,   -- -1.0 to +1.0
    weight        REAL NOT NULL DEFAULT 0,   -- total evidence weight
    last_updated  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dimension)
);

CREATE TABLE IF NOT EXISTS watch_events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    rating_key        TEXT NOT NULL,
    event_type        TEXT NOT NULL,  -- 'started' | 'completed' | 'abandoned'
                                       -- | 'rewatched' | 'rated' | 'on_deck_dismissed'
    event_value       REAL,           -- rating value if applicable
    event_timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watch_progress    REAL            -- 0.0 - 1.0 at event time
);
CREATE INDEX IF NOT EXISTS idx_watch_events_key ON watch_events(rating_key);
CREATE INDEX IF NOT EXISTS idx_watch_events_time ON watch_events(event_timestamp);
```

### Scoring logic

Each watch event updates dimension scores:

- **completed** (≥90% watched): +1.0 to every dimension of the film
- **abandoned** (<30% watched after ≥15 minutes): -0.5 to every
  dimension (weaker signal; could just be wrong mood)
- **rewatched**: +2.0 (strong positive)
- **rated ≥4 stars**: +2.0
- **rated ≤2 stars**: -2.0
- **on_deck_dismissed** without watching: -0.3

Dimensions are updated via EMA:
```
new_score = (score * weight + event_delta) / (weight + event_weight)
new_weight = min(weight + event_weight, MAX_WEIGHT)
```

`MAX_WEIGHT` caps around 100 so recent events keep mattering even
if user has 10,000 past events in that dimension.

### Time-of-day and day-of-week

Secondary tables track temporal preferences:

```sql
CREATE TABLE IF NOT EXISTS temporal_taste (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    time_bucket   TEXT NOT NULL,  -- 'weekday_evening' | 'weekend_afternoon' |
                                  -- 'late_night' | 'sunday_morning'
    dimension     TEXT NOT NULL,
    score         REAL NOT NULL,
    weight        REAL NOT NULL,
    UNIQUE(time_bucket, dimension)
);
```

"Sunday morning Sandra likes contemplative documentaries" is a
real pattern the system can surface.

### Watch-chain analysis

"What Sandra watches after what" is a weak signal but
interesting:

```sql
CREATE TABLE IF NOT EXISTS watch_transitions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    from_rating_key   TEXT NOT NULL,
    to_rating_key     TEXT NOT NULL,
    transition_count  INTEGER DEFAULT 1,
    last_seen         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_rating_key, to_rating_key)
);
```

After a heavy film, does she watch something light? After a
documentary, does she rewatch an old favourite? These transitions
inform recommendations.

## Implementation

### Phase 1 — Watch event capture (half day)

Background daemon polls Plex history every 10 minutes, detects
new events, inserts into `watch_events`. Use Plex's history
timestamps as canonical.

Initial backfill: on first run, pull entire Plex history (could be
years) and populate `watch_events` wholesale.

### Phase 2 — Score calculation (1 day)

`src/plex_mcp/services/taste/scorer.py`:

```python
async def update_taste_from_event(event: WatchEvent) -> None:
    """Apply a watch event to the taste profile."""

    enrichment = get_enrichment(event.rating_key)
    if not enrichment:
        # Without enrichment we only have Plex-native fields
        dimensions = derive_dimensions_from_plex(event.rating_key)
    else:
        dimensions = derive_dimensions_from_enrichment(enrichment)

    event_delta = event_type_to_delta(event.event_type, event.event_value)
    event_weight = event_type_to_weight(event.event_type)

    for dim in dimensions:
        update_ema(dim, event_delta, event_weight)

    # Temporal
    time_bucket = classify_time_bucket(event.event_timestamp)
    for dim in dimensions:
        update_ema_temporal(time_bucket, dim, event_delta, event_weight)
```

Dimensions per film:
- Every thematic_tag from enrichment → `theme:{tag}`
- Director → `director:{name}`
- Primary cast (top 3) → `actor:{name}`
- Decade → `decade:{1970s}`
- Country → `country:{france}`
- Runtime bucket → `runtime:{90-120min}`
- Plex genre → `genre:{thriller}`
- If enrichment has pacing hints → `pacing:{slow}`

### Phase 3 — Taste-aware scoring (half day)

`src/plex_mcp/services/taste/ranker.py`:

```python
def score_item_for_taste(rating_key: str,
                          time_bucket: str | None = None) -> float:
    """Return a taste-fit score for an item."""
    dimensions = get_item_dimensions(rating_key)
    profile_scores = get_profile_scores(list(dimensions))

    if time_bucket:
        temporal_scores = get_temporal_scores(time_bucket, list(dimensions))
        # Weighted blend: 70% base profile, 30% temporal
        blended = {d: 0.7 * profile_scores.get(d, 0)
                       + 0.3 * temporal_scores.get(d, 0)
                   for d in dimensions}
    else:
        blended = profile_scores

    # Sum weighted by evidence
    return weighted_average(dimensions, blended)
```

### Phase 4 — MCP tools (half day)

Extend or add `plex_taste`:

| Operation              | Purpose                                      |
|-----------------------|----------------------------------------------|
| `profile`             | Dump current taste profile                   |
| `score_item`          | Score one item against profile               |
| `score_library`       | Rank entire library by taste fit             |
| `dimensions_for`      | What dimensions does this item have          |
| `rebuild_from_history`| Re-derive profile from full watch history    |
| `temporal_profile`    | Taste profile for specific time bucket       |
| `recent_shifts`       | Dimensions that have changed in last 30 days |

### Phase 5 — REST + frontend (half day)

```
GET  /api/taste/profile?temporal=weekday_evening&top=50
GET  /api/taste/score/{rating_key}
POST /api/taste/rebuild
GET  /api/taste/temporal/{bucket}
GET  /api/taste/recent-shifts?days=30
```

Frontend: `/taste` page with:
- Top dimensions (positive): "You watch slow films, 1970s cinema,
  films by Tarkovsky, Japanese films, heist films..."
- Anti-preferences (negative): "Comedies, films after 2020,
  Marvel-style action..."
- Temporal breakdown: what Sunday morning looks like vs weeknight
- Recent shifts: "You've been watching more documentaries lately"

Visual is the point here. Sandra should recognize herself in the
profile. If she doesn't, the model is wrong.

## Gotchas

- **Without enrichment, dimensions are thin.** Plex-native fields
  alone give weak signal. This project plays best after enrichment
  ships.

- **Family viewing pollutes profile.** If someone else watches on
  Sandra's Plex account, their taste contaminates the model.
  Mitigation: per-user taste profile if Plex has distinct user
  accounts; otherwise accept noise.

- **Completion bias.** Sandra might stop a film for reasons
  unrelated to taste (fell asleep, interrupted). Heavy weight on
  completion penalizes interrupted viewing. Dampen abandonment
  penalty.

- **Ratings sparse.** Most Plex users don't rate. Don't over-weight
  when ratings are rare.

- **Profile drift.** Tastes change. The EMA handles this with the
  MAX_WEIGHT cap but tune it.

- **Spoiler-averse scoring.** Don't let the profile cause Sandra
  to surface items from spoilery genres unintentionally. Not a
  problem for taste itself, but for downstream features consuming
  the profile.

## Testing

1. Rebuild profile from full history
2. Eyeball top 10 positive dimensions — do they match Sandra's
   self-description?
3. Score a known favourite — should be high
4. Score a genre Sandra explicitly dislikes — should be negative
5. Check temporal split: are Sunday morning tastes plausibly
   different from Saturday night tastes?

## Update on completion

- [x] CHANGELOG (repo and mcp-central-docs mirror)
- [x] docs/plans/README.md, ROADMAP.md, GAP_ANALYSIS_AND_IMPROVEMENTS.md
- [ ] FLEET_INDEX.md in mcp-central-docs - not touched, do at the next fleet-wide capability sweep

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

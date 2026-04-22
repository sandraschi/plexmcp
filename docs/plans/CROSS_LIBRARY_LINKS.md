# Cross-Library Linking — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 2 days
**Priority:** 6 of 6

---

## The problem

Plex libraries are siloed. Movies and TV separate. Documentaries
often in their own library. Anime sometimes in a third. For
Sandra's 50k-item collection, crossing these boundaries is
manual.

Useful cross-library questions Plex can't answer:

- "What other films did this director make that I own, in any
  library?"
- "Documentaries about the making of this fiction film"
- "Interviews with this actor across my library"
- "Concert footage by the composer of this film"
- "Adaptations of this film's source material"
- "The fiction based on this documentary's true story, or vice
  versa"

These are real viewing paths. A serious film lover knows that
after watching Herzog's _Fitzcarraldo_, the natural next watch
is _Burden of Dreams_ (the documentary about the making of it).
That pairing doesn't exist in Plex.

## The approach

This is not new infrastructure — it's a synthesis layer over
data projects 1-5 already produce.

After enrichment (project 1), every item has:
- Director
- Cast members
- Production companies
- Source material (if an adaptation)
- Shared-universe membership
- Thematic tags

After taste modelling (project 3), we know which of these
connections Sandra values.

This project builds the query + UI layer that makes cross-library
connections visible.

## The connection types

| Connection type        | How we detect                              |
|-----------------------|--------------------------------------------|
| Same director         | Enrichment director field match            |
| Shared cast           | Cast list overlap                          |
| Adaptation ↔ source   | Enrichment's "based on" field              |
| Documentary ↔ subject | LLM-inferred subject matter match          |
| Making-of pair        | Filename patterns + title similarity       |
| Shared composer       | Music credit match                         |
| Director's influence  | Enrichment "influenced by" field           |
| Same era/movement     | Decade + country + movement tag match      |
| Shared source IP      | Franchise/collection membership            |
| Interview pairs       | Interview show + subject match             |

Some are deterministic (shared director), some require LLM
judgment (making-of detection based on titles).

## Implementation

### Phase 1 — Extend the crossref table from project 1

Project 1 introduced `enrichment_cross_refs`. Extend the
`relation_type` vocabulary to cover all the above, and add
bidirectional relations:

```sql
ALTER TABLE enrichment_cross_refs ADD COLUMN bidirectional INTEGER DEFAULT 0;
ALTER TABLE enrichment_cross_refs ADD COLUMN libraries TEXT;
-- 'libraries' is a JSON array of library types the pair spans, e.g.
-- '["movies", "documentaries"]' — makes the cross-library nature visible
```

### Phase 2 — New crossref detectors (1 day)

`src/plex_mcp/services/enrichment/crossrefs/`:

One module per connection type. Examples:

**`making_of.py`** — detects documentary/fiction pairs:

```python
def detect_making_of_pairs(library_path: str) -> list[CrossRef]:
    """Find documentaries that document the production of fiction films."""

    pairs = []
    docs = get_items_by_type('documentary')
    films = get_items_by_type('movie')

    for doc in docs:
        # Pattern 1: "The Making of X" / "Behind the Scenes of X"
        title_match = re.search(
            r'(?:making of|behind the scenes of|shooting)\s+(.+)',
            doc.title,
            re.IGNORECASE,
        )
        if title_match:
            target_title = title_match.group(1).strip()
            matches = find_film_by_title(films, target_title)
            for film in matches:
                pairs.append(CrossRef(
                    source=doc.rating_key,
                    target=film.rating_key,
                    relation_type='making_of',
                    bidirectional=True,
                    detail=f'Documentary about production of "{film.title}"',
                ))

        # Pattern 2: LLM-assisted for non-obvious titles
        # (only for documentaries where title gives no hint)
        if doc.summary and should_try_llm(doc):
            candidates = llm_identify_subject_film(doc, films)
            for film, confidence in candidates:
                if confidence >= 0.8:
                    pairs.append(CrossRef(
                        source=doc.rating_key,
                        target=film.rating_key,
                        relation_type='making_of',
                        confidence=confidence,
                    ))

    return pairs
```

**`adaptation_pairs.py`** — links films to books:

```python
def detect_adaptation_pairs() -> list[CrossRef]:
    """Films adapted from books (or vice versa) that we own."""
    films = get_items_with_enrichment()
    pairs = []
    for film in films:
        source_material = film.enrichment.get('based_on')
        if not source_material:
            continue
        # Cross-reference with calibre-mcp library via API
        book_matches = query_calibre_mcp(source_material)
        for book in book_matches:
            pairs.append(CrossRef(
                source=film.rating_key,
                target=f'calibre:{book.book_id}',
                relation_type='adaptation_of',
                detail=source_material,
            ))
    return pairs
```

That last one is particularly nice — the three-tool trio (Plex +
Calibre + MCP server) links a film to its source novel if Sandra
owns both. Cross-fleet linking.

### Phase 3 — Query and ranking (half day)

`src/plex_mcp/services/crossref_query.py`:

```python
def get_related(
    rating_key: str,
    relation_types: list[str] | None = None,
    cross_library_only: bool = False,
    limit: int = 20,
    min_confidence: float = 0.5,
) -> list[CrossRefHit]:
    """Fetch related items with taste-adjusted ranking."""

    raw = fetch_crossrefs(rating_key, relation_types, min_confidence)

    if cross_library_only:
        raw = [r for r in raw if r.spans_libraries()]

    # Rank by combination of: crossref confidence, taste fit of
    # target item, connection strength
    ranked = sorted(raw, key=lambda r: -compute_rank_score(r))[:limit]

    return [hydrate_with_metadata(r) for r in ranked]
```

### Phase 4 — MCP tools (half day)

Extend `plex_media_enrichment` or add `plex_crossrefs`:

| Operation            | Purpose                                  |
|---------------------|------------------------------------------|
| `related`           | All related for one item                 |
| `cross_library`     | Related that spans libraries only        |
| `adaptation_pairs`  | Show all adaptation pairs in library     |
| `making_of_pairs`   | All fiction/doc production pairs         |
| `director_network`  | All films by directors I own, graph form |
| `rebuild_crossrefs` | Full re-run of detection                 |

### Phase 5 — Frontend (half day)

Film detail page gets a "Connections" panel showing cross-library
relations, grouped by type. Icons differentiate library boundary
(movie → documentary is highlighted vs movie → movie).

A new `/connections` page visualizes the library as a graph.
Force-directed graph with films as nodes, relations as edges.
Heavy for 50k items — limit to "films you've watched + their
1-hop neighbors" for performance.

## Gotchas

- **Running detectors at 50k items.** Each detector is O(n) or
  O(n²). The O(n²) detectors (thematic similarity) need sensible
  partitioning. Run crossref detection in background after
  enrichment completes, never in request path.

- **LLM-inferred connections need confidence tracking.** Store
  `confidence` explicitly. Filter display by threshold. Sandra can
  surface low-confidence ones manually if she wants to explore.

- **Calibre-mcp cross-linking requires calibre-mcp running.**
  Graceful degrade if unavailable — just show Plex-internal
  crossrefs.

- **Making-of detection has tricky false positives.** "The Making
  of a Murderer" is not a making-of pair. Regex has to be
  careful, and LLM backup has to be sanity-checked.

- **Bidirectional storage.** Store each relation once with
  `bidirectional=True`; expand at query time. Avoids double
  storage and keeps edits atomic.

## Testing

1. Run detection on a subset
2. Spot check: pick a well-known director with many films in
   library, verify all connections found
3. Check a known documentary/fiction pair (e.g., Fitzcarraldo ↔
   Burden of Dreams): does it link?
4. Cross-fleet: if calibre-mcp knows about the novel, does the
   film detail page link to it?
5. Graph UI performance at scale — may need to cap or paginate

## Update on completion

- CHANGELOG
- docs/plans/README.md
- FLEET_INDEX.md

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

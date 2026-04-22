# Mood-Based Nightly Picker — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 1–2 days
**Priority:** 3 of 6

---

## The idea

Sandra watches something most nights. The question "what should I
put on" is often the hardest part of the evening. A good picker
removes the decision fatigue.

Inputs:
- A mood (selectable or free-text)
- Available time (30 min / 60 min / full evening / movie-length)
- Taste profile (from project 3)
- Enrichment data (from project 1)
- Watch history (avoid immediate re-watches unless asked)

Output: 3-5 suggestions with one-line rationales.

## Why this is project 3's killer feature

Without taste modelling, a mood picker is just "filter by genre."
With taste modelling, it's "what fits both your mood AND your
actual preferences." That's the thing Plex can't do.

## Mood taxonomy

Fixed enumeration of moods, each mapped to enrichment dimensions:

| Mood                      | Maps to (positive)           | Maps to (negative)         |
|--------------------------|-------------------------------|----------------------------|
| Comfort rewatch          | rewatches_score > 0           | new_to_library             |
| Something challenging    | theme:philosophical, pacing:slow | genre:action           |
| Light & silly            | genre:comedy, tone:warm       | tone:melancholy            |
| Deeply absorbing         | runtime:120+, pacing:slow     | genre:sitcom               |
| Educational              | type:documentary              | genre:fiction (weighted)   |
| Atmospheric              | cinematography-heavy, pacing:slow, era:70s-80s | |
| Noir & cynical           | genre:noir, tone:cynical      | tone:hopeful               |
| Romance-adjacent         | theme:relationships           |                            |
| Action thrill            | genre:thriller, pacing:fast   | pacing:slow                |
| Foreign                  | country:not-USA               |                            |
| Surprise me              | (random within high-taste-fit) |                           |

Free-text moods use LLM sampling to map to dimensions:

> User says "I want something like Blade Runner but not a rewatch"
> → LLM extracts: dimensions ['mood:melancholy', 'genre:sf',
> 'aesthetic:neon', 'theme:identity', 'pacing:slow'], exclusion
> 'Blade Runner'

## Implementation

### Phase 1 — Selection service (half day)

`src/plex_mcp/services/mood/picker.py`:

```python
def pick_for_mood(
    mood: str,
    max_runtime_minutes: int | None = None,
    exclude_recent_days: int = 14,
    n: int = 5,
) -> list[PickSuggestion]:
    """Select n candidates matching mood + time + taste."""

    # 1. Map mood to dimension weights
    if mood in PRESET_MOODS:
        dim_weights = PRESET_MOODS[mood]
    else:
        dim_weights = llm_map_free_mood(mood)

    # 2. Time bucket for temporal taste
    time_bucket = classify_current_time_bucket()

    # 3. Candidate pool: filter by runtime + not recently watched
    candidates = query_candidates(
        max_runtime_minutes=max_runtime_minutes,
        exclude_watched_since=exclude_recent_days,
    )

    # 4. Score each candidate
    scored = []
    for c in candidates:
        mood_fit = score_against_dimensions(c, dim_weights)
        taste_fit = score_item_for_taste(c.rating_key, time_bucket)
        novelty_bonus = novelty_score(c)  # unread items slight boost
        combined = 0.5 * mood_fit + 0.4 * taste_fit + 0.1 * novelty_bonus
        scored.append((c, combined))

    # 5. Top n with rationale
    top = sorted(scored, key=lambda x: -x[1])[:n]
    return [make_suggestion(c, score, mood, dim_weights) for c, score in top]


def make_suggestion(item, score, mood, dim_weights) -> PickSuggestion:
    """Generate a one-line rationale for why this fits."""
    top_matching_dims = get_top_matching_dims(item, dim_weights)
    return PickSuggestion(
        rating_key=item.rating_key,
        score=score,
        rationale=format_rationale(top_matching_dims, mood),
    )
```

Rationale format: "Fits '{mood}' because it's {top_dim_1} and
{top_dim_2}, and you tend to enjoy {taste_dim}."

### Phase 2 — MCP tool (half day)

Extend or add `plex_mood_picker`:

| Operation         | Purpose                                     |
|------------------|---------------------------------------------|
| `pick`           | Get suggestions for mood + constraints      |
| `preset_moods`   | List available preset moods                 |
| `history`        | Last N picks + user actions                 |
| `record_action`  | Record: picked | skipped | dismissed       |

### Phase 3 — REST + frontend (1 day)

```
POST /api/mood/pick             body: {mood, max_runtime?, n?}
GET  /api/mood/presets
GET  /api/mood/history
POST /api/mood/action/{pick_id} body: {action: 'picked'|'skipped'|'dismissed'}
```

Frontend: `/tonight` page.

Design principle: minimal. The whole point is to NOT make Sandra
think. Big mood buttons, optional runtime slider, a "pick" button,
done. Results as 3-5 cards with poster + 1-line rationale + "Play
in Plex" button.

```
┌─ What are you in the mood for? ─────────────────────┐
│                                                       │
│  [Comfort rewatch]  [Something challenging]           │
│  [Light & silly]    [Deeply absorbing]                │
│  [Documentary]      [Noir]                            │
│  [Surprise me]      [...] free-text input             │
│                                                       │
│  Max runtime: [⏺ any] [< 60m] [< 90m] [< 2h]          │
│                                                       │
│  [Pick me something]                                  │
└───────────────────────────────────────────────────────┘
```

After pick:

```
┌─ Three options for "atmospheric, under 2h" ──────────┐
│                                                       │
│  [poster] Stalker (1979) · 163 min ⚠ over runtime    │
│  Atmospheric, slow pacing, you love Tarkovsky         │
│  [▶ Play]  [Skip]                                     │
│                                                       │
│  [poster] Under the Skin (2013) · 108 min             │
│  Atmospheric, cinematography-focused, fits mood       │
│  [▶ Play]  [Skip]                                     │
│                                                       │
│  [poster] Paris, Texas (1984) · 145 min               │
│  Atmospheric, melancholic, 80s cinema                 │
│  [▶ Play]  [Skip]                                     │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## Gotchas

- **First-time usage with thin taste data.** Without enrichment
  and watch history, rationales fall back to "fits mood" only.
  Acceptable; will improve as data accumulates.

- **Runtime mismatch handling.** If user wants < 60 min but best
  matches are all features, show them anyway with a warning flag
  rather than returning nothing.

- **"Comfort rewatch" needs special handling.** That mood
  explicitly wants items Sandra has watched before. All other
  moods default to excluding recent watches.

- **Free-text mood LLM cost.** Each free-text query hits Ollama.
  Not expensive but not free. Cache LLM→dimensions mappings for
  repeated inputs.

- **Skip accumulation as negative signal.** If Sandra skips a
  suggestion, that's a weak negative on those dimensions. Feed
  back into taste model.

## Testing

1. Run presets — do suggestions feel mood-appropriate?
2. Run free-text mood — does LLM mapping give sensible dimensions?
3. Use it for a week — does the suggestion actually become what's
   watched, or does Sandra still override?
4. Skip rate metric: if > 70%, something's wrong

## Update on completion

- CHANGELOG
- docs/plans/README.md
- FLEET_INDEX.md

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*

"""Lift-based taste scores and profile summaries (pure functions).

score(d) = (watch_share - library_share) / (watch_share + library_share), in [-1, 1]:
  +  you give this dimension more attention than its share of the library
  0  proportional to what's available
  -  available but you pass it over (-1: in the library, never watched)
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any

from .scorer import ALL_SCOPE, Profile, replay, to_days, total_scope, value_at

BASE_BLEND = 0.7
TEMPORAL_BLEND = 0.3
MIN_EVIDENCE = 3.0  # decayed event-weight needed before a *liked* dimension is trusted
MIN_LIBRARY_COUNT = 10  # library items needed before "never watched" counts as a dislike
MIN_BUCKET_ATTENTION = 10.0  # decayed event-weight a time-of-week bucket needs before it is scored at all


def lift(watch_share: float, library_share: float) -> float:
    total = watch_share + library_share
    return 0.0 if total <= 0 else (watch_share - library_share) / total


def compute_scores(
    profile: Profile,
    library_counts: dict[str, int],
    library_sizes: dict[str, int],
    now_days: float,
    kind: str,
    scope: str = ALL_SCOPE,
    min_evidence: float = MIN_EVIDENCE,
    min_library: int = MIN_LIBRARY_COUNT,
) -> dict[str, dict[str, Any]]:
    """Score every dimension of one kind ("movie" or "show") that has a library baseline and
    enough evidence either way. `scope` is ALL_SCOPE or a time bucket."""
    library_size = library_sizes.get(kind, 0)
    total_pos, _ = value_at(profile.totals.get(total_scope(kind, scope)), now_days)
    if total_pos <= 0 or library_size <= 0:
        return {}
    if scope != ALL_SCOPE and total_pos < MIN_BUCKET_ATTENTION:
        return {}  # too little viewing at this time of week: absence would read as a hard dislike

    prefix = f"{kind}:"
    if scope == ALL_SCOPE:
        entries = {k: e for k, e in profile.dims.items() if k.startswith(prefix)}
    else:
        entries = {d: e for (b, d), e in profile.temporal.items() if b == scope and d.startswith(prefix)}
    in_kind = {k: n for k, n in library_counts.items() if k.startswith(prefix)}

    scores: dict[str, dict[str, Any]] = {}
    for key in in_kind.keys() | entries.keys():
        d = key[len(prefix) :]
        in_library = in_kind.get(key, 0)
        if in_library == 0:
            continue  # no baseline (e.g. enrichment themes) -> cannot be judged relative to the library
        pos, neg = value_at(entries.get(key), now_days)
        if in_library < min_library and pos < min_evidence:
            continue
        library_share = in_library / library_size
        watch_share = max(0.0, pos - neg) / total_pos
        expected = library_share * total_pos
        scores[d] = {
            "score": lift(watch_share, library_share),
            "watch_share": watch_share,
            "library_share": library_share,
            "library_count": in_library,
            "attention": pos,
            "evidence": math.sqrt(max(pos, expected)),
        }
    return scores


def summarize(
    scores: dict[str, dict[str, Any]], top: int = 25, prefix: str | None = None
) -> dict[str, list[dict[str, Any]]]:
    """Strongest likes and dislikes, ranked by score x evidence so thin data can't top the list."""
    rows = []
    for d, s in scores.items():
        if prefix is not None and not d.startswith(f"{prefix}:"):
            continue
        rows.append(
            {
                "dimension": d,
                "score": round(s["score"], 3),
                "watch_share": round(s["watch_share"], 4),
                "library_share": round(s["library_share"], 4),
                "library_count": s["library_count"],
                "attention": round(s["attention"], 2),
                "strength": round(s["score"] * s["evidence"], 3),
            }
        )
    likes = sorted((r for r in rows if r["score"] > 0), key=lambda r: r["strength"], reverse=True)[:top]
    dislikes = sorted((r for r in rows if r["score"] < 0), key=lambda r: r["strength"])[:top]
    return {"likes": likes, "dislikes": dislikes}


def score_item(
    dims: list[str],
    scores: dict[str, dict[str, Any]],
    temporal_scores: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Taste fit of one item: evidence-weighted mean of its dimensions' scores.

    A dimension with no temporal evidence falls back to its base score rather
    than being diluted toward zero. Dimensions with no score are ignored (and
    lower `confidence`) rather than counted as neutral.
    """
    contributions: list[tuple[str, float, float]] = []
    for d in dims:
        base = scores.get(d)
        if base is None:
            continue
        s = base["score"]
        if temporal_scores and d in temporal_scores:
            s = BASE_BLEND * s + TEMPORAL_BLEND * temporal_scores[d]["score"]
        contributions.append((d, s, base["evidence"]))

    total = sum(w for _, _, w in contributions)
    overall = sum(s * w for _, s, w in contributions) / total if total > 0 else 0.0
    ranked = sorted(contributions, key=lambda c: c[1] * c[2], reverse=True)
    return {
        "score": round(overall, 4),
        "confidence": round(len(contributions) / len(dims), 3) if dims else 0.0,
        "known_dimensions": len(contributions),
        "total_dimensions": len(dims),
        "top_positive": [{"dimension": d, "score": round(s, 3)} for d, s, _ in ranked if s > 0][:5],
        "top_negative": [{"dimension": d, "score": round(s, 3)} for d, s, _ in reversed(ranked) if s < 0][:5],
    }


def recent_shifts(
    events: list[dict[str, Any]],
    dims_lookup: dict[str, list[str]],
    library_counts: dict[str, int],
    library_sizes: dict[str, int],
    kind: str,
    days: int = 30,
    top: int = 15,
    now: datetime | None = None,
    prefix: str | None = None,
) -> list[dict[str, Any]]:
    """Dimensions (of one kind) whose score moved most over the last `days` (history replayed to the cutoff).

    `prefix` limits to one family ("genre", "decade", ...): actor dimensions are noisy over long windows."""
    now = now or datetime.now()
    cutoff = now - timedelta(days=days)
    then_profile, _ = replay(events, dims_lookup, until=cutoff.strftime("%Y-%m-%d %H:%M:%S"))
    now_profile, _ = replay(events, dims_lookup)
    then_scores = compute_scores(then_profile, library_counts, library_sizes, to_days(cutoff), kind)
    now_scores = compute_scores(now_profile, library_counts, library_sizes, to_days(now), kind)

    shifts = []
    for d, cur in now_scores.items():
        if prefix is not None and not d.startswith(f"{prefix}:"):
            continue
        prev = then_scores.get(d)
        delta = cur["score"] - (prev["score"] if prev else 0.0)
        if abs(delta) < 0.05:
            continue
        shifts.append(
            {
                "dimension": d,
                "score_then": round(prev["score"], 3) if prev else None,
                "score_now": round(cur["score"], 3),
                "delta": round(delta, 3),
                # "new" = no attention before the window. Not `prev is None`: a dimension that is
                # plentiful in the library but never watched has a score (-1), so it does exist.
                "new": prev is None or prev["attention"] <= 1e-9,
                "_rank": abs(delta) * cur["evidence"],
            }
        )
    shifts.sort(key=lambda s: s["_rank"], reverse=True)
    for s in shifts:
        del s["_rank"]
    return shifts[:top]

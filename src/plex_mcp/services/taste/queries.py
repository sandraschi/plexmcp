"""Read-side taste queries shared by the MCP tool and the webapp REST API."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from . import db, ranker, sync
from .scorer import ALL_SCOPE, KINDS, TIME_BUCKETS, dimensions_from_meta, kind_of, to_days


class TasteNotBuilt(Exception):  # noqa: N818 - reads better as a state than as an "Error"
    """Raised when a query needs a profile that hasn't been built yet."""


def validate_kind(kind: str) -> str:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    return kind


def validate_bucket(bucket: str | None) -> str | None:
    if bucket in (None, "", ALL_SCOPE):
        return None
    if bucket not in TIME_BUCKETS:
        raise ValueError(f"time_bucket must be one of {', '.join(TIME_BUCKETS)}")
    return bucket


def _load() -> tuple[Any, dict[str, int], dict[str, int]]:
    if not db.get_meta("rebuilt_at"):
        raise TasteNotBuilt("No taste profile yet. Run rebuild_from_history first.")
    counts, sizes = db.load_library()
    return db.load_profile(), counts, sizes


def get_profile(
    kind: str = "movie", bucket: str | None = None, top: int = 25, prefix: str | None = None
) -> dict[str, Any]:
    kind, bucket = validate_kind(kind), validate_bucket(bucket)
    profile, counts, sizes = _load()
    scores = ranker.compute_scores(profile, counts, sizes, to_days(datetime.now()), kind, scope=bucket or ALL_SCOPE)
    summary = ranker.summarize(scores, top=top, prefix=prefix)
    return {
        "kind": kind,
        "time_bucket": bucket,
        "prefix": prefix,
        "scored_dimensions": len(scores),
        "library_items": sizes.get(kind, 0),
        **summary,
    }


def get_recent_shifts(
    kind: str = "movie", days: int = 30, top: int = 15, prefix: str | None = None
) -> list[dict[str, Any]]:
    kind = validate_kind(kind)
    _, counts, sizes = _load()
    return ranker.recent_shifts(
        db.all_events(), db.all_item_dimensions(), counts, sizes, kind, days=days, top=top, prefix=prefix
    )


async def dimensions_for(rating_key: str, server: Any | None = None) -> dict[str, Any]:
    """Dimensions of one item (cached, else read from Plex), plus its kind and title."""
    rating_key = str(rating_key)
    row = _cached_row(rating_key)
    if row is None:
        server = server or await sync.get_plex_server()
        await asyncio.to_thread(sync.resolve_dimensions, server, rating_key)
        row = _cached_row(rating_key)
    if row is None or not row["media_type"]:
        raise LookupError(f"No Plex item found for rating_key={rating_key}")
    return {
        "rating_key": rating_key,
        "title": row["title"],
        "kind": kind_of(row["media_type"]),
        "dimensions": row["dims"],
    }


def _cached_row(rating_key: str) -> dict[str, Any] | None:
    conn = db.get_connection()
    try:
        r = conn.execute(
            "SELECT media_type, title, dims FROM item_dimensions WHERE rating_key = ?", (rating_key,)
        ).fetchone()
    finally:
        conn.close()
    if not r:
        return None
    return {"media_type": r["media_type"], "title": r["title"], "dims": json.loads(r["dims"])}


async def score_item(rating_key: str, bucket: str | None = None, server: Any | None = None) -> dict[str, Any]:
    bucket = validate_bucket(bucket)
    profile, counts, sizes = _load()
    item = await dimensions_for(rating_key, server)
    now = to_days(datetime.now())
    scores = ranker.compute_scores(profile, counts, sizes, now, item["kind"])
    temporal = ranker.compute_scores(profile, counts, sizes, now, item["kind"], scope=bucket) if bucket else None
    return {
        "rating_key": item["rating_key"],
        "title": item["title"],
        "kind": item["kind"],
        "time_bucket": bucket,
        **ranker.score_item(item["dimensions"], scores, temporal),
    }


def _is_unwatched(item: Any) -> bool:
    if getattr(item, "type", "") == "show":
        return not getattr(item, "viewedLeafCount", 0)
    return not getattr(item, "viewCount", 0)


async def score_library(
    library_id: str,
    server: Any | None = None,
    limit: int = 50,
    unwatched_only: bool = True,
    bucket: str | None = None,
) -> dict[str, Any]:
    """Rank one library's items by taste fit (best first)."""
    bucket = validate_bucket(bucket)
    profile, counts, sizes = _load()
    server = server or await sync.get_plex_server()
    section = await asyncio.to_thread(server.library.sectionByID, int(library_id))
    if section.type not in ("movie", "show"):
        raise ValueError(f"Library {library_id} is a {section.type} library; only movie and show libraries are scored.")
    items = await asyncio.to_thread(section.all)

    kind = kind_of(section.type)
    now = to_days(datetime.now())
    scores = ranker.compute_scores(profile, counts, sizes, now, kind)
    temporal = ranker.compute_scores(profile, counts, sizes, now, kind, scope=bucket) if bucket else None

    ranked = []
    for it in items:
        if unwatched_only and not _is_unwatched(it):
            continue
        dims = dimensions_from_meta(sync._meta_from_plex(it))  # Plex-native: same source as the baseline
        result = ranker.score_item(dims, scores, temporal)
        if result["known_dimensions"] == 0:
            continue
        ranked.append(
            {
                "rating_key": str(it.ratingKey),
                "title": it.title,
                "year": getattr(it, "year", None),
                "score": result["score"],
                "confidence": result["confidence"],
                "top_positive": result["top_positive"][:3],
                "top_negative": result["top_negative"][:3],
            }
        )
    ranked.sort(key=lambda r: (r["score"], r["confidence"]), reverse=True)
    return {
        "library_id": str(library_id),
        "kind": kind,
        "time_bucket": bucket,
        "considered": len(items),
        "ranked": len(ranked),
        "items": ranked[:limit],
    }

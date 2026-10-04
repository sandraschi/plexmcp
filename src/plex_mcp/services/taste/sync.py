"""Plex -> taste events and item dimensions; incremental sync and full rebuild.

Facts about Plex that shape this module (verified against a live server):
- History entries carry NO playback progress, so a history entry is treated as
  a completed view and a repeat view of the same item as a rewatch.
- Episode history entries expose the show only via `grandparentKey`
  ("/library/metadata/<id>"), not `grandparentRatingKey`.
- `abandoned` is derived from on-deck items with partial progress, since that
  is the only place Plex exposes progress. `on_deck_dismissed` is supported by
  the scorer but Plex does not expose dismissals, so it is never captured.
"""

from __future__ import annotations

import asyncio
import os
import threading
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from ...utils import get_logger
from ..enrichment import db as enrichment_db
from . import db
from .scorer import classify_time_bucket, dimensions_from_meta, event_sign_weight, kind_of, replay

logger = get_logger(__name__)

TS_FORMAT = "%Y-%m-%d %H:%M:%S"
ABANDON_MAX_PROGRESS = 0.30
ABANDON_MIN_MINUTES = 15
ABANDON_STALE_DAYS = 14
DIMENSION_TTL_DAYS = 30
MIN_BASELINE_COUNT = 2

_progress_lock = threading.Lock()
_progress: dict[str, Any] = {"phase": "idle", "message": ""}
_run_lock: asyncio.Lock | None = None


def _set_progress(**fields: Any) -> None:
    with _progress_lock:
        _progress.update(fields)


def mark_starting(message: str = "Starting...") -> None:
    """Reset progress for a newly accepted run (also clears any previous error)."""
    _set_progress(phase="starting", message=message, done=0, total=0)


def report_error(message: str) -> None:
    """Surface a background failure in the progress state the UI polls."""
    _set_progress(phase="error", message=message)


def get_progress() -> dict[str, Any]:
    with _progress_lock:
        return dict(_progress)


def _get_run_lock() -> asyncio.Lock:
    global _run_lock
    if _run_lock is None:
        _run_lock = asyncio.Lock()
    return _run_lock


def is_running() -> bool:
    return _get_run_lock().locked()


async def get_plex_server() -> Any:
    """Connected plexapi PlexServer built from PLEX_URL / PLEX_TOKEN."""
    from ..plex_service import PlexService

    base_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    token = os.getenv("PLEX_TOKEN")
    if not token:
        raise RuntimeError("PLEX_TOKEN is required (set it in Settings or .env).")
    service = PlexService(base_url=base_url, token=token)
    await service.connect()
    return service.server


# --- pure event builders (testable without Plex) -------------------------------


def _key_from_path(path: str | None) -> str | None:
    return path.rstrip("/").rsplit("/", 1)[-1] if path else None


def _ts(dt: datetime) -> str:
    return dt.strftime(TS_FORMAT)


def build_history_events(entries: list[Any], seen_source_keys: set[str]) -> list[dict[str, Any]]:
    """History entries -> completed / rewatched events, chronological. Episodes roll up to their show."""
    # Entries for items since deleted from Plex have no ratingKey: nothing to attach taste to.
    wanted = [
        h
        for h in entries
        if getattr(h, "type", None) in ("movie", "episode")
        and getattr(h, "viewedAt", None)
        and getattr(h, "ratingKey", None)
    ]
    wanted.sort(key=lambda h: h.viewedAt)
    seen = set(seen_source_keys)
    events: list[dict[str, Any]] = []
    for h in wanted:
        source_key = str(h.ratingKey)
        rating_key = (
            (_key_from_path(getattr(h, "grandparentKey", None)) or source_key) if h.type == "episode" else source_key
        )
        event_type = "rewatched" if source_key in seen else "completed"
        seen.add(source_key)
        events.append(
            {
                "rating_key": rating_key,
                "source_key": source_key,
                "account_id": getattr(h, "accountID", None),
                "media_type": h.type,
                "event_type": event_type,
                "event_value": None,
                "event_timestamp": _ts(h.viewedAt),
                "watch_progress": 1.0,
            }
        )
    return events


def build_abandoned_events(items: list[Any], now: datetime | None = None) -> list[dict[str, Any]]:
    """On-deck items stopped early and left alone for a while -> abandoned (dampened) events."""
    now = now or datetime.now()
    events: list[dict[str, Any]] = []
    for it in items:
        if getattr(it, "type", None) not in ("movie", "episode"):
            continue
        offset = getattr(it, "viewOffset", None) or 0
        duration = getattr(it, "duration", None) or 0
        last = getattr(it, "lastViewedAt", None)
        if not offset or not duration or not last:
            continue
        progress = offset / duration
        if progress >= ABANDON_MAX_PROGRESS or offset / 60000 < ABANDON_MIN_MINUTES:
            continue
        if (now - last) < timedelta(days=ABANDON_STALE_DAYS):
            continue  # recent: probably just paused, not abandoned
        source_key = str(it.ratingKey)
        rating_key = (
            (_key_from_path(getattr(it, "grandparentKey", None)) or source_key) if it.type == "episode" else source_key
        )
        events.append(
            {
                "rating_key": rating_key,
                "source_key": source_key,
                "account_id": None,
                "media_type": it.type,
                "event_type": "abandoned",
                "event_value": None,
                "event_timestamp": _ts(last),
                "watch_progress": round(progress, 3),
            }
        )
    return events


def build_rating_events(items: list[Any]) -> list[dict[str, Any]]:
    """Rated items -> rated events. Timestamp is deterministic so re-syncing never duplicates."""
    events: list[dict[str, Any]] = []
    for it in items:
        rating = getattr(it, "userRating", None)
        when = getattr(it, "lastRatedAt", None) or getattr(it, "lastViewedAt", None) or getattr(it, "addedAt", None)
        if rating is None or when is None:
            continue
        key = str(it.ratingKey)
        events.append(
            {
                "rating_key": key,
                "source_key": key,
                "account_id": None,
                "media_type": it.type,
                "event_type": "rated",
                "event_value": float(rating),
                "event_timestamp": _ts(when),
                "watch_progress": None,
            }
        )
    return events


# --- item dimensions ------------------------------------------------------------


def _tags(item: Any, attr: str) -> list[str]:
    return [getattr(x, "tag", x) for x in (getattr(item, attr, None) or [])]


def _meta_from_plex(item: Any) -> dict[str, Any]:
    return {
        "genres": _tags(item, "genres"),
        "directors": _tags(item, "directors"),
        "actors": _tags(item, "roles"),
        "countries": _tags(item, "countries"),
        "year": getattr(item, "year", None),
        "duration_min": (getattr(item, "duration", None) or 0) / 60000,
    }


def _merge_enrichment(meta: dict[str, Any], rating_key: str) -> dict[str, Any]:
    """Add enrichment themes to Plex-native metadata.

    Only themes, deliberately: the library baseline is built from Plex-native tags, so letting
    TMDB director/cast/country in for just the enriched items would inflate their watch share
    against a baseline that never saw those values. Theme dimensions have no baseline yet, so
    they are recorded but not scored until one exists (needs broad enrichment coverage).
    """
    row = enrichment_db.load_enrichment(rating_key)
    if not row:
        return meta
    return {**meta, "themes": row.get("themes") or []}


def resolve_dimensions(server: Any, rating_key: str, max_age_days: float | None = DIMENSION_TTL_DAYS) -> list[str]:
    """Dimensions for one item: cached, else fetched from Plex (+ enrichment) and cached. Blocking."""
    cached = db.load_item_dimensions(rating_key, max_age_days=max_age_days)
    if cached is not None:
        return cached
    from plexapi.exceptions import NotFound

    try:
        item = server.fetchItem(int(rating_key))
    except NotFound:
        db.save_item_dimensions(rating_key, "", "", [])  # gone from Plex: don't retry forever
        return []
    except Exception as e:
        logger.warning("Could not fetch Plex item %s (will retry next sync): %s", rating_key, e)
        return []
    dims = dimensions_from_meta(_merge_enrichment(_meta_from_plex(item), rating_key))
    db.save_item_dimensions(rating_key, getattr(item, "type", ""), getattr(item, "title", ""), dims)
    return dims


def resolve_all(server: Any, keys: list[str], max_age_days: float | None) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    total = len(keys)
    for i, key in enumerate(keys, 1):
        out[key] = resolve_dimensions(server, key, max_age_days=max_age_days)
        if i % 25 == 0 or i == total:
            _set_progress(phase="resolving", message=f"Reading metadata {i}/{total}", done=i, total=total)
    return out


# --- sync ---------------------------------------------------------------------


async def _collect_events(
    server: Any, since: datetime | None, include_ratings: bool
) -> tuple[list[dict[str, Any]], str | None]:
    """Gather events from Plex. Returns (events, history_cursor); the caller advances the cursor
    only after the events are safely stored, so a mid-way failure can't skip any."""
    kwargs: dict[str, Any] = {"mindate": since} if since else {}
    _set_progress(phase="history", message="Reading Plex watch history...")
    entries = await asyncio.to_thread(server.history, **kwargs)
    events = build_history_events(entries, db.seen_source_keys())
    cursor = max((e["event_timestamp"] for e in events), default=None)

    _set_progress(phase="in_progress", message="Checking for abandoned items...")
    on_deck = await asyncio.to_thread(server.library.onDeck)
    events += build_abandoned_events(on_deck)

    if include_ratings:
        _set_progress(phase="ratings", message="Reading your ratings...")

        def _rated() -> list[Any]:
            found: list[Any] = []
            for section in server.library.sections():
                if section.type in ("movie", "show"):
                    found += section.search(userRating__gte=0.1)
            return found

        events += build_rating_events(await asyncio.to_thread(_rated))
    return events, cursor


def build_library_baseline(server: Any) -> tuple[dict[str, int], dict[str, int]]:
    """Count how many library items of each kind carry each dimension (the 'what's available'
    side of lift). Returns ({"kind:dimension": n}, {kind: items}). Blocking.

    One listing per section already includes genres/directors/roles/countries, so this is
    ~1s per 1,000 items. Episodes roll up to their show: the unit is movie or show.
    """
    sections = [s for s in server.library.sections() if s.type in ("movie", "show")]
    counts: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    for i, section in enumerate(sections, 1):
        _set_progress(phase="baseline", message=f"Surveying library {i}/{len(sections)}: {section.title}")
        kind = kind_of(section.type)
        for item in section.all():
            sizes[kind] += 1
            counts.update(f"{kind}:{d}" for d in dimensions_from_meta(_meta_from_plex(item)))
    # Dimensions carried by a single item can't be judged against; keeping them would only bloat the table.
    return {d: n for d, n in counts.items() if n >= MIN_BASELINE_COUNT}, dict(sizes)


async def rebuild_from_history(
    server: Any, refresh_dimensions: bool = False, refresh_baseline: bool = False
) -> dict[str, Any]:
    """Re-derive the whole profile from full Plex history, abandonment and ratings."""
    async with _get_run_lock():
        _set_progress(phase="starting", message="Rebuilding taste profile...", done=0, total=0)
        events, cursor = await _collect_events(server, since=None, include_ratings=True)
        new = db.insert_events(events)
        if cursor:
            db.set_meta("last_history_ts", cursor)

        if refresh_baseline or not db.load_library()[1]:
            counts, sizes = await asyncio.to_thread(build_library_baseline, server)
            db.replace_library(counts, sizes)

        all_events = db.all_events()
        keys = sorted({e["rating_key"] for e in all_events})
        dims_lookup = await asyncio.to_thread(resolve_all, server, keys, 0 if refresh_dimensions else None)

        _set_progress(phase="scoring", message="Scoring...")
        profile, stats = replay(all_events, dims_lookup)
        db.replace_profile(profile)
        db.set_meta("rebuilt_at", datetime.now().strftime(TS_FORMAT))
        summary = {
            "events_total": len(all_events),
            "events_new": len(new),
            "items": len(keys),
            "dimensions": len(profile.dims),
            "library_items": sum(db.load_library()[1].values()),
            **stats,
        }
        _set_progress(phase="complete", message=f"Profile built from {len(all_events)} events.", **summary)
        return summary


async def sync(server: Any, include_ratings: bool = False) -> dict[str, Any]:
    """Incremental sync: new events since last time, applied to the existing profile."""
    if not db.get_meta("last_history_ts"):
        return await rebuild_from_history(server)
    async with _get_run_lock():
        since = datetime.strptime(db.get_meta("last_history_ts"), TS_FORMAT) + timedelta(seconds=1)
        episode_counts = db.episode_event_counts()  # BEFORE inserting: seeds the concave episode weighting
        events, cursor = await _collect_events(server, since=since, include_ratings=include_ratings)
        new = sorted(db.insert_events(events), key=lambda e: e["event_timestamp"])
        if cursor:
            db.set_meta("last_history_ts", cursor)

        keys = sorted({e["rating_key"] for e in new})
        dims_lookup = await asyncio.to_thread(resolve_all, server, keys, DIMENSION_TTL_DAYS) if keys else {}

        profile = db.load_profile()
        t_dims: set[str] = set()
        t_temporal: set[tuple[str, str]] = set()
        t_totals: set[str] = set()
        applied = 0
        for e in new:
            k = 1
            if e["media_type"] == "episode" and e["event_type"] != "rated":
                episode_counts[e["rating_key"]] = k = episode_counts.get(e["rating_key"], 0) + 1
            sw = event_sign_weight(e["event_type"], e.get("event_value"), e["media_type"], k)
            dims = dims_lookup.get(e["rating_key"])
            if sw is None or not dims:
                continue
            when = datetime.strptime(e["event_timestamp"], TS_FORMAT)
            a, b, c = profile.apply(dims, sw[0], sw[1], when, classify_time_bucket(when), kind_of(e["media_type"]))
            t_dims |= a
            t_temporal |= b
            t_totals |= c
            applied += 1
        db.upsert_profile(profile, t_dims, t_temporal, t_totals)
        summary = {"events_new": len(new), "events_applied": applied}
        _set_progress(phase="complete", message=f"Synced {len(new)} new event(s).", **summary)
        return summary


def status() -> dict[str, Any]:
    return {
        "events": db.count_events(),
        "dimensions": len(db.load_profile().dims),
        "library_items": sum(db.load_library()[1].values()),
        "last_history_ts": db.get_meta("last_history_ts"),
        "rebuilt_at": db.get_meta("rebuilt_at"),
        "built": bool(db.get_meta("rebuilt_at")),
        "running": is_running(),
        "progress": get_progress(),
    }

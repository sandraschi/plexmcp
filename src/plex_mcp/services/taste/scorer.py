"""Pure taste-accumulation logic: event rules, decayed attention sums, dimensions, replay.

Model (a deliberate refinement of the spec's capped-EMA, see docs/plans/TASTE_MODELLING.md):
each dimension accumulates *exponentially decayed attention* from positive and
negative events. Shares of attention are later compared against the library's
own composition (ranker.py) so a score means "watched more/less than what was
available", not merely "watched". A capped EMA over mostly-positive history
saturates every touched dimension at +1 and carries no information.

No I/O here, so everything is unit-testable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

HALF_LIFE_DAYS = 365.0
TOP_ACTORS = 3

# An episode is a weak, repeating signal about the *show*. The k-th episode event
# of a show weighs EPISODE_FACTOR / sqrt(k): 200 episodes ~ 7 movie-views, not 50.
EPISODE_FACTOR = 0.25

# event_type -> (sign, weight)
EVENT_RULES: dict[str, tuple[int, float]] = {
    "completed": (1, 1.0),
    "rewatched": (1, 2.0),
    # Abandonment is dampened: stopping is often not taste (fell asleep, interrupted).
    "abandoned": (-1, 0.5),
    "on_deck_dismissed": (-1, 0.3),
}

# Plex userRating is 0-10 (4 stars == 8.0, 2 stars == 4.0).
RATING_HIGH = 8.0
RATING_LOW = 4.0
RATING_WEIGHT = 2.0

TIME_BUCKETS = (
    "weekday_morning",
    "weekday_afternoon",
    "weekday_evening",
    "saturday_morning",
    "sunday_morning",
    "weekend_afternoon",
    "weekend_evening",
    "late_night",
)

ALL_SCOPE = "all"
KINDS = ("movie", "show")


def kind_of(media_type: str) -> str:
    """Movies and TV are different populations (shows have no director/country in Plex, use
    different genre names, and are watched in far larger volume), so every score is computed
    within one kind and never across them."""
    return "movie" if media_type == "movie" else "show"


def event_sign_weight(
    event_type: str, event_value: float | None = None, media_type: str = "movie", episode_index: int = 1
) -> tuple[int, float] | None:
    """Return (sign, weight) for an event, or None when it carries no taste information."""
    if event_type == "rated":
        if event_value is None:
            return None
        if event_value >= RATING_HIGH:
            return 1, RATING_WEIGHT
        if event_value <= RATING_LOW:
            return -1, RATING_WEIGHT
        return None  # a middling rating is neutral, not evidence
    rule = EVENT_RULES.get(event_type)
    if rule is None:
        return None
    sign, weight = rule
    if media_type == "episode":
        weight *= EPISODE_FACTOR / math.sqrt(max(episode_index, 1))
    return sign, weight


def to_days(dt: datetime) -> float:
    return dt.timestamp() / 86400.0


def decay_factor(elapsed_days: float) -> float:
    return 0.5 ** (max(elapsed_days, 0.0) / HALF_LIFE_DAYS)


def classify_time_bucket(dt: datetime) -> str:
    hour, weekday = dt.hour, dt.weekday()  # Monday == 0
    if hour >= 23 or hour < 5:
        return "late_night"
    if weekday < 5:
        if hour < 12:
            return "weekday_morning"
        return "weekday_afternoon" if hour < 17 else "weekday_evening"
    if hour < 12:
        return "saturday_morning" if weekday == 5 else "sunday_morning"
    return "weekend_afternoon" if hour < 17 else "weekend_evening"


def runtime_bucket(minutes: float | None) -> str | None:
    if not minutes or minutes <= 0:
        return None
    for limit, label in ((30, "<30min"), (60, "30-60min"), (90, "60-90min"), (120, "90-120min"), (150, "120-150min")):
        if minutes < limit:
            return label
    return "150+min"


def _norm(value: Any) -> str:
    return str(value).strip().lower()


def dimensions_from_meta(meta: dict[str, Any]) -> list[str]:
    """Derive taste dimensions from a unified metadata dict.

    Keys (all optional): genres, directors, actors, themes, countries (lists),
    year (int), duration_min (number). Unknown fields are ignored.
    """
    dims: list[str] = []

    def add(prefix: str, values: Any) -> None:
        for v in values or []:
            if v is not None and _norm(v):
                dims.append(f"{prefix}:{_norm(v)}")

    add("genre", meta.get("genres"))
    add("director", meta.get("directors"))
    add("actor", (meta.get("actors") or [])[:TOP_ACTORS])
    add("theme", meta.get("themes"))
    add("country", meta.get("countries"))

    year = meta.get("year")
    if isinstance(year, int) and year > 1800:
        dims.append(f"decade:{year // 10 * 10}s")
    rt = runtime_bucket(meta.get("duration_min"))
    if rt:
        dims.append(f"runtime:{rt}")

    return list(dict.fromkeys(dims))


# An entry is [positive_attention, negative_attention, as_of_days]
Entry = list[float]


def _add(entry: Entry | None, sign: int, weight: float, now_days: float) -> Entry:
    if entry is None:
        entry = [0.0, 0.0, now_days]
    else:
        f = decay_factor(now_days - entry[2])
        entry[0] *= f
        entry[1] *= f
        entry[2] = now_days
    entry[0 if sign > 0 else 1] += weight
    return entry


def value_at(entry: Entry | None, now_days: float) -> tuple[float, float]:
    """(positive, negative) attention of an entry decayed to `now_days`."""
    if entry is None:
        return 0.0, 0.0
    f = decay_factor(now_days - entry[2])
    return entry[0] * f, entry[1] * f


def total_scope(kind: str, bucket: str | None = None) -> str:
    return kind if not bucket or bucket == ALL_SCOPE else f"{kind}/{bucket}"


@dataclass
class Profile:
    """Decayed attention per "kind:dimension", per time-bucket x "kind:dimension", and per
    scope (totals, keyed "movie", "show", "movie/late_night", ...)."""

    dims: dict[str, Entry] = field(default_factory=dict)
    temporal: dict[tuple[str, str], Entry] = field(default_factory=dict)
    totals: dict[str, Entry] = field(default_factory=dict)

    def apply(
        self, dims: list[str], sign: int, weight: float, when: datetime, bucket: str | None, kind: str
    ) -> tuple[set[str], set[tuple[str, str]], set[str]]:
        """Add one event. Returns the (dimension, temporal, totals) keys that changed."""
        now = to_days(when)
        t_dims: set[str] = set()
        t_temporal: set[tuple[str, str]] = set()
        scopes = {total_scope(kind)}
        if bucket:
            scopes.add(total_scope(kind, bucket))
        for scope in scopes:
            self.totals[scope] = _add(self.totals.get(scope), sign, weight, now)
        for d in dims:
            key = f"{kind}:{d}"
            self.dims[key] = _add(self.dims.get(key), sign, weight, now)
            t_dims.add(key)
            if bucket:
                self.temporal[(bucket, key)] = _add(self.temporal.get((bucket, key)), sign, weight, now)
                t_temporal.add((bucket, key))
        return t_dims, t_temporal, scopes


def replay(
    events: list[dict[str, Any]],
    dims_lookup: dict[str, list[str]],
    until: str | None = None,
    episode_counts: dict[str, int] | None = None,
) -> tuple[Profile, dict[str, int]]:
    """Rebuild a profile from events (chronological). `until` excludes events at/after that moment.

    `episode_counts` seeds the per-show episode counter (incremental sync passes the
    counts of events that already exist); it is mutated in place.
    """
    profile = Profile()
    counts = episode_counts if episode_counts is not None else {}
    stats = {"applied": 0, "no_signal": 0, "no_dimensions": 0}
    for e in events:
        if until and e["event_timestamp"] >= until:
            break
        media_type = e.get("media_type", "movie")
        k = 1
        if media_type == "episode" and e["event_type"] != "rated":
            counts[e["rating_key"]] = k = counts.get(e["rating_key"], 0) + 1
        sw = event_sign_weight(e["event_type"], e.get("event_value"), media_type, k)
        if sw is None:
            stats["no_signal"] += 1
            continue
        dims = dims_lookup.get(e["rating_key"])
        if not dims:
            stats["no_dimensions"] += 1
            continue
        when = datetime.fromisoformat(e["event_timestamp"])
        profile.apply(dims, sw[0], sw[1], when, classify_time_bucket(when), kind_of(media_type))
        stats["applied"] += 1
    return profile, stats

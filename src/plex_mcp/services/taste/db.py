"""SQLite storage for taste modelling (events, attention profile, library baseline, item dimensions)."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .scorer import Profile

_lock = threading.Lock()
_db_path: Path | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS watch_events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    rating_key        TEXT NOT NULL,
    source_key        TEXT NOT NULL,
    account_id        INTEGER,
    media_type        TEXT NOT NULL,
    event_type        TEXT NOT NULL,
    event_value       REAL,
    event_timestamp   TEXT NOT NULL,
    watch_progress    REAL,
    UNIQUE(source_key, event_type, event_timestamp)
);
CREATE INDEX IF NOT EXISTS idx_watch_events_key ON watch_events(rating_key);
CREATE INDEX IF NOT EXISTS idx_watch_events_time ON watch_events(event_timestamp);

CREATE TABLE IF NOT EXISTS taste_profile (
    dimension     TEXT PRIMARY KEY,
    pos           REAL NOT NULL,
    neg           REAL NOT NULL,
    as_of         REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS temporal_taste (
    time_bucket   TEXT NOT NULL,
    dimension     TEXT NOT NULL,
    pos           REAL NOT NULL,
    neg           REAL NOT NULL,
    as_of         REAL NOT NULL,
    PRIMARY KEY (time_bucket, dimension)
);

CREATE TABLE IF NOT EXISTS taste_totals (
    scope         TEXT PRIMARY KEY,
    pos           REAL NOT NULL,
    neg           REAL NOT NULL,
    as_of         REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS library_dimensions (
    dimension     TEXT PRIMARY KEY,
    item_count    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS item_dimensions (
    rating_key    TEXT PRIMARY KEY,
    media_type    TEXT,
    title         TEXT,
    dims          TEXT NOT NULL,
    fetched_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS taste_meta (
    key           TEXT PRIMARY KEY,
    value         TEXT
);
"""


def set_db_path(path: str | Path) -> None:
    global _db_path
    with _lock:
        _db_path = Path(path)


def get_db_path() -> Path:
    if _db_path:
        return _db_path
    # src/plex_mcp/services/taste/db.py -> repo_root/data/taste.db
    return Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "taste.db"


def get_connection() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    with _lock:
        conn.executescript(SCHEMA)
        conn.commit()
    return conn


# --- meta -------------------------------------------------------------------


def get_meta(key: str) -> str | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM taste_meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None
    finally:
        conn.close()


def set_meta(key: str, value: str) -> None:
    conn = get_connection()
    try:
        with _lock, conn:
            conn.execute(
                "INSERT INTO taste_meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
    finally:
        conn.close()


# --- events -----------------------------------------------------------------


def insert_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Insert events, ignoring duplicates. Returns only the events that were actually new."""
    if not events:
        return []
    conn = get_connection()
    new: list[dict[str, Any]] = []
    try:
        with _lock, conn:
            for e in events:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO watch_events "
                    "(rating_key, source_key, account_id, media_type, event_type, event_value, "
                    "event_timestamp, watch_progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        e["rating_key"],
                        e["source_key"],
                        e.get("account_id"),
                        e["media_type"],
                        e["event_type"],
                        e.get("event_value"),
                        e["event_timestamp"],
                        e.get("watch_progress"),
                    ),
                )
                if cur.rowcount:
                    new.append(e)
    finally:
        conn.close()
    return new


def all_events() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM watch_events ORDER BY event_timestamp, id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def seen_source_keys() -> set[str]:
    """Source keys that already have a completed/rewatched event (for rewatch detection)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT source_key FROM watch_events WHERE event_type IN ('completed', 'rewatched')"
        ).fetchall()
        return {r["source_key"] for r in rows}
    finally:
        conn.close()


def episode_event_counts() -> dict[str, int]:
    """Per-show count of existing episode events (seeds the concave episode weighting)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT rating_key, COUNT(*) AS n FROM watch_events "
            "WHERE media_type = 'episode' AND event_type != 'rated' GROUP BY rating_key"
        ).fetchall()
        return {r["rating_key"]: r["n"] for r in rows}
    finally:
        conn.close()


def count_events() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM watch_events").fetchone()[0]
    finally:
        conn.close()


# --- item dimensions ----------------------------------------------------------


def save_item_dimensions(rating_key: str, media_type: str, title: str, dims: list[str]) -> None:
    conn = get_connection()
    try:
        with _lock, conn:
            conn.execute(
                "INSERT INTO item_dimensions (rating_key, media_type, title, dims, fetched_at) "
                "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP) "
                "ON CONFLICT(rating_key) DO UPDATE SET media_type=excluded.media_type, "
                "title=excluded.title, dims=excluded.dims, fetched_at=CURRENT_TIMESTAMP",
                (rating_key, media_type, title, json.dumps(dims, ensure_ascii=False)),
            )
    finally:
        conn.close()


def load_item_dimensions(rating_key: str, max_age_days: float | None = 30) -> list[str] | None:
    conn = get_connection()
    try:
        if max_age_days is None:
            row = conn.execute("SELECT dims FROM item_dimensions WHERE rating_key = ?", (rating_key,)).fetchone()
        else:
            row = conn.execute(
                "SELECT dims FROM item_dimensions WHERE rating_key = ? AND julianday('now') - julianday(fetched_at) < ?",
                (rating_key, max_age_days),
            ).fetchone()
        return json.loads(row["dims"]) if row else None
    finally:
        conn.close()


def all_item_dimensions() -> dict[str, list[str]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT rating_key, dims FROM item_dimensions").fetchall()
        return {r["rating_key"]: json.loads(r["dims"]) for r in rows}
    finally:
        conn.close()


# --- profile ----------------------------------------------------------------


def replace_profile(profile: Profile) -> None:
    """Wipe and write the whole profile (used by rebuild)."""
    conn = get_connection()
    try:
        with _lock, conn:
            conn.execute("DELETE FROM taste_profile")
            conn.execute("DELETE FROM temporal_taste")
            conn.execute("DELETE FROM taste_totals")
            conn.executemany(
                "INSERT INTO taste_profile (dimension, pos, neg, as_of) VALUES (?, ?, ?, ?)",
                [(d, *e) for d, e in profile.dims.items()],
            )
            conn.executemany(
                "INSERT INTO temporal_taste (time_bucket, dimension, pos, neg, as_of) VALUES (?, ?, ?, ?, ?)",
                [(b, d, *e) for (b, d), e in profile.temporal.items()],
            )
            conn.executemany(
                "INSERT INTO taste_totals (scope, pos, neg, as_of) VALUES (?, ?, ?, ?)",
                [(s, *e) for s, e in profile.totals.items()],
            )
    finally:
        conn.close()


def upsert_profile(profile: Profile, dims: set[str], temporal: set[tuple[str, str]], totals: set[str]) -> None:
    """Write only the touched entries (used by incremental sync)."""
    conn = get_connection()
    try:
        with _lock, conn:
            conn.executemany(
                "INSERT INTO taste_profile (dimension, pos, neg, as_of) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(dimension) DO UPDATE SET pos=excluded.pos, neg=excluded.neg, as_of=excluded.as_of",
                [(d, *profile.dims[d]) for d in dims],
            )
            conn.executemany(
                "INSERT INTO temporal_taste (time_bucket, dimension, pos, neg, as_of) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(time_bucket, dimension) DO UPDATE SET "
                "pos=excluded.pos, neg=excluded.neg, as_of=excluded.as_of",
                [(b, d, *profile.temporal[(b, d)]) for (b, d) in temporal],
            )
            conn.executemany(
                "INSERT INTO taste_totals (scope, pos, neg, as_of) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(scope) DO UPDATE SET pos=excluded.pos, neg=excluded.neg, as_of=excluded.as_of",
                [(s, *profile.totals[s]) for s in totals],
            )
    finally:
        conn.close()


def load_profile() -> Profile:
    conn = get_connection()
    try:
        profile = Profile()
        for r in conn.execute("SELECT dimension, pos, neg, as_of FROM taste_profile"):
            profile.dims[r["dimension"]] = [r["pos"], r["neg"], r["as_of"]]
        for r in conn.execute("SELECT time_bucket, dimension, pos, neg, as_of FROM temporal_taste"):
            profile.temporal[(r["time_bucket"], r["dimension"])] = [r["pos"], r["neg"], r["as_of"]]
        for r in conn.execute("SELECT scope, pos, neg, as_of FROM taste_totals"):
            profile.totals[r["scope"]] = [r["pos"], r["neg"], r["as_of"]]
        return profile
    finally:
        conn.close()


# --- library baseline -----------------------------------------------------------


def replace_library(counts: dict[str, int], sizes: dict[str, int]) -> None:
    """`counts` keys are "kind:dimension"; `sizes` maps kind -> number of library items."""
    conn = get_connection()
    try:
        with _lock, conn:
            conn.execute("DELETE FROM library_dimensions")
            conn.executemany(
                "INSERT INTO library_dimensions (dimension, item_count) VALUES (?, ?)", list(counts.items())
            )
            conn.execute(
                "INSERT INTO taste_meta (key, value) VALUES ('library_sizes', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (json.dumps(sizes),),
            )
            conn.execute(
                "INSERT INTO taste_meta (key, value) VALUES ('baseline_at', datetime('now', 'localtime')) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value"
            )
    finally:
        conn.close()


def load_library() -> tuple[dict[str, int], dict[str, int]]:
    """(counts keyed "kind:dimension", sizes keyed by kind)."""
    conn = get_connection()
    try:
        counts = {
            r["dimension"]: r["item_count"]
            for r in conn.execute("SELECT dimension, item_count FROM library_dimensions")
        }
        row = conn.execute("SELECT value FROM taste_meta WHERE key = 'library_sizes'").fetchone()
        return counts, json.loads(row["value"]) if row else {}
    finally:
        conn.close()

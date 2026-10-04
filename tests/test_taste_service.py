"""Tests for taste modelling: scorer, ranker, event builders, and sync against a fake Plex.

No network. The taste and enrichment sqlite files are redirected to tmp_path.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from plexapi.exceptions import NotFound

from plex_mcp.services.enrichment import db as enrichment_db
from plex_mcp.services.taste import db, ranker, sync
from plex_mcp.services.taste.scorer import (
    HALF_LIFE_DAYS,
    Profile,
    classify_time_bucket,
    dimensions_from_meta,
    event_sign_weight,
    kind_of,
    replay,
    to_days,
    value_at,
)

NOW = datetime(2026, 10, 4, 12, 0, 0)


@pytest.fixture(autouse=True)
def isolated_dbs(tmp_path):
    db.set_db_path(tmp_path / "taste_test.db")
    enrichment_db.set_db_path(tmp_path / "enrichment_for_taste_test.db")
    sync._run_lock = None  # a lock created under a previous test's event loop must not leak
    yield


def ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def event(key, when, event_type="completed", media_type="movie", value=None, source=None):
    return {
        "rating_key": key,
        "source_key": source or key,
        "account_id": 1,
        "media_type": media_type,
        "event_type": event_type,
        "event_value": value,
        "event_timestamp": ts(when),
        "watch_progress": 1.0,
    }


# --- scorer ---------------------------------------------------------------------


def test_event_rules():
    assert event_sign_weight("completed") == (1, 1.0)
    assert event_sign_weight("rewatched") == (1, 2.0)
    assert event_sign_weight("abandoned") == (-1, 0.5)
    assert event_sign_weight("nonsense") is None


def test_ratings_high_low_and_neutral():
    assert event_sign_weight("rated", 10.0) == (1, 2.0)
    assert event_sign_weight("rated", 8.0) == (1, 2.0)
    assert event_sign_weight("rated", 4.0) == (-1, 2.0)
    assert event_sign_weight("rated", 6.0) is None  # middling rating is not evidence
    assert event_sign_weight("rated", None) is None


def test_episode_weight_is_concave_per_show():
    first = event_sign_weight("completed", media_type="episode", episode_index=1)[1]
    fourth = event_sign_weight("completed", media_type="episode", episode_index=4)[1]
    assert first == pytest.approx(0.25)
    assert fourth == pytest.approx(0.125)
    # 200 episodes must weigh like a handful of movies, not 50 of them
    total = sum(event_sign_weight("completed", media_type="episode", episode_index=k)[1] for k in range(1, 201))
    assert 5 < total < 10


def test_rating_weight_not_reduced_for_shows():
    assert event_sign_weight("rated", 10.0, media_type="show") == (1, 2.0)


@pytest.mark.parametrize(
    ("when", "bucket"),
    [
        (datetime(2026, 10, 4, 9), "sunday_morning"),  # Sunday
        (datetime(2026, 10, 3, 9), "saturday_morning"),
        (datetime(2026, 10, 6, 20), "weekday_evening"),  # Tuesday
        (datetime(2026, 10, 7, 2), "late_night"),
        (datetime(2026, 10, 3, 14), "weekend_afternoon"),
        (datetime(2026, 10, 3, 19), "weekend_evening"),
        (datetime(2026, 10, 5, 9), "weekday_morning"),
        (datetime(2026, 10, 5, 14), "weekday_afternoon"),
        (datetime(2026, 10, 5, 23), "late_night"),
    ],
)
def test_time_buckets(when, bucket):
    assert classify_time_bucket(when) == bucket


def test_dimensions_from_meta():
    dims = dimensions_from_meta(
        {
            "genres": ["Thriller", "Drama"],
            "directors": ["Michael Mann"],
            "actors": ["A", "B", "C", "D"],
            "themes": ["heist"],
            "countries": ["United States of America"],
            "year": 1995,
            "duration_min": 170,
        }
    )
    assert "genre:thriller" in dims
    assert "director:michael mann" in dims
    assert {"actor:a", "actor:b", "actor:c"} <= set(dims)
    assert "actor:d" not in dims  # only top 3 cast
    assert "theme:heist" in dims
    assert "country:united states of america" in dims
    assert "decade:1990s" in dims
    assert "runtime:150+min" in dims


def test_dimensions_dedupe_and_ignore_blanks():
    dims = dimensions_from_meta({"genres": ["Comedy", "comedy", " ", None], "year": None, "duration_min": 0})
    assert dims == ["genre:comedy"]


def test_kind_of():
    assert kind_of("movie") == "movie"
    assert kind_of("episode") == "show"
    assert kind_of("show") == "show"


def test_attention_halves_after_one_half_life():
    profile = Profile()
    profile.apply(["genre:x"], 1, 1.0, NOW, None, "movie")
    entry = profile.dims["movie:genre:x"]
    now_days = to_days(NOW)
    assert value_at(entry, now_days)[0] == pytest.approx(1.0)
    assert value_at(entry, now_days + HALF_LIFE_DAYS)[0] == pytest.approx(0.5)


def test_profile_keeps_movies_and_shows_apart():
    profile = Profile()
    profile.apply(["genre:comedy"], 1, 1.0, NOW, "late_night", "movie")
    assert "movie:genre:comedy" in profile.dims
    assert "show:genre:comedy" not in profile.dims
    assert "movie" in profile.totals
    assert "show" not in profile.totals
    assert "movie/late_night" in profile.totals


def test_replay_applies_and_counts_skips():
    events = [
        event("1", NOW - timedelta(days=3)),
        event("2", NOW - timedelta(days=2), event_type="rated", value=6.0),  # neutral -> no signal
        event("3", NOW - timedelta(days=1)),  # no known dimensions
    ]
    profile, stats = replay(events, {"1": ["genre:a"], "2": ["genre:a"]})
    assert stats == {"applied": 1, "no_signal": 1, "no_dimensions": 1}
    assert "movie:genre:a" in profile.dims


def test_replay_until_excludes_later_events():
    events = [event("1", NOW - timedelta(days=40)), event("1", NOW - timedelta(days=1), source="1b")]
    profile, stats = replay(events, {"1": ["genre:a"]}, until=ts(NOW - timedelta(days=30)))
    assert stats["applied"] == 1


def test_replay_episode_counter_is_per_show():
    events = [event("S", NOW - timedelta(days=i), media_type="episode", source=f"e{i}") for i in (3, 2, 1)]
    profile, _ = replay(events, {"S": ["genre:a"]})
    total_pos = profile.totals["show"][0]
    expected = 0.25 + 0.25 / 2**0.5 + 0.25 / 3**0.5
    assert total_pos == pytest.approx(expected, rel=0.01)  # tiny decay between days


# --- ranker -----------------------------------------------------------------------


def test_lift_bounds():
    assert ranker.lift(0.5, 0.5) == 0
    assert ranker.lift(1.0, 0.0) == 1.0
    assert ranker.lift(0.0, 0.5) == -1.0
    assert ranker.lift(0.0, 0.0) == 0.0


def _scores(profile, counts, sizes, kind="movie", now=NOW, scope="all"):
    return ranker.compute_scores(profile, counts, sizes, to_days(now), kind, scope=scope)


def test_everything_watched_everything_available_scores_neutral():
    """Regression: a capped EMA over all-positive history saturates every dimension at +1.
    Lift against the library must give 0 when attention simply mirrors what's available."""
    profile = Profile()
    for i in range(20):
        profile.apply(["genre:a", "genre:b"], 1, 1.0, NOW - timedelta(days=i), None, "movie")
    counts = {"movie:genre:a": 100, "movie:genre:b": 100}
    scores = _scores(profile, counts, {"movie": 100})
    assert scores["genre:a"]["score"] == pytest.approx(0.0, abs=0.01)
    assert scores["genre:b"]["score"] == pytest.approx(0.0, abs=0.01)


def test_likes_dislikes_and_unseen_dimensions():
    profile = Profile()
    for i in range(30):
        profile.apply(["genre:thriller"], 1, 1.0, NOW - timedelta(days=i), None, "movie")
    counts = {"movie:genre:thriller": 20, "movie:genre:comedy": 60, "movie:genre:tiny": 3}
    scores = _scores(profile, counts, {"movie": 100})
    assert scores["genre:thriller"]["score"] > 0.5
    assert scores["genre:comedy"]["score"] == -1.0  # plentiful in the library, never watched
    assert "genre:tiny" not in scores  # too few library items to call it a dislike
    summary = ranker.summarize(scores)
    assert summary["likes"][0]["dimension"] == "genre:thriller"
    assert summary["dislikes"][0]["dimension"] == "genre:comedy"


def test_negative_events_pull_a_dimension_down():
    liked = Profile()
    disliked = Profile()
    for i in range(10):
        liked.apply(["genre:a"], 1, 1.0, NOW - timedelta(days=i), None, "movie")
        disliked.apply(["genre:a"], 1, 1.0, NOW - timedelta(days=i), None, "movie")
    for i in range(10):
        disliked.apply(["genre:a"], -1, 2.0, NOW - timedelta(days=i), None, "movie")
    counts = {"movie:genre:a": 30}
    assert (
        _scores(disliked, counts, {"movie": 100})["genre:a"]["score"]
        < _scores(liked, counts, {"movie": 100})["genre:a"]["score"]
    )


def test_scores_are_per_kind():
    profile = Profile()
    for i in range(10):
        profile.apply(["genre:a"], 1, 1.0, NOW - timedelta(days=i), None, "show")
    counts = {"movie:genre:a": 50, "show:genre:a": 10}
    sizes = {"movie": 100, "show": 20}
    assert _scores(profile, counts, sizes, kind="movie") == {}  # no movie watching at all
    assert _scores(profile, counts, sizes, kind="show")["genre:a"]["score"] > 0.3


def test_thin_time_bucket_is_not_scored():
    """With little viewing in a bucket, 'never watched here' is weak evidence, not a -1.00 dislike."""
    profile = Profile()
    for i in range(3):
        profile.apply(["genre:doc"], 1, 1.0, NOW - timedelta(days=i), "sunday_morning", "movie")
    counts = {"movie:genre:doc": 10, "movie:genre:drama": 60}
    assert _scores(profile, counts, {"movie": 100}, scope="sunday_morning") == {}
    assert _scores(profile, counts, {"movie": 100})  # the overall profile is unaffected


def test_temporal_scope_scores_only_that_bucket():
    profile = Profile()
    for i in range(15):
        profile.apply(["genre:doc"], 1, 1.0, NOW - timedelta(days=i), "sunday_morning", "movie")
    counts = {"movie:genre:doc": 10}
    sizes = {"movie": 100}
    assert _scores(profile, counts, sizes, scope="sunday_morning")["genre:doc"]["score"] > 0.5
    assert _scores(profile, counts, sizes, scope="late_night") == {}


def test_score_item_blend_and_confidence():
    scores = {
        "genre:a": {"score": 0.8, "evidence": 4.0},
        "genre:b": {"score": -0.4, "evidence": 1.0},
    }
    plain = ranker.score_item(["genre:a", "genre:b", "genre:unknown"], scores)
    assert plain["score"] == pytest.approx((0.8 * 4 - 0.4 * 1) / 5, abs=1e-3)
    assert plain["confidence"] == pytest.approx(2 / 3, abs=1e-3)
    assert plain["top_positive"][0]["dimension"] == "genre:a"
    assert plain["top_negative"][0]["dimension"] == "genre:b"

    temporal = {"genre:a": {"score": 0.0, "evidence": 1.0}}  # genre:b has no temporal evidence -> base score
    blended = ranker.score_item(["genre:a", "genre:b"], scores, temporal)
    assert blended["score"] == pytest.approx((0.7 * 0.8 * 4 - 0.4 * 1) / 5, abs=1e-3)


def test_score_item_with_nothing_known():
    result = ranker.score_item(["genre:x"], {})
    assert result["score"] == 0.0
    assert result["confidence"] == 0.0


def test_recent_shifts_finds_new_interest():
    events = []
    for i in range(60):  # long-standing interest, all older than 30 days
        events.append(event(f"old{i}", NOW - timedelta(days=100 + i), source=f"old{i}"))
    for i in range(40):  # brand-new interest in the last 2 weeks
        events.append(event(f"new{i}", NOW - timedelta(days=i % 14 + 1), source=f"new{i}"))
    events.sort(key=lambda e: e["event_timestamp"])
    dims = {f"old{i}": ["genre:western"] for i in range(60)} | {f"new{i}": ["genre:documentary"] for i in range(40)}
    counts = {"movie:genre:western": 40, "movie:genre:documentary": 40}
    shifts = ranker.recent_shifts(events, dims, counts, {"movie": 200}, "movie", days=30, now=NOW)
    by_dim = {s["dimension"]: s for s in shifts}
    assert by_dim["genre:documentary"]["delta"] > 0
    assert by_dim["genre:documentary"]["new"] is True
    assert by_dim["genre:western"]["delta"] < 0


# --- event builders (fake Plex objects) --------------------------------------------


def hist(rating_key, viewed_at, type_="movie", grandparent=None, account=1):
    return SimpleNamespace(
        ratingKey=rating_key,
        type=type_,
        viewedAt=viewed_at,
        grandparentKey=f"/library/metadata/{grandparent}" if grandparent else None,
        accountID=account,
    )


def test_history_events_rollup_rewatch_and_filters():
    entries = [
        hist(11, NOW - timedelta(days=1), "episode", grandparent=500),
        hist(10, NOW - timedelta(days=5)),
        hist(10, NOW - timedelta(days=2)),  # second view of the same movie -> rewatch
        hist(99, NOW, "track"),  # music: ignored
        hist(None, NOW, "movie"),  # item deleted from Plex: ignored
        SimpleNamespace(ratingKey=7, type="movie", viewedAt=None),  # no timestamp: ignored
    ]
    events = sync.build_history_events(entries, set())
    assert [e["event_type"] for e in events] == ["completed", "rewatched", "completed"]
    assert [e["rating_key"] for e in events] == ["10", "10", "500"]  # episode rolled up to show 500
    assert events[2]["source_key"] == "11"
    assert events == sorted(events, key=lambda e: e["event_timestamp"])


def test_history_rewatch_uses_previously_seen_keys():
    events = sync.build_history_events([hist(10, NOW)], {"10"})
    assert events[0]["event_type"] == "rewatched"


def item(rating_key, type_="movie", offset=None, duration=None, last_viewed=None, **kw):
    return SimpleNamespace(
        ratingKey=rating_key, type=type_, viewOffset=offset, duration=duration, lastViewedAt=last_viewed, **kw
    )


def test_abandoned_requires_low_progress_enough_time_and_staleness():
    hour = 60 * 60 * 1000
    stale = NOW - timedelta(days=30)
    items = [
        item(1, offset=20 * 60000, duration=2 * hour, last_viewed=stale),  # 17% of a 2h film, stale -> abandoned
        item(2, offset=5 * 60000, duration=2 * hour, last_viewed=stale),  # only 5 minutes in -> not enough to judge
        item(3, offset=int(1.2 * hour), duration=2 * hour, last_viewed=stale),  # 60% -> not abandoned
        item(4, offset=20 * 60000, duration=2 * hour, last_viewed=NOW - timedelta(days=2)),  # recent: just paused
        item(5, offset=0, duration=2 * hour, last_viewed=stale),  # up-next, never started
    ]
    events = sync.build_abandoned_events(items, now=NOW)
    assert [e["rating_key"] for e in events] == ["1"]
    assert events[0]["event_type"] == "abandoned"
    assert events[0]["watch_progress"] == pytest.approx(0.167, abs=0.01)


def test_rating_events_use_deterministic_timestamps():
    rated = SimpleNamespace(
        ratingKey=1, type="movie", userRating=10.0, lastRatedAt=NOW, lastViewedAt=None, addedAt=None
    )
    fallback = SimpleNamespace(
        ratingKey=2, type="show", userRating=2.0, lastRatedAt=None, lastViewedAt=NOW, addedAt=None
    )
    unrated = SimpleNamespace(
        ratingKey=3, type="movie", userRating=None, lastRatedAt=NOW, lastViewedAt=None, addedAt=None
    )
    undated = SimpleNamespace(
        ratingKey=4, type="movie", userRating=9.0, lastRatedAt=None, lastViewedAt=None, addedAt=None
    )
    events = sync.build_rating_events([rated, fallback, unrated, undated])
    assert [e["rating_key"] for e in events] == ["1", "2"]
    assert events[0]["event_value"] == 10.0
    assert events[1]["event_timestamp"] == ts(NOW)
    assert sync.build_rating_events([rated]) == sync.build_rating_events([rated])  # re-sync can't duplicate


# --- db + sync against a fake Plex server -------------------------------------------


def media(rating_key, type_, title, genres, year=2000, directors=(), roles=(), countries=(), duration=7200000):
    tag = lambda names: [SimpleNamespace(tag=n) for n in names]  # noqa: E731
    return SimpleNamespace(
        ratingKey=rating_key,
        type=type_,
        title=title,
        year=year,
        genres=tag(genres),
        directors=tag(directors),
        roles=tag(roles),
        countries=tag(countries),
        duration=duration,
        userRating=None,
        lastRatedAt=None,
        lastViewedAt=None,
        addedAt=None,
    )


class FakeSection:
    def __init__(self, type_, title, items):
        self.type = type_
        self.title = title
        self._items = items

    def all(self):
        return list(self._items)

    def search(self, **_kwargs):
        return [i for i in self._items if i.userRating]


class FakeServer:
    def __init__(self, items, history_entries, on_deck=None):
        self.items = {i.ratingKey: i for i in items}
        self.history_entries = history_entries
        self.on_deck = on_deck or []
        self.history_calls: list[dict] = []
        self.fail_on_deck = False
        movies = [i for i in items if i.type == "movie"]
        shows = [i for i in items if i.type == "show"]
        self._sections = [FakeSection("movie", "Movies", movies), FakeSection("show", "Shows", shows)]
        self.library = SimpleNamespace(
            sections=lambda: self._sections,
            sectionByID=lambda section_id: self._sections[int(section_id)],  # id 0 = movies, 1 = shows
            onDeck=self._on_deck,
        )

    def _on_deck(self):
        if self.fail_on_deck:
            raise RuntimeError("on-deck endpoint down")
        return self.on_deck

    def history(self, mindate=None):
        self.history_calls.append({"mindate": mindate})
        return [h for h in self.history_entries if mindate is None or h.viewedAt >= mindate]

    def fetchItem(self, key):  # noqa: N802 - mirrors the plexapi name
        if key not in self.items:
            raise NotFound("gone")
        return self.items[key]


def build_world():
    thrillers = [media(100 + i, "movie", f"Thriller {i}", ["Thriller"], directors=["Mann"]) for i in range(12)]
    comedies = [media(200 + i, "movie", f"Comedy {i}", ["Comedy"]) for i in range(24)]
    show = media(500, "show", "Space Show", ["Sci-Fi"], year=1990, duration=1800000)
    return [*thrillers, *comedies, show]


async def test_rebuild_builds_profile_baseline_and_scores():
    items = build_world()
    entries = [hist(100 + i, NOW - timedelta(days=40 - i)) for i in range(12)]  # all 12 thrillers watched
    entries += [hist(1000 + i, NOW - timedelta(days=20 - i), "episode", grandparent=500) for i in range(5)]
    server = FakeServer(items, entries)

    summary = await sync.rebuild_from_history(server)

    assert summary["events_total"] == 17
    assert summary["applied"] == 17
    counts, sizes = db.load_library()
    assert sizes == {"movie": 36, "show": 1}
    assert counts["movie:genre:thriller"] == 12
    assert counts["movie:genre:comedy"] == 24

    scores = ranker.compute_scores(db.load_profile(), counts, sizes, to_days(NOW), "movie")
    assert scores["genre:thriller"]["score"] > 0.5
    assert scores["genre:comedy"]["score"] == -1.0
    assert sync.status()["built"] is True


async def test_incremental_sync_applies_only_new_events_and_never_duplicates():
    items = build_world()
    entries = [hist(100 + i, NOW - timedelta(days=40 - i)) for i in range(5)]
    server = FakeServer(items, entries)
    await sync.rebuild_from_history(server)
    before = db.count_events()

    nothing = await sync.sync(server)
    assert nothing["events_new"] == 0
    assert db.count_events() == before

    cursor_before = datetime.strptime(db.get_meta("last_history_ts"), sync.TS_FORMAT)
    server.history_entries.append(hist(105, NOW - timedelta(days=1)))
    result = await sync.sync(server)
    assert result == {"events_new": 1, "events_applied": 1}
    assert db.count_events() == before + 1
    # incremental: asks Plex only for entries strictly after the previous cursor
    assert server.history_calls[-1]["mindate"] == cursor_before + timedelta(seconds=1)

    again = await sync.sync(server)
    assert again["events_new"] == 0  # re-syncing the same entry must not double count


async def test_incremental_equals_full_rebuild():
    items = build_world()
    entries = [hist(100 + i, NOW - timedelta(days=40 - i)) for i in range(8)]
    entries += [hist(1000 + i, NOW - timedelta(days=30 - i), "episode", grandparent=500) for i in range(6)]
    server = FakeServer(items, entries[:10])
    await sync.rebuild_from_history(server)
    server.history_entries = entries
    await sync.sync(server)
    incremental = db.load_profile()

    db.set_db_path(db.get_db_path().with_name("rebuilt.db"))
    await sync.rebuild_from_history(server)
    full = db.load_profile()

    assert incremental.dims.keys() == full.dims.keys()
    for key, entry in full.dims.items():
        assert incremental.dims[key][:2] == pytest.approx(entry[:2], rel=1e-6)
    for scope, entry in full.totals.items():
        assert incremental.totals[scope][:2] == pytest.approx(entry[:2], rel=1e-6)


async def test_cursor_does_not_advance_when_sync_fails_midway():
    items = build_world()
    server = FakeServer(items, [hist(100, NOW - timedelta(days=10))])
    await sync.rebuild_from_history(server)
    cursor = db.get_meta("last_history_ts")

    server.history_entries.append(hist(101, NOW - timedelta(days=1)))
    server.fail_on_deck = True
    with pytest.raises(RuntimeError):
        await sync.sync(server)
    assert db.get_meta("last_history_ts") == cursor  # nothing lost: next sync re-reads from the same point

    server.fail_on_deck = False
    result = await sync.sync(server)
    assert result["events_new"] == 1


async def test_deleted_item_is_cached_as_unresolvable_not_retried():
    server = FakeServer(build_world(), [hist(9999, NOW - timedelta(days=1))])  # 9999 not in Plex
    summary = await sync.rebuild_from_history(server)
    assert summary["no_dimensions"] == 1
    assert db.load_item_dimensions("9999", max_age_days=None) == []


async def test_sync_without_prior_build_does_a_full_rebuild():
    server = FakeServer(build_world(), [hist(100, NOW - timedelta(days=1))])
    result = await sync.sync(server)
    assert "events_total" in result  # went through rebuild_from_history


async def test_enrichment_contributes_themes_only():
    items = build_world()
    enrichment_db.save_enrichment(
        "100",
        media_type="movie",
        title="Thriller 0",
        year=2000,
        report_sections={},
        sources_fetched=["tmdb"],
        sources_failed=[],
        raw_data={"tmdb": {"director": "Someone Else", "countries": ["Fantasia"]}},
        themes=["heist"],
        director="Someone Else",
        tmdb_collection_id=None,
    )
    server = FakeServer(items, [hist(100, NOW - timedelta(days=1))])
    await sync.rebuild_from_history(server)
    dims = db.load_item_dimensions("100", max_age_days=None)
    assert "theme:heist" in dims
    assert "director:someone else" not in dims  # would break baseline consistency
    assert "country:fantasia" not in dims

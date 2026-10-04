"""Tests for the taste REST API (webapp/backend/app/api/taste.py) against a fake Plex server."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from plex_mcp.services.enrichment import db as enrichment_db
from plex_mcp.services.taste import db, sync
from tests.test_taste_service import NOW, FakeServer, build_world, hist

GET_SERVER = "plex_mcp.services.taste.sync.get_plex_server"


@pytest.fixture(autouse=True)
def isolated(tmp_path):
    db.set_db_path(tmp_path / "taste_api_test.db")
    enrichment_db.set_db_path(tmp_path / "enrichment_api_taste_test.db")
    sync._run_lock = None
    sync.mark_starting("idle")
    from webapp.backend.app.api import taste as taste_api

    taste_api._scheduled = False
    yield


def make_server():
    entries = [hist(100 + i, NOW - timedelta(days=40 - i)) for i in range(12)]  # all 12 thrillers watched
    return FakeServer(build_world(), entries)


async def build_profile(ac, server):
    with patch(GET_SERVER, AsyncMock(return_value=server)):
        started = await ac.post("/api/taste/rebuild", json={})
        assert started.status_code == 200
        for _ in range(100):
            status = (await ac.get("/api/taste/status")).json()
            if status["built"] and not status["running"]:
                return status
            await asyncio.sleep(0.05)
    raise AssertionError("rebuild did not finish")


@pytest.mark.asyncio
async def test_status_and_profile_before_any_build(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        status = (await ac.get("/api/taste/status")).json()
        assert status["built"] is False

        profile = await ac.get("/api/taste/profile")
        assert profile.status_code == 200  # expected state, not an error: the UI shows a call to action
        assert profile.json()["success"] is False
        assert profile.json()["error_code"] == "NOT_BUILT"


@pytest.mark.asyncio
async def test_rebuild_then_profile_and_temporal(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        status = await build_profile(ac, make_server())
        assert status["events"] == 12

        profile = (await ac.get("/api/taste/profile?kind=movie&top=5")).json()
        assert profile["success"] is True
        # director:mann ties with genre:thriller here (every fake thriller shares a director)
        assert "genre:thriller" in {r["dimension"] for r in profile["likes"]}
        assert any(d["dimension"] == "genre:comedy" for d in profile["dislikes"])

        prefixed = (await ac.get("/api/taste/profile?kind=movie&prefix=director")).json()
        assert all(r["dimension"].startswith("director:") for r in prefixed["likes"] + prefixed["dislikes"])

        # all 12 views fall in one bucket per their weekday/hour; asking for another returns an empty profile
        temporal = await ac.get("/api/taste/temporal/late_night?kind=movie")
        assert temporal.status_code == 200
        assert temporal.json()["success"] is True


@pytest.mark.asyncio
async def test_validation_errors_are_400(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        await build_profile(ac, make_server())
        assert (await ac.get("/api/taste/profile?kind=podcast")).status_code == 400
        assert (await ac.get("/api/taste/profile?bucket=teatime")).status_code == 400
        assert (await ac.get("/api/taste/recent-shifts?kind=nope")).status_code == 400


@pytest.mark.asyncio
async def test_score_and_rank(webapp_app):
    server = make_server()
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        await build_profile(ac, server)

        scored = (await ac.get("/api/taste/score/100")).json()  # a watched thriller: dimensions are cached
        assert scored["success"] is True
        assert scored["kind"] == "movie"
        assert scored["score"] > 0

        with patch(GET_SERVER, AsyncMock(return_value=server)):
            rank = (await ac.get("/api/taste/rank?library_id=0&limit=100&unwatched_only=false")).json()
        assert rank["success"] is True
        assert rank["kind"] == "movie"
        titles = [i["title"] for i in rank["items"]]
        assert titles[0].startswith("Thriller")  # thrillers outrank comedies
        assert titles[-1].startswith("Comedy")


@pytest.mark.asyncio
async def test_recent_shifts_endpoint(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        await build_profile(ac, make_server())
        body = (await ac.get("/api/taste/recent-shifts?kind=movie&days=30")).json()
        assert body["success"] is True
        assert isinstance(body["shifts"], list)


@pytest.mark.asyncio
async def test_second_rebuild_while_running_is_409(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        from webapp.backend.app.api import taste as taste_api

        taste_api._scheduled = True  # a rebuild has been accepted and has not finished
        response = await ac.post("/api/taste/rebuild", json={})
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_sync_requires_a_built_profile_then_picks_up_new_events(webapp_app):
    server = make_server()
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        not_built = (await ac.post("/api/taste/sync")).json()
        assert not_built["success"] is False
        assert not_built["error_code"] == "NOT_BUILT"

        await build_profile(ac, server)
        server.history_entries.append(hist(112, NOW - timedelta(days=1)))
        with patch(GET_SERVER, AsyncMock(return_value=server)):
            result = (await ac.post("/api/taste/sync")).json()
        assert result["success"] is True
        assert result["events_new"] == 1


@pytest.mark.asyncio
async def test_rebuild_failure_is_reported_in_status(webapp_app):
    async with AsyncClient(transport=ASGITransport(app=webapp_app), base_url="http://test") as ac:
        with patch(GET_SERVER, AsyncMock(side_effect=RuntimeError("PLEX_TOKEN is required"))):
            assert (await ac.post("/api/taste/rebuild", json={})).status_code == 200
            for _ in range(100):
                status = (await ac.get("/api/taste/status")).json()
                if not status["running"]:
                    break
                await asyncio.sleep(0.05)
        assert status["built"] is False
        assert status["progress"]["phase"] == "error"
        assert "PLEX_TOKEN" in status["progress"]["message"]

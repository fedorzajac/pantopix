"""test methods for launch data filter"""

import asyncio

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.routers import _filter_launches_router

fake_launches_raw = [
    {
        "id": "1",
        "name": "A",
        "date_utc": "2020-01-01T00:00:00Z",
        "date_unix": 0,
        "rocket": "r1",
        "launchpad": "p1",
        "success": True,
        "details": None,
        "links": {},
    },
    {
        "id": "2",
        "name": "B",
        "date_utc": "2021-01-01T00:00:00Z",
        "date_unix": 4,
        "rocket": "r2",
        "launchpad": "p2",
        "success": False,
        "details": None,
        "links": {},
    },
]


@pytest.mark.asyncio
async def test_filter_launches_date_range(monkeypatch):
    """filtering test"""

    async def fake_load_all_data():
        """method to provide fake data into get_data - returning fake request from url"""
        return {"launches": fake_launches_raw, "rockets": [], "launchpads": []}

    monkeypatch.setattr("app.libs.load_all_data", fake_load_all_data)
    app = FastAPI()

    app.include_router(_filter_launches_router())

    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/launches/filter?date_from=0&date_to=2")

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == "1"


@pytest.mark.asyncio
async def test_filter_launches_success(monkeypatch):
    """filtering test"""

    async def fake_load_all_data():
        """method to provide fake data into get_data - returning fake request from url"""
        return {"launches": fake_launches_raw, "rockets": [], "launchpads": []}

    monkeypatch.setattr("app.libs.load_all_data", fake_load_all_data)
    app = FastAPI()

    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()

    app.include_router(_filter_launches_router())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/launches/filter?success=true")

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == "1"

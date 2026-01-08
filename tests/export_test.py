"""Tests for data export functionality."""

import asyncio
import csv
import json
from io import StringIO

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.routers import _export_router

fake_launches_raw = [
    {
        "id": "1",
        "name": "Falcon 1 Flight 1",
        "date_utc": "2020-01-01T00:00:00Z",
        "date_unix": 1577836800,
        "rocket": "5e9d0d95eda69955f709d1eb",
        "launchpad": "5e9e4501f509094ba4566f84",
        "success": True,
        "details": "First successful launch",
        "links": {},
    },
    {
        "id": "2",
        "name": "Falcon 9 Flight 1",
        "date_utc": "2021-06-15T10:30:00Z",
        "date_unix": 1623754200,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "launchpad": "5e9e4502f509092b78566f87",
        "success": False,
        "details": None,
        "links": {},
    },
    {
        "id": "3",
        "name": "Starship Test",
        "date_utc": "2022-03-20T15:00:00Z",
        "date_unix": 1647788400,
        "rocket": "5e9d0d96eda699382d09d1ee",
        "launchpad": "5e9e4502f509094188566f88",
        "success": True,
        "details": "Test flight successful",
        "links": {},
    },
]


@pytest.fixture
def setup_app(monkeypatch):
    """Setup FastAPI app with mocked data."""

    async def fake_load_all_data():
        return {"launches": fake_launches_raw, "rockets": [], "launchpads": []}

    monkeypatch.setattr("app.libs.load_all_data", fake_load_all_data)

    app = FastAPI()
    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()

    app.include_router(_export_router())

    return app


@pytest.mark.asyncio
async def test_export_csv_all_launches(setup_app):
    """Test CSV export with all launches."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/csv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "launches.csv" in response.headers["content-disposition"]

    # Parse CSV content
    csv_content = response.text
    csv_reader = csv.DictReader(StringIO(csv_content))
    rows = list(csv_reader)

    assert len(rows) == 3
    assert rows[0]["id"] == "1"
    assert rows[0]["name"] == "Falcon 1 Flight 1"
    assert rows[0]["success"] == "True"
    assert rows[0]["details"] == "First successful launch"


@pytest.mark.asyncio
async def test_export_csv_filtered_by_success(setup_app):
    """Test CSV export with success filter."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/csv?success=true")

    assert response.status_code == 200

    csv_content = response.text
    csv_reader = csv.DictReader(StringIO(csv_content))
    rows = list(csv_reader)

    assert len(rows) == 2
    assert all(row["success"] == "True" for row in rows)


@pytest.mark.asyncio
async def test_export_csv_filtered_by_date_range(setup_app):
    """Test CSV export with date range filter."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Filter for launches in 2021
        response = await ac.get("/export/csv?date_from=1609459200&date_to=1640995199")

    assert response.status_code == 200

    csv_content = response.text
    csv_reader = csv.DictReader(StringIO(csv_content))
    rows = list(csv_reader)

    assert len(rows) == 1
    assert rows[0]["name"] == "Falcon 9 Flight 1"


@pytest.mark.asyncio
async def test_export_csv_with_none_details(setup_app):
    """Test CSV export handles None values correctly."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/csv?success=false")

    assert response.status_code == 200

    csv_content = response.text
    csv_reader = csv.DictReader(StringIO(csv_content))
    rows = list(csv_reader)

    assert len(rows) == 1
    assert rows[0]["details"] == ""  # None should be empty string


@pytest.mark.asyncio
async def test_export_json_all_launches(setup_app):
    """Test JSON export with all launches."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers["content-disposition"]
    assert "launches.json" in response.headers["content-disposition"]

    data = response.json()

    assert len(data) == 3
    assert data[0]["id"] == "1"
    assert data[0]["name"] == "Falcon 1 Flight 1"
    assert data[0]["success"] is True
    assert data[0]["details"] == "First successful launch"


@pytest.mark.asyncio
async def test_export_json_filtered_by_rocket(setup_app):
    """Test JSON export with rocket filter."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/json?rocket=5e9d0d95eda69973a809d1ec")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["rocket"] == "5e9d0d95eda69973a809d1ec"


@pytest.mark.asyncio
async def test_export_json_empty_result(setup_app):
    """Test JSON export with filter that returns no results."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/json?rocket=nonexistent")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0
    assert data == []


@pytest.mark.asyncio
async def test_export_json_structure(setup_app):
    """Test JSON export has correct structure."""

    transport = ASGITransport(app=setup_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/export/json")

    assert response.status_code == 200
    data = response.json()

    # Check we have data
    assert len(data) > 0

    # Check required fields exist in all launches
    required_fields = [
        "id",
        "name",
        "date_utc",
        "date_unix",
        "rocket",
        "launchpad",
        "success",
        "details",
        "links",
    ]

    for launch in data:
        for field in required_fields:
            assert (
                field in launch
            ), f"Field '{field}' missing in launch {launch.get('id', 'unknown')}"

    # Verify specific data from first launch
    first_launch = data[0]
    assert first_launch["id"] == "1"
    assert first_launch["name"] == "Falcon 1 Flight 1"
    assert first_launch["date_unix"] == 1577836800
    assert first_launch["rocket"] == "5e9d0d95eda69955f709d1eb"
    assert first_launch["launchpad"] == "5e9e4501f509094ba4566f84"
    assert first_launch["success"] is True
    assert first_launch["details"] == "First successful launch"
    assert isinstance(first_launch["links"], dict)

    # Verify data types are correct
    assert isinstance(first_launch["id"], str)
    assert isinstance(first_launch["name"], str)
    assert isinstance(first_launch["date_utc"], str)
    assert isinstance(first_launch["date_unix"], int)
    assert isinstance(first_launch["rocket"], str)
    assert isinstance(first_launch["launchpad"], str)
    assert isinstance(first_launch["success"], bool)
    assert isinstance(first_launch["links"], dict)

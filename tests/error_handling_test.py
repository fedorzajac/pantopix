import asyncio

import httpx
import pytest
import respx
from fastapi import FastAPI, Request

from app.libs import get_data, load_cached_data


@pytest.mark.asyncio
async def test_get_data_timeout():
    """Test timeout handling."""
    with respx.mock:
        respx.get("https://api.spacexdata.com/v4/launches").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        result = await get_data("launches")

    assert result is None


@pytest.mark.asyncio
async def test_get_data_http_error():
    """Test HTTP error handling."""
    with respx.mock:
        respx.get("https://api.spacexdata.com/v4/launches").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )
        result = await get_data("launches")

    assert result is None


@pytest.mark.asyncio
async def test_cache_with_invalid_data(monkeypatch):
    """Test handling of invalid data from API."""
    app = FastAPI()
    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()

    async def fake_load_all_data():
        return {"launches": [{"invalid": "data"}], "rockets": [], "launchpads": []}

    monkeypatch.setattr("app.libs.load_all_data", fake_load_all_data)
    request = Request({"type": "http", "app": app})

    with pytest.raises(Exception):  # Should handle validation errors
        await load_cached_data(request)

import asyncio
import json
import time
from pathlib import Path

import httpx
import pytest
import respx
from fastapi import FastAPI, Request

from app.libs import load_cached_data
from app.models import Launch


@pytest.mark.asyncio
async def test_load_cached_data_cache_miss():
    # Reset cache
    app = FastAPI()
    # app.state.settings = Settings()
    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()
    request = Request({"type": "http", "app": app})

    mock_json_launches = None
    with open(Path(__file__).parent / "mock" / "launches.json") as f:
        mock_json_launches = json.load(f)

    mock_json_rockets = None
    with open(Path(__file__).parent / "mock" / "rockets.json") as f:
        mock_json_rockets = json.load(f)

    mock_json_launchpads = None
    with open(Path(__file__).parent / "mock" / "launchpads.json") as f:
        mock_json_launchpads = json.load(f)

    # Mock HTTP request
    with respx.mock:
        respx.get("https://api.spacexdata.com/v4/launches").mock(
            return_value=httpx.Response(200, json=mock_json_launches)
        )
        respx.get("https://api.spacexdata.com/v4/rockets").mock(
            return_value=httpx.Response(200, json=mock_json_rockets)
        )
        respx.get("https://api.spacexdata.com/v4/launchpads").mock(
            return_value=httpx.Response(200, json=mock_json_launchpads)
        )

        cache = await load_cached_data(request)

    assert len(cache["launches"]) == 205
    assert len(cache["rockets"]) == 4
    assert len(cache["launchpads"]) == 6
    assert isinstance(cache["launches"][0], Launch)
    assert cache["launches"][0].id == "5eb87cd9ffd86e000604b32a"
    assert app.state.cache is not None
    assert app.state.cache_expires > time.time()


@pytest.mark.asyncio
async def test_load_cached_data_cache_hit():
    # Prepare fake cache
    # Reset cache
    app = FastAPI()
    # app.state.settings = Settings()
    app.state.cache = None
    app.state.cache_expires = 0
    app.state.cache_lock = asyncio.Lock()
    request = Request({"type": "http", "app": app})
    app.state.cache = [
        Launch(
            id="cached",
            name="Cached Launch",
            date_utc="2020-01-01T00:00:00Z",
            date_unix=1,
            rocket="rocket",
            launchpad="pad",
            success=True,
            details=None,
            links={},
        )
    ]
    app.state.cache_expires = time.time() + 600

    with respx.mock:
        respx.get("https://api.spacexdata.com/v4/launches").mock(
            return_value=httpx.Response(500)
        )
        respx.get("https://api.spacexdata.com/v4/rockets").mock(
            return_value=httpx.Response(500)
        )
        respx.get("https://api.spacexdata.com/v4/launchpads").mock(
            return_value=httpx.Response(500)
        )

        launches = await load_cached_data(request)

    assert len(launches) == 1
    assert launches[0].id == "cached"

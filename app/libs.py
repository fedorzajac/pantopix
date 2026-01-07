"""spacex app main methods"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

import httpx
from fastapi import Request

from app.models import Launch, Launchpad, Rocket

BASE_URL = "https://api.spacexdata.com/v4"
CACHE_DATA = None
CACHE_EXPIRES = 0
CACHE_TTL = 600
CACHE_LOCK = asyncio.Lock()


async def get_data(endpoint: str) -> Optional[List]:
    """Fetch JSON from SpaceX API and convert each item to a dataclass."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{BASE_URL}/{endpoint}")
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        logging.error(f"Timeout fetching {endpoint}")
        return None
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error {e.response.status_code} for {endpoint}")
        return None
    except httpx.RequestError as e:
        logging.error(f"Network error fetching {endpoint}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching {endpoint}: {e}")
        return None


async def load_all_data():
    """temp function"""
    all_data = {
        "launches": await get_data("launches"),
        "rockets": await get_data("rockets"),
        "launchpads": await get_data("launchpads"),
    }
    return all_data


async def load_cached_data(request: Request) -> Dict:
    try:
        """chack cached data, reloads and validate"""

        if (
            request.app.state.cache is not None
            and time.time() < request.app.state.cache_expires
        ):
            logging.info("serving data from cache")
            return request.app.state.cache

        async with request.app.state.cache_lock:
            raw = await load_all_data()

            # using cached data if api fails
            if raw is None:
                if request.app.state.cache is not None:
                    logging.warning("API failed, serving stale cache")
                    # Extend cache expiry slightly
                    request.app.state.cache_expires = time.time() + 60
                    return request.app.state.cache
                else:
                    # No cache at all, raise error
                    raise HTTPException(
                        status_code=503,
                        detail="Unable to fetch data from SpaceX API and no cache available",
                    )
            # same principle for validation
            try:
                validated_launches = [
                    Launch.model_validate(item) for item in raw["launches"]
                ]
                validated_rockets = [
                    Rocket.model_validate(item) for item in raw["rockets"]
                ]
                validated_launchpads = [
                    Launchpad.model_validate(item) for item in raw["launchpads"]
                ]
            except Exception as e:
                logging.error(f"Data validation failed: {e}")
                if request.app.state.cache is not None:
                    logging.warning("Using stale cache due to validation error")
                    return request.app.state.cache
                raise HTTPException(status_code=500, detail="Data validation failed")

            validated = {
                "launches": validated_launches,
                "rockets": validated_rockets,
                "launchpads": validated_launchpads,
            }
            # validated = [Launch.model_validate(item) for item in raw]
            request.app.state.cache = validated
            request.app.state.cache_expires = time.time() + 600
            return validated
    except Exception as e:
        logging.error(f"load cached data failed: {e}")
        raise

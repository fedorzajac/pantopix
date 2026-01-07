"""methids used in router"""

from typing import Optional

from fastapi import Request

from app.libs import load_cached_data


async def healthcheck(request: Request):
    """application health check"""
    return {
        "status": "ok",
    }


async def rockets(request: Request):
    data = await load_cached_data(request)
    return data["rockets"]


async def launchpads(request: Request):
    data = await load_cached_data(request)
    return data["launchpads"]


async def filter_launches(
    request: Request,
    date_from: Optional[int] = None,
    date_to: Optional[int] = None,
    success: Optional[str] = None,
    rocket: Optional[str] = None,
    launchpad: Optional[str] = None,
):
    """main filter logic"""
    cache = await load_cached_data(request)
    result = cache["launches"]

    # date range
    if date_from is not None and date_to is not None:
        result = [t for t in result if date_from <= int(t.date_unix) <= date_to]

    # Success filter
    if success is not None:
        if success.lower() == "true":
            result = [launch for launch in result if launch.success is True]
        elif success.lower() == "false":
            result = [launch for launch in result if launch.success is False]

    # rocket filter
    if rocket:
        result = [t for t in result if t.rocket == rocket]

    # launchpad filter
    if launchpad:
        result = [t for t in result if t.launchpad == launchpad]

    return result

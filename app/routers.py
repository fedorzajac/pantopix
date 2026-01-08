"""FastAPI router setup"""

from typing import Dict, List

from fastapi import APIRouter, Depends, FastAPI, Request, status

from app.analytics import analytics
from app.export import export_to_csv, export_to_json
from app.methods import filter_launches, healthcheck, launchpads, rockets
from app.models import FilterQuery, Launch, Launchpad, Rocket

API_PREFIX = ""


def _health_checks_router() -> APIRouter:
    """Create and return the health check router."""
    router = APIRouter(prefix="/health", tags=["health"])

    @router.get(
        "",
        name="healthcheck",
        summary="Health check",
        description="Returns the application health status.",
        status_code=status.HTTP_200_OK,
    )
    async def health_endpoint(request: Request) -> dict[str, str]:
        return await healthcheck(request)

    return router


def _filter_launches_router() -> APIRouter:
    """endpoint for queriing the data"""

    router = APIRouter(prefix="/launches/filter", tags=["launches"])

    @router.get(
        "",
        name="launches",
        summary="Launches Endpoint",
        status_code=status.HTTP_200_OK,
    )
    async def launches_endpoint(
        request: Request, q: FilterQuery = Depends()
    ) -> List[Launch]:
        return await filter_launches(request, **q.model_dump())

    return router


def _select_rocket_router() -> APIRouter:
    """rocket select dropdown"""
    router = APIRouter(prefix="/select/rocket", tags=["rockets"])

    @router.get(
        "",
        name="rocket",
        summary="data for rocket select dropdown",
        status_code=status.HTTP_200_OK,
    )
    async def select_rocket_endpoint(request: Request) -> List[Rocket]:
        return await rockets(request)

    return router


def _select_launchpad_router() -> APIRouter:
    """rocket select dropdown"""
    router = APIRouter(prefix="/select/launchpad", tags=["launchpad"])

    @router.get(
        "",
        name="launchpad",
        summary="data for launchpad select dropdown",
        status_code=status.HTTP_200_OK,
    )
    async def select_launchpad_endpoint(request: Request) -> List[Launchpad]:
        return await launchpads(request)

    return router


def _stats_router() -> APIRouter:
    """analytics"""
    router = APIRouter(prefix="/stats/data", tags=["data"])

    @router.get(
        "",
        name="analytics",
        summary="analytics data",
        status_code=status.HTTP_200_OK,
    )
    async def analytics_endpoint(request: Request) -> Dict:
        return await analytics(request)

    return router


def _export_router() -> APIRouter:
    """Export endpoints."""
    router = APIRouter(prefix="/export", tags=["export"])

    @router.get(
        "/csv",
        name="export_csv",
        summary="Export launches to CSV",
    )
    async def export_csv_endpoint(request: Request, q: FilterQuery = Depends()):
        launches = await filter_launches(request, **q.model_dump())
        return export_to_csv(launches)

    @router.get(
        "/json",
        name="export_json",
        summary="Export launches to JSON",
    )
    async def export_json_endpoint(request: Request, q: FilterQuery = Depends()):
        launches = await filter_launches(request, **q.model_dump())
        return export_to_json(launches)

    return router


def register_routers(app: FastAPI) -> None:
    """Register all routers on the FastAPI application."""
    routers = [
        _health_checks_router(),
        _filter_launches_router(),
        _select_rocket_router(),
        _select_launchpad_router(),
        _stats_router(),
        _export_router(),
    ]
    for router in routers:
        app.include_router(router, prefix=API_PREFIX)

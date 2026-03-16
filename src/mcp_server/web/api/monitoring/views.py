"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import UJSONResponse

from mcp_server.settings import provider_settings_manager

router = APIRouter(tags=["monitoring"])


@router.get("/health")
async def health_check() -> UJSONResponse:
    return UJSONResponse({"status": "ok", "provider": "webscrape"})


@router.get("/readiness")
async def readiness_check() -> UJSONResponse:
    ps = provider_settings_manager.current
    return UJSONResponse(
        {
            "status": "ok",
            "provider": "webscrape",
            "request_timeout": ps.request_timeout,
        },
    )

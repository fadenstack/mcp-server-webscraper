"""Settings REST API — schema/get/update for provider settings."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import UJSONResponse
from pydantic import ValidationError

from mcp_server.settings import provider_settings_manager

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/schema")
async def get_settings_schema() -> UJSONResponse:
    return UJSONResponse(provider_settings_manager.get_schema())


@router.get("")
async def get_settings() -> UJSONResponse:
    return UJSONResponse(provider_settings_manager.get_values())


@router.put("")
async def update_settings(body: dict[str, Any]) -> UJSONResponse:
    try:
        provider_settings_manager.update(body)
    except ValidationError as exc:
        return UJSONResponse(
            {"error": "validation_error", "detail": exc.errors()},
            status_code=422,
        )
    return UJSONResponse(provider_settings_manager.get_values())

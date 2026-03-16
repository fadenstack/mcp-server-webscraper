"""FastAPI application factory."""

from __future__ import annotations

from importlib import metadata

from fastapi import FastAPI

from mcp_server.log import configure_logging
from mcp_server.mcp.transport import mount_mcp_transport
from mcp_server.web.api.router import api_router
from mcp_server.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="MCP Server — Webscrape",
        version=metadata.version("mcp-server-webscrape"),
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.include_router(api_router, prefix="/api")
    mount_mcp_transport(app)

    return app

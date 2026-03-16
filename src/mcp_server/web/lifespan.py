"""Application lifespan hooks."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import anyio
import httpx
from fastapi import FastAPI
from loguru import logger

from mcp_server.mcp import transport as transport_mod
from mcp_server.mcp.server import mcp_server
from mcp_server.settings import provider_settings_manager, settings


@asynccontextmanager
async def lifespan_setup(app: FastAPI) -> AsyncGenerator[None, None]:
    ps = provider_settings_manager.current
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(ps.request_timeout, connect=6.0),
    )
    logger.info(
        "MCP Webscrape server starting on {}:{} (env={})",
        settings.host,
        settings.port,
        settings.environment,
    )

    transport = transport_mod.mcp_transport
    if transport is None:
        raise RuntimeError("mount_mcp_transport() must be called before lifespan")

    init_options = mcp_server.create_initialization_options()

    async with anyio.create_task_group() as tg:

        async def _run_mcp(*, task_status: anyio.abc.TaskStatus = anyio.TASK_STATUS_IGNORED) -> None:
            async with transport.connect() as (read_stream, write_stream):
                task_status.started()
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    init_options,
                    raise_exceptions=False,
                )

        await tg.start(_run_mcp)
        logger.info("MCP transport connected at /mcp (stateless mode)")

        yield

        await transport.terminate()
        tg.cancel_scope.cancel()

    await app.state.http_client.aclose()
    logger.info("MCP Webscrape server stopped")

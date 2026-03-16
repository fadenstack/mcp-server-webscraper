"""Mount MCP Streamable-HTTP transport at /mcp."""

from __future__ import annotations

from fastapi import FastAPI
from loguru import logger
from mcp.server.streamable_http import StreamableHTTPServerTransport
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from mcp_server.mcp.server import mcp_server, register_provider
from mcp_server.providers.webscrape.provider import WebScrapeProvider
from mcp_server.settings import settings

mcp_transport: StreamableHTTPServerTransport | None = None


class _MCPAsgiApp:
    def __init__(self, transport: StreamableHTTPServerTransport) -> None:
        self._transport = transport

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return
        request = Request(scope, receive)
        if not _check_auth(request):
            response = Response(content="Unauthorized", status_code=401)
            await response(scope, receive, send)
            return
        try:
            await self._transport.handle_request(scope, receive, send)
        except Exception:
            logger.exception("MCP transport error")
            raise


def _check_auth(request: Request) -> bool:
    if not settings.auth_enabled:
        return True
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:] == settings.auth_token
    return False


def mount_mcp_transport(app: FastAPI) -> None:
    global mcp_transport

    provider = WebScrapeProvider()
    register_provider(provider)
    logger.info(
        "Registered provider '{}' with {} tool(s)",
        provider.provider_name,
        len(provider.list_tools()),
    )

    mcp_transport = StreamableHTTPServerTransport(mcp_session_id=None)
    app.mount("/mcp", _MCPAsgiApp(mcp_transport))

"""Webscrape provider — exposes scrape_url tool."""

from __future__ import annotations

from mcp.types import Tool

from mcp_server.providers.base import ToolProvider
from mcp_server.providers.webscrape.client import WebScrapeClient

_SCRAPE_URL_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "Target page URL",
        },
        "max_output_chars": {
            "type": "integer",
            "description": "Max chars in returned extraction",
            "minimum": 1000,
            "maximum": 200000,
        },
        "output_format": {
            "type": "string",
            "description": "Output format",
            "enum": ["txt", "markdown"],
            "default": "txt",
        },
        "include_links": {
            "type": "boolean",
            "description": "Include links in extracted output",
        },
        "include_tables": {
            "type": "boolean",
            "description": "Include table content",
        },
        "include_comments": {
            "type": "boolean",
            "description": "Include comments",
        },
        "include_images": {
            "type": "boolean",
            "description": "Include image references",
        },
    },
    "required": ["url"],
}


class WebScrapeProvider(ToolProvider):
    def __init__(self) -> None:
        self._client = WebScrapeClient()

    @property
    def provider_name(self) -> str:
        return "webscrape"

    def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="scrape_url",
                description=(
                    "Fetch and extract the main textual content from a webpage using Trafilatura. "
                    "Returns cleaned, boilerplate-reduced content suitable for LLM usage."
                ),
                inputSchema=_SCRAPE_URL_SCHEMA,
            ),
        ]

    async def call_tool(self, name: str, arguments: dict) -> str:
        if name != "scrape_url":
            raise ValueError(f"Unknown tool: {name}")

        return await self._client.scrape_url(
            url=arguments["url"],
            max_output_chars=arguments.get("max_output_chars"),
            output_format=arguments.get("output_format"),
            include_links=arguments.get("include_links"),
            include_tables=arguments.get("include_tables"),
            include_comments=arguments.get("include_comments"),
            include_images=arguments.get("include_images"),
        )

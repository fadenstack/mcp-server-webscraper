"""Web scraping client: fetch URL + extract main content with Trafilatura."""

from __future__ import annotations

import re

import httpx
import trafilatura

from mcp_server.settings import provider_settings_manager


class WebScrapeClient:
    def _normalise_format(self, output_format: str | None) -> str:
        fmt = (output_format or provider_settings_manager.current.default_output_format).lower()
        return "markdown" if fmt == "markdown" else "txt"

    async def scrape_url(
        self,
        *,
        url: str,
        max_output_chars: int | None = None,
        output_format: str | None = None,
        include_links: bool | None = None,
        include_tables: bool | None = None,
        include_comments: bool | None = None,
        include_images: bool | None = None,
    ) -> str:
        ps = provider_settings_manager.current
        timeout = httpx.Timeout(ps.request_timeout, connect=6.0)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"User-Agent": ps.user_agent},
            )

        response.raise_for_status()
        content_type = response.headers.get("content-type", "")

        fmt = self._normalise_format(output_format)
        extracted = trafilatura.extract(
            response.text,
            output_format=fmt,
            include_links=ps.include_links if include_links is None else include_links,
            include_tables=ps.include_tables if include_tables is None else include_tables,
            include_comments=ps.include_comments if include_comments is None else include_comments,
            include_images=ps.include_images if include_images is None else include_images,
            favor_precision=True,
            deduplicate=True,
        )

        if not extracted:
            if "application/json" in content_type or content_type.startswith("text/plain"):
                extracted = response.text
            else:
                raise RuntimeError("Failed to extract main content from URL.")

        cleaned = re.sub(r"\n{3,}", "\n\n", extracted).strip()
        cap = max_output_chars or ps.default_max_output_chars

        if len(cleaned) > cap:
            cleaned = cleaned[:cap].rstrip() + "\n\n[truncated]"

        return cleaned

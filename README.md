# MCP Server — Webscrape

Standalone MCP server for webpage extraction using [Trafilatura](https://trafilatura.readthedocs.io/).
Designed for **LLM token reduction by content quality**, i.e. boilerplate removal + compact text output.

## Why this server

- Keeps only core article/page content (drops nav/footer clutter)
- Produces compact LLM-ready text or markdown
- Supports runtime settings via `/api/settings`
- Uses Streamable HTTP MCP transport (`/mcp/`)

## Tool

| Tool         | Description                                                      |
| ------------ | ---------------------------------------------------------------- |
| `scrape_url` | Fetches a URL and extracts main textual content with Trafilatura |

## Quick Start

### Docker

```bash
docker compose up -d --build
curl http://localhost:8102/api/health
```

### Local

```bash
uv sync
uv run python -m mcp_server
```

## Configuration

Environment variables use prefix `MCP_WEBSCRAPE_`:

| Variable                                 | Default                      | Description                            |
| ---------------------------------------- | ---------------------------- | -------------------------------------- |
| `MCP_WEBSCRAPE_HOST`                     | `0.0.0.0`                    | Bind host                              |
| `MCP_WEBSCRAPE_PORT`                     | `8102`                       | Bind port                              |
| `MCP_WEBSCRAPE_REQUEST_TIMEOUT`          | `20`                         | Fetch timeout (seconds)                |
| `MCP_WEBSCRAPE_USER_AGENT`               | `Fadenstack-Webscrape-MCP/1.0` | HTTP User-Agent                        |
| `MCP_WEBSCRAPE_DEFAULT_MAX_OUTPUT_CHARS` | `12000`                      | Default output cap                     |
| `MCP_WEBSCRAPE_AUTH_TOKEN`               | _(empty)_                    | Optional bearer token for MCP endpoint |

## Fadenstack Registration

| Field       | Value                     |
| ----------- | ------------------------- |
| Name        | `webscrape`               |
| Transport   | `Streamable HTTP`         |
| URL         | `http://<host>:8102/mcp/` |
| Tool Prefix | `webscrape`               |

## License

Apache-2.0

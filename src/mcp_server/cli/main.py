"""Dedicated CLI for the Webscrape MCP server."""

from __future__ import annotations

import json
import subprocess

import click

from mcp_server.settings import provider_settings_manager, settings


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.version_option(package_name="mcp-server-webscrape")
@click.pass_context
def cli(ctx: click.Context, *, verbose: bool) -> None:
    """mcp-webscrape — standalone MCP server for webpage extraction."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--host", default=None, help="Bind host (overrides MCP_WEBSCRAPE_HOST).")
@click.option("--port", default=None, type=int, help="Bind port (overrides MCP_WEBSCRAPE_PORT).")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development.")
def run(host: str | None, port: int | None, *, reload: bool) -> None:
    import uvicorn

    uvicorn.run(
        "mcp_server.web.application:get_app",
        host=host or settings.host,
        port=port or settings.port,
        workers=settings.workers_count,
        reload=reload or settings.reload,
        factory=True,
    )


@cli.command()
def doctor() -> None:
    """Validate configuration and basic fetch path."""
    import httpx

    errors: list[str] = []

    click.echo("Checking configuration...\n")
    ps = provider_settings_manager.current
    click.echo(f"  Timeout: {ps.request_timeout}s")
    click.echo(f"  User-Agent: {ps.user_agent}")
    click.echo(f"  Default output cap: {ps.default_max_output_chars}")

    click.echo("\nTesting outbound HTTP reachability...")
    try:
        resp = httpx.get("https://example.com", timeout=10, headers={"User-Agent": ps.user_agent})
        if resp.status_code >= 500:
            errors.append(f"Probe URL returned HTTP {resp.status_code}")
        else:
            click.echo("  [OK] outbound HTTP reachable")
    except Exception as exc:
        errors.append(str(exc))

    if errors:
        for e in errors:
            click.echo(click.style(f"  [FAIL] {e}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\nAll checks passed.", fg="green"))


@cli.command()
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output.")
def manifest(*, pretty: bool) -> None:
    from mcp_server.providers.webscrape.provider import WebScrapeProvider

    provider = WebScrapeProvider()
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "inputSchema": t.inputSchema,
        }
        for t in provider.list_tools()
    ]

    output = {
        "server_name": "webscrape",
        "provider": provider.provider_name,
        "transport": "streamable-http",
        "endpoint": f"http://{settings.host}:{settings.port}/mcp",
        "tools": tools,
    }
    indent = 2 if pretty else None
    click.echo(json.dumps(output, indent=indent))


@cli.command("docker-up")
@click.option("--build", is_flag=True, help="Rebuild the image before starting.")
def docker_up(*, build: bool) -> None:
    cmd = ["docker", "compose", "up"]
    if build:
        cmd.append("--build")
    cmd.append("-d")
    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


@cli.command("docker-down")
def docker_down() -> None:
    cmd = ["docker", "compose", "down"]
    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    cli()

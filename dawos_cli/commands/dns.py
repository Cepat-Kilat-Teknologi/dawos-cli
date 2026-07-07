"""DNS forwarding — status, config, flush cache."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="DNS forwarding management.")


@app.command("status")
def status() -> None:
    """Show DNS forwarding status and stats."""
    data = client.get("/api/v1/dns/forwarding/status")
    output.response(data, title="DNS Forwarding Status")


@app.command("config")
def config_show() -> None:
    """Show DNS forwarding configuration."""
    data = client.get("/api/v1/dns/forwarding/config")
    output.response(data, title="DNS Forwarding Config")


@app.command("config-set")
def config_set(
    servers: str = typer.Option(
        None, "--servers", "-s", help="Comma-separated upstream nameservers"
    ),
    cache_size: int = typer.Option(
        None, "--cache-size", help="DNS cache size (0=disable, max 100000)"
    ),
) -> None:
    """Update DNS forwarding configuration."""
    payload: dict = {}
    if servers is not None:
        payload["servers"] = [s.strip() for s in servers.split(",")]
    if cache_size is not None:
        payload["cache_size"] = cache_size
    if not payload:
        output.warning("No settings specified. Use --servers or --cache-size.")
        raise typer.Exit(1)
    client.put("/api/v1/dns/forwarding/config", json=payload)
    output.success("DNS forwarding config updated")


@app.command("flush")
def flush() -> None:
    """Flush the DNS cache."""
    client.post("/api/v1/dns/forwarding/flush")
    output.success("DNS cache flushed")

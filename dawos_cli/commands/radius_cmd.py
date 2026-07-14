"""RADIUS diagnostics — config, status, server check."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="RADIUS server diagnostics.")


@app.command("config")
def radius_config() -> None:
    """Show RADIUS configuration from accel-ppp.conf.

    Returns server addresses, ports, NAS identity, and timeout
    settings. Shared secrets are never exposed.
    """
    data = client.get("/api/v1/radius/config")
    output.response(data, title="RADIUS Config")


@app.command("status")
def radius_status() -> None:
    """Show live RADIUS server statistics.

    Returns per-server metrics including authentication, accounting,
    and interim counters with sent/lost/latency breakdowns.
    """
    data = client.get("/api/v1/radius/status")
    output.response(data, title="RADIUS Status")


@app.command("check")
def radius_check() -> None:
    """Run a RADIUS server diagnostic check.

    For every configured RADIUS server: tests TCP reachability
    and queries accel-ppp for runtime state. The healthy flag is
    True only when all servers are reachable and active.
    """
    data = client.get("/api/v1/radius/check")
    if isinstance(data, dict):
        healthy = data.get("healthy")
        if healthy is True:
            output.success("All RADIUS servers are healthy")
        elif healthy is False:
            output.error("One or more RADIUS servers are unhealthy")
    output.response(data, title="RADIUS Check")

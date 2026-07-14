"""System and health commands — system info, health check."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="System information and health.")


@app.command("info")
def info() -> None:
    """Show system information (OS, CPU, memory, disk)."""
    data = client.get("/api/v1/system/info")
    output.response(data, title="System Info")


@app.command("health")
def health() -> None:
    """Show agent health status."""
    data = client.get("/health")
    output.response(data, title="Health")


@app.command("metrics")
def metrics() -> None:
    """Show system metrics (CPU, memory, disk, load, network)."""
    data = client.get("/api/v1/system/metrics")
    output.response(data, title="System Metrics")


@app.command("ready")
def ready() -> None:
    """Check accel-ppp readiness (load balancer probe)."""
    data = client.get("/health/ready")
    output.response(data, title="Readiness")


@app.command("stats-extended")
def stats_extended() -> None:
    """Show comprehensive accel-ppp runtime statistics.

    Includes uptime, CPU, memory, core counters, session counts,
    PPPoE protocol counters, and per-RADIUS-server statistics.
    """
    data = client.get("/api/v1/system/stats")
    output.response(data, title="Extended Statistics")

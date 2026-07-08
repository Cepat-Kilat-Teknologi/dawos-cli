"""Monitoring — status, metrics, configure, restart services."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Monitoring and metrics management.")


@app.command("status")
def status() -> None:
    """Show monitoring stack status."""
    data = client.get("/api/v1/monitoring/status")
    output.response(data, title="Monitoring Status")


@app.command("metrics")
def metrics(
    service: str = typer.Argument(..., help="Service name (e.g. accel-ppp, frr, dhcp)"),
) -> None:
    """Show metrics for a specific monitoring service."""
    data = client.get(f"/api/v1/monitoring/metrics/{service}")
    output.response(data, title=f"Metrics: {service}")


@app.command("metrics-service")
def metrics_service(
    service: str = typer.Argument(..., help="Service name (e.g. accel-ppp, frr, dhcp)"),
) -> None:
    """Show metrics for a specific service (alias for 'metrics')."""
    data = client.get(f"/api/v1/monitoring/metrics/{service}")
    output.response(data, title=f"Metrics: {service}")


@app.command("configure")
def configure(
    service: str = typer.Option(..., "--service", "-s", help="Exporter service name"),
    enable: bool = typer.Option(True, "--enable/--disable", help="Enable or disable"),
) -> None:
    """Enable or disable a monitoring exporter."""
    client.post(
        "/api/v1/monitoring/configure",
        json={"service": service, "enable": enable},
    )
    state = "enabled" if enable else "disabled"
    output.success(f"Monitoring exporter '{service}' {state}")


@app.command("restart")
def restart(
    service: str = typer.Argument(..., help="Service to restart"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart a monitoring service."""
    if not force:
        typer.confirm(f"Restart monitoring service '{service}'?", abort=True)
    client.post(f"/api/v1/monitoring/restart/{service}")
    output.success(f"Monitoring service '{service}' restarted")

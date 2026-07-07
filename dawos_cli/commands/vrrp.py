"""VRRP — virtual router redundancy protocol management."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="VRRP high-availability management.")


@app.command("status")
def status() -> None:
    """Show VRRP status overview."""
    data = client.get("/api/v1/vrrp/status")
    output.response(data, title="VRRP Status")


@app.command("group")
def group(
    group_id: str = typer.Argument(..., help="VRRP group name or ID"),
) -> None:
    """Show detail for a specific VRRP group."""
    data = client.get(f"/api/v1/vrrp/groups/{group_id}")
    output.response(data, title=f"VRRP Group: {group_id}")


@app.command("failover")
def failover(
    group_id: str = typer.Argument(..., help="VRRP group to failover"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Trigger a VRRP failover (switch to backup)."""
    if not force:
        typer.confirm(f"Trigger failover for VRRP group '{group_id}'?", abort=True)
    client.post("/api/v1/vrrp/failover", json={"group": group_id})
    output.success(f"VRRP failover triggered for '{group_id}'")


@app.command("restart")
def restart(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart the VRRP daemon."""
    if not force:
        typer.confirm("Restart VRRP daemon?", abort=True)
    client.post("/api/v1/vrrp/restart")
    output.success("VRRP daemon restarted")

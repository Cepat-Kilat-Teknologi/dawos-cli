"""LLDP — link-layer discovery protocol status and neighbors."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="LLDP link-layer discovery.")


@app.command("status")
def status() -> None:
    """Show LLDP daemon status."""
    data = client.get("/api/v1/lldp/status")
    output.response(data, title="LLDP Status")


@app.command("neighbors")
def neighbors() -> None:
    """List all LLDP neighbors."""
    data = client.get("/api/v1/lldp/neighbors")
    nbrs = data.get("neighbors", data) if isinstance(data, dict) else data
    if isinstance(nbrs, list):
        output.table(
            nbrs,
            [
                "local_port",
                "chassis_id",
                "system_name",
                "port_id",
                "management_address",
                "ttl",
            ],
            title="LLDP Neighbors",
            col_styles={"local_port": "bold", "system_name": "cyan"},
        )
    else:
        output.response(data)


@app.command("neighbor")
def neighbor(
    interface: str = typer.Argument(..., help="Interface name (e.g. eth0)"),
) -> None:
    """Show LLDP neighbor detail for a specific interface."""
    data = client.get(f"/api/v1/lldp/neighbors/{interface}")
    output.response(data, title=f"LLDP Neighbor: {interface}")

"""Zone-based firewall — list, create, delete zones."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Zone-based firewall management.")


@app.command("list")
def list_zones() -> None:
    """List all firewall zones."""
    data = client.get("/api/v1/zones")
    zones = output.unwrap(data, "zones")
    if isinstance(zones, list):
        output.table(
            zones,
            ["name", "interfaces", "default_action", "rules_count"],
            title="Firewall Zones",
            col_styles={"name": "bold"},
        )
    else:
        output.response(data)


@app.command("show")
def show(
    zone: str = typer.Argument(..., help="Zone name"),
) -> None:
    """Show detail for a specific zone."""
    data = client.get(f"/api/v1/zones/{zone}")
    output.response(data, title=f"Zone: {zone}")


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Zone name"),
    default_action: str = typer.Option(
        "drop", "--default-action", "-d", help="Default action (accept/drop/reject)"
    ),
) -> None:
    """Create a firewall zone."""
    client.post("/api/v1/zones", json={"name": name, "default_action": default_action})
    output.success(f"Zone '{name}' created (default: {default_action})")


@app.command("remove")
def remove(
    zone: str = typer.Argument(..., help="Zone name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a firewall zone."""
    if not force:
        typer.confirm(f"Delete zone '{zone}'?", abort=True)
    client.delete(f"/api/v1/zones/{zone}")
    output.success(f"Zone '{zone}' deleted")

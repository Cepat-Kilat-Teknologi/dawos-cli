"""IP pool management — list pools, usage, add/remove."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="IP address pool management.")


@app.command("list")
def list_pools() -> None:
    """List all configured IP pools."""
    data = client.get("/api/v1/ip-pool")
    pools = data.get("pools", data) if isinstance(data, dict) else data
    if isinstance(pools, list):
        output.table(
            pools,
            ["name", "subnet", "used", "available", "total"],
            title="IP Pools",
            col_styles={"name": "bold", "subnet": "cyan"},
        )
    else:
        output.response(data)


@app.command("usage")
def usage() -> None:
    """Show IP pool usage summary."""
    data = client.get("/api/v1/ip-pool/usage")
    output.response(data, title="Pool Usage")


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Pool name"),
    ip_range: str = typer.Argument(..., help="IP range CIDR (e.g. 10.0.0.0/24)"),
) -> None:
    """Add an IP pool."""
    client.post("/api/v1/ip-pool", json={"name": name, "ip_range": ip_range})
    output.success(f"Pool '{name}' added: {ip_range}")


@app.command("remove")
def remove(
    name: str = typer.Argument(..., help="Pool name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove an IP pool."""
    if not force:
        typer.confirm(f"Remove pool '{name}'?", abort=True)
    client.delete(f"/api/v1/ip-pool/{name}")
    output.success(f"Pool '{name}' removed")

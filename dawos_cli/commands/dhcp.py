"""DHCP — server status, leases, relay, restart."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="DHCP server and relay management.")


@app.command("status")
def status() -> None:
    """Show DHCP server status."""
    data = client.get("/api/v1/dhcp/status")
    output.response(data, title="DHCP Status")


@app.command("leases")
def leases() -> None:
    """List active DHCP leases."""
    data = client.get("/api/v1/dhcp/leases")
    lease_list = data.get("leases", data) if isinstance(data, dict) else data
    if isinstance(lease_list, list):
        output.table(
            lease_list,
            ["ip", "mac", "hostname", "expires", "interface"],
            title="DHCP Leases",
            col_styles={"ip": "cyan", "mac": "bold"},
        )
    else:
        output.response(data)


@app.command("relay")
def relay() -> None:
    """Show DHCP relay status."""
    data = client.get("/api/v1/dhcp/relay/status")
    output.response(data, title="DHCP Relay Status")


@app.command("restart")
def restart(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart the DHCP server."""
    if not force:
        typer.confirm("Restart DHCP server?", abort=True)
    client.post("/api/v1/dhcp/restart")
    output.success("DHCP server restarted")


@app.command("relay-restart")
def relay_restart(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart the DHCP relay agent."""
    if not force:
        typer.confirm("Restart DHCP relay?", abort=True)
    client.post("/api/v1/dhcp/relay/restart")
    output.success("DHCP relay restarted")

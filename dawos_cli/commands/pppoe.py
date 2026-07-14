"""PPPoE management — listeners, MAC filter, PADO delay."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="PPPoE listeners, MAC filter, PADO delay.")


@app.command("interfaces")
def interfaces() -> None:
    """List PPPoE listener interfaces."""
    data = client.get("/api/v1/pppoe/interfaces")
    ifaces = output.unwrap(data, "interfaces")
    if isinstance(ifaces, list):
        output.table(ifaces, ["name", "status", "sessions"], title="PPPoE Interfaces")
    else:
        output.response(data)


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Interface name to add as PPPoE listener"),
) -> None:
    """Add a PPPoE listener interface."""
    client.post("/api/v1/pppoe/interfaces", json={"interface": name})
    output.success(f"PPPoE listener added on {name}")


@app.command("remove")
def remove(
    name: str = typer.Argument(..., help="Interface name to remove"),
) -> None:
    """Remove a PPPoE listener interface."""
    client.delete(f"/api/v1/pppoe/interfaces/{name}")
    output.success(f"PPPoE listener removed from {name}")


# --- MAC Filter ------------------------------------------------------------


@app.command("mac-filter")
def mac_filter() -> None:
    """List MAC filter entries."""
    data = client.get("/api/v1/pppoe/mac-filter")
    entries = output.unwrap(data, "entries")
    if isinstance(entries, list):
        output.table(entries, ["mac", "action"], title="MAC Filter")
    else:
        output.response(data)


@app.command("mac-add")
def mac_add(
    mac: str = typer.Argument(..., help="MAC address to add (e.g. AA:BB:CC:DD:EE:FF)"),
) -> None:
    """Add a MAC address to the filter."""
    client.post("/api/v1/pppoe/mac-filter", json={"mac": mac})
    output.success(f"MAC {mac} added to filter")


@app.command("mac-del")
def mac_del(
    mac: str = typer.Argument(..., help="MAC address to remove"),
) -> None:
    """Remove a MAC address from the filter."""
    client.delete(f"/api/v1/pppoe/mac-filter/{mac}")
    output.success(f"MAC {mac} removed from filter")


# --- PADO Delay ------------------------------------------------------------


@app.command("pado")
def pado() -> None:
    """Show PADO delay configuration."""
    data = client.get("/api/v1/pppoe/pado")
    output.response(data, title="PADO Delay")


@app.command("pado-set")
def pado_set(
    delay: int = typer.Argument(..., help="PADO delay in milliseconds"),
) -> None:
    """Set PADO delay for PPPoE discovery."""
    client.put("/api/v1/pppoe/pado", json={"delay": delay})
    output.success(f"PADO delay set to {delay}ms")


# --- Runtime Config --------------------------------------------------------


@app.command("runtime")
def runtime() -> None:
    """Show PPPoE runtime configuration (service-name, ac-name, verbose)."""
    data = client.get("/api/v1/pppoe/runtime")
    output.response(data, title="PPPoE Runtime Config")


@app.command("runtime-set")
def runtime_set(
    service_name: str = typer.Option(  # pylint: disable=unused-argument
        None, "--service-name", help="PPPoE service name"
    ),
    ac_name: str = typer.Option(  # pylint: disable=unused-argument
        None, "--ac-name", help="Access concentrator name"
    ),
    verbose: bool = typer.Option(  # pylint: disable=unused-argument
        None, "--verbose/--no-verbose", help="Enable/disable verbose logging"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Update PPPoE runtime configuration and reload accel-ppp.

    Only provided fields are updated; omitted fields keep their
    current values. Triggers a graceful reload after writing.
    """
    body = {}
    if service_name is not None:
        body["service_name"] = service_name
    if ac_name is not None:
        body["ac_name"] = ac_name
    if verbose is not None:
        body["verbose"] = verbose
    if not body:
        output.warning(
            "No fields to update. Use --service-name, --ac-name, or --verbose."
        )
        raise typer.Exit(1)
    if not force:
        typer.confirm("Update PPPoE runtime config and reload?", abort=True)
    data = client.put("/api/v1/pppoe/runtime", json=body)
    output.response(data, title="Updated PPPoE Runtime Config")

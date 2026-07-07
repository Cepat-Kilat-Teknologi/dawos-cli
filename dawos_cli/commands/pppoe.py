"""PPPoE management — listeners, MAC filter, PADO delay."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="PPPoE listeners, MAC filter, PADO delay.")


@app.command("interfaces")
def interfaces() -> None:
    """List PPPoE listener interfaces."""
    data = client.get("/api/v1/pppoe/interfaces")
    ifaces = data.get("interfaces", data) if isinstance(data, dict) else data
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
    entries = data.get("entries", data) if isinstance(data, dict) else data
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

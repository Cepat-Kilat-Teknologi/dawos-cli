"""Network management — interfaces, routes, VLANs, DNS, throughput."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Network interfaces, routes, VLANs, DNS, throughput.")


@app.command("interfaces")
def interfaces() -> None:
    """List all network interfaces."""
    data = client.get("/api/v1/network/interfaces")
    ifaces = output.unwrap(data, "interfaces")
    if isinstance(ifaces, list):
        output.table(
            ifaces,
            ["name", "state", "mac", "mtu", "addresses"],
            title="Network Interfaces",
            col_styles={"name": "bold", "state": "green"},
        )
    else:
        output.response(data)


@app.command("interface")
def interface(
    name: str = typer.Argument(..., help="Interface name (e.g. eth0, ppp0)"),
) -> None:
    """Show details of a specific interface."""
    data = client.get(f"/api/v1/network/interfaces/{name}")
    output.response(data, title=f"Interface: {name}")


@app.command("interface-config")
def interface_config(
    name: str = typer.Argument(..., help="Interface name"),
    state: str = typer.Option(None, "--state", help="up or down"),
    mtu: int = typer.Option(None, "--mtu", help="MTU value"),
) -> None:
    """Configure an interface (state, MTU)."""
    body = {}
    if state:
        body["state"] = state
    if mtu:
        body["mtu"] = mtu
    if not body:
        output.error("Specify at least --state or --mtu.")
        raise typer.Exit(1)
    data = client.put(f"/api/v1/network/interfaces/{name}", json=body)
    output.success(f"Interface {name}: updated")
    output.response(data)


@app.command("routes")
def routes() -> None:
    """Show routing table."""
    data = client.get("/api/v1/network/routes")
    rts = output.unwrap(data, "routes")
    if isinstance(rts, list):
        output.table(
            rts,
            ["destination", "gateway", "interface", "metric", "protocol"],
            title="Routes",
        )
    else:
        output.response(data)


@app.command("add-route")
def add_route(
    destination: str = typer.Argument(..., help="Destination CIDR (e.g. 10.0.0.0/24)"),
    gateway: str = typer.Option(None, "--gw", help="Gateway IP"),
    interface: str = typer.Option(  # pylint: disable=redefined-outer-name
        None, "--dev", help="Output interface"
    ),
    metric: int = typer.Option(None, "--metric", help="Route metric"),
) -> None:
    """Add a static route."""
    body = {"destination": destination}
    if gateway:
        body["gateway"] = gateway
    if interface:
        body["device"] = interface
    if metric is not None:
        body["metric"] = metric
    client.post("/api/v1/network/routes", json=body)
    output.success(f"Route added: {destination}")


@app.command("del-route")
def del_route(
    destination: str = typer.Argument(..., help="Destination CIDR to remove"),
    gateway: str = typer.Option(None, "--gw", help="Gateway (to disambiguate)"),
) -> None:
    """Delete a static route."""
    body: dict = {"destination": destination}
    if gateway:
        body["gateway"] = gateway
    client.delete("/api/v1/network/routes", json=body)
    output.success(f"Route deleted: {destination}")


@app.command("dns")
def dns() -> None:
    """Show DNS resolver configuration."""
    data = client.get("/api/v1/network/dns")
    output.response(data, title="DNS Configuration")


@app.command("dns-set")
def dns_set(
    servers: str = typer.Argument(
        ..., help="Comma-separated DNS servers (e.g. 8.8.8.8,1.1.1.1)"
    ),
) -> None:
    """Update DNS resolver servers."""
    server_list = [s.strip() for s in servers.split(",")]
    client.put("/api/v1/network/dns", json={"nameservers": server_list})
    output.success(f"DNS servers updated: {', '.join(server_list)}")


@app.command("vlans")
def vlans() -> None:
    """List VLAN interfaces."""
    data = client.get("/api/v1/network/vlans")
    vl = output.unwrap(data, "vlans")
    if isinstance(vl, list):
        output.table(vl, ["name", "id", "parent", "state"], title="VLANs")
    else:
        output.response(data)


@app.command("vlan-add")
def vlan_add(
    parent: str = typer.Argument(..., help="Parent interface (e.g. eth0)"),
    vid: int = typer.Option(..., "--id", help="VLAN ID (1-4094)"),
    address: str = typer.Option(
        None, "--address", "-a", help="IP address in CIDR (optional)"
    ),
) -> None:
    """Create a VLAN interface."""
    body: dict = {"parent": parent, "vlan_id": vid}
    if address:
        body["address"] = address
    client.post("/api/v1/network/vlans", json=body)
    output.success(f"VLAN {parent}.{vid} created")


@app.command("vlan-del")
def vlan_del(
    name: str = typer.Argument(..., help="VLAN interface name to delete"),
) -> None:
    """Delete a VLAN interface."""
    client.delete(f"/api/v1/network/vlans/{name}")
    output.success(f"VLAN {name} deleted")


@app.command("vlan-state")
def vlan_state(
    name: str = typer.Argument(..., help="VLAN interface name"),
    state: str = typer.Argument(..., help="up or down"),
) -> None:
    """Set VLAN interface state (up/down)."""
    client.put(f"/api/v1/network/vlans/{name}", json={"state": state})
    output.success(f"VLAN {name} → {state}")


def _format_bytes(value: int) -> str:
    """Format byte count into a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024:
            return f"{value:.1f} {unit}" if unit != "B" else f"{value} {unit}"
        value /= 1024  # type: ignore[assignment]
    return f"{value:.1f} PB"


@app.command("throughput")
def throughput() -> None:
    """Show per-interface network throughput counters.

    Reads cumulative byte counters from /proc/net/dev on the BNG node.
    Loopback interfaces are excluded. Only requires viewer-level API key.
    """
    data = client.get("/api/v1/network/throughput")
    ifaces = output.unwrap(data, "interfaces")
    if isinstance(ifaces, list) and ifaces:
        rows = []
        for iface in ifaces:
            rows.append(
                {
                    "name": iface.get("name", "—"),
                    "rx_bytes": _format_bytes(iface.get("rx_bytes", 0)),
                    "tx_bytes": _format_bytes(iface.get("tx_bytes", 0)),
                }
            )
        output.table(
            rows,
            ["name", "rx_bytes", "tx_bytes"],
            title="Network Throughput",
            col_labels={
                "name": "Interface",
                "rx_bytes": "RX (received)",
                "tx_bytes": "TX (transmitted)",
            },
            col_styles={"name": "bold"},
        )
    else:
        output.response(data, title="Network Throughput")

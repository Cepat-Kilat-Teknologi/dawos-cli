"""NAT management — masquerade, egress map, public IP binding, box egress."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="NAT masquerade, egress map, public IP pool.")


@app.command("status")
def status() -> None:
    """Show NAT status (ip_forward, masquerade rules)."""
    data = client.get("/api/v1/firewall/nat/status")
    output.response(data, title="NAT Status")


@app.command("masquerade-on")
def masquerade_on(
    interface: str = typer.Argument(..., help="Outbound interface (e.g. eth0)"),
) -> None:
    """Enable NAT masquerade on an interface."""
    client.post("/api/v1/firewall/nat/masquerade", json={"wan_interface": interface})
    output.success(f"Masquerade enabled on {interface}")


@app.command("masquerade-off")
def masquerade_off(
    interface: str = typer.Argument(..., help="Interface to remove masquerade from"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Disable NAT masquerade on an interface."""
    if not force:
        typer.confirm(f"Disable NAT masquerade on {interface}?", abort=True)
    client.delete("/api/v1/firewall/nat/masquerade", json={"wan_interface": interface})
    output.success(f"Masquerade disabled on {interface}")


@app.command("egress")
def egress() -> None:
    """Show per-customer NAT egress map."""
    data = client.get("/api/v1/firewall/nat/egress")
    output.response(data, title="NAT Egress Map")


@app.command("egress-set")
def egress_set(
    customer_ip: str = typer.Argument(..., help="Customer IP address"),
    public_ip: str = typer.Argument(..., help="Public NAT IP to assign"),
) -> None:
    """Set per-customer NAT egress IP."""
    client.post(
        "/api/v1/firewall/nat/egress",
        json={"target": customer_ip, "public_ip": public_ip},
    )
    output.success(f"Egress: {customer_ip} → {public_ip}")


@app.command("egress-del")
def egress_del(
    customer_ip: str = typer.Argument(..., help="Customer IP to clear egress for"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove per-customer NAT egress mapping."""
    if not force:
        typer.confirm(f"Remove NAT egress mapping for {customer_ip}?", abort=True)
    client.delete(f"/api/v1/firewall/nat/egress/{customer_ip}")
    output.success(f"Egress cleared for {customer_ip}")


@app.command("public-ip-add")
def public_ip_add(
    ip: str = typer.Argument(..., help="Public IP to bind to uplink"),
) -> None:
    """Bind a public NAT IP to the uplink interface."""
    client.post("/api/v1/firewall/nat/public-ip", json={"public_ip": ip})
    output.success(f"Public IP {ip} bound")


@app.command("public-ip-del")
def public_ip_del(
    ip: str = typer.Argument(..., help="Public IP to unbind"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Unbind a public NAT IP from the uplink interface."""
    if not force:
        typer.confirm(f"Unbind public IP {ip}?", abort=True)
    client.delete(f"/api/v1/firewall/nat/public-ip/{ip}")
    output.success(f"Public IP {ip} unbound")


@app.command("box-egress")
def box_egress() -> None:
    """Show the server's own internet egress status."""
    data = client.get("/api/v1/firewall/nat/box-egress")
    output.response(data, title="Box Egress")


@app.command("box-egress-set")
def box_egress_set(
    enabled: bool = typer.Argument(
        ..., help="true/false — enable/disable box internet"
    ),
) -> None:
    """Toggle the server's own internet egress (for apt, NTP, etc.)."""
    action = "on" if enabled else "off"
    client.post("/api/v1/firewall/nat/box-egress", json={"action": action})
    state = "enabled" if enabled else "disabled"
    output.success(f"Box egress {state}")

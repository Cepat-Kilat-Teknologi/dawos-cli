"""Firewall management — nftables rules, sysctl, conntrack, SNMP, groups."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Firewall rules, sysctl, conntrack, SNMP.")


@app.command("status")
def status() -> None:
    """Show firewall status (nftables ruleset summary)."""
    data = client.get("/api/v1/firewall/status")
    output.response(data, title="Firewall Status")


@app.command("rules")
def rules() -> None:
    """List all nftables rules."""
    data = client.get("/api/v1/firewall/rules")
    if isinstance(data, dict) and "ruleset" in data:
        output.print_raw(data["ruleset"])
    else:
        output.response(data, title="Firewall Rules")


@app.command("save")
def save() -> None:
    """Persist the current nftables ruleset to disk."""
    data = client.post("/api/v1/firewall/save")
    output.success(f"Ruleset saved: {data.get('message', 'ok')}")


@app.command("validate")
def validate(
    ruleset: str = typer.Argument(..., help="Ruleset content to validate"),
) -> None:
    """Validate an nftables configuration."""
    data = client.post("/api/v1/firewall/validate", json={"ruleset": ruleset})
    output.response(data, title="Validation Result")


@app.command("sysctl")
def sysctl() -> None:
    """Show kernel parameters (sysctl)."""
    data = client.get("/api/v1/firewall/sysctl")
    output.response(data, title="Sysctl Parameters")


@app.command("sysctl-set")
def sysctl_set(
    key: str = typer.Argument(..., help="Sysctl key (e.g. net.ipv4.ip_forward)"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a kernel parameter."""
    client.put("/api/v1/firewall/sysctl", json={"key": key, "value": value})
    output.success(f"{key} = {value}")


@app.command("conntrack")
def conntrack() -> None:
    """Show conntrack table settings."""
    data = client.get("/api/v1/firewall/conntrack")
    output.response(data, title="Conntrack")


@app.command("conntrack-set")
def conntrack_set(
    max_entries: int = typer.Argument(..., help="Max conntrack entries"),
) -> None:
    """Update conntrack table max size."""
    client.put("/api/v1/firewall/conntrack", json={"max": max_entries})
    output.success(f"Conntrack max → {max_entries}")


@app.command("snmp")
def snmp() -> None:
    """Show SNMP status."""
    data = client.get("/api/v1/firewall/snmp")
    output.response(data, title="SNMP Status")


# --- Firewall Groups -------------------------------------------------------


@app.command("groups")
def groups() -> None:
    """List firewall groups (address/port/network)."""
    data = client.get("/api/v1/firewall/groups")
    grps = data.get("groups", data) if isinstance(data, dict) else data
    if isinstance(grps, list):
        output.table(grps, ["name", "group_type", "elements"], title="Firewall Groups")
    else:
        output.response(data)


@app.command("group-add")
def group_add(
    name: str = typer.Argument(..., help="Group name"),
    group_type: str = typer.Option(
        ..., "--type", "-t", help="address, port, or network"
    ),
    elements: str = typer.Option(
        "", "--elements", "-e", help="Comma-separated initial elements"
    ),
) -> None:
    """Create a firewall group."""
    body = {"name": name, "group_type": group_type}
    if elements:
        body["elements"] = [e.strip() for e in elements.split(",")]
    data = client.post("/api/v1/firewall/groups", json=body)
    if isinstance(data, dict) and data.get("success") is False:
        output.error(data.get("message") or "Group creation failed")
        raise typer.Exit(1)
    output.success(f"Group '{name}' created (type: {group_type})")


@app.command("group-del")
def group_del(
    name: str = typer.Argument(..., help="Group name to delete"),
) -> None:
    """Delete a firewall group."""
    data = client.delete(f"/api/v1/firewall/groups/{name}")
    if isinstance(data, dict) and data.get("success") is False:
        output.error(data.get("message") or "Group deletion failed")
        raise typer.Exit(1)
    output.success(f"Group '{name}' deleted")


@app.command("group-members")
def group_members(
    name: str = typer.Argument(..., help="Group name"),
    elements: str = typer.Argument(..., help="Comma-separated elements to add"),
) -> None:
    """Add members to a firewall group."""
    elems = [e.strip() for e in elements.split(",")]
    data = client.post(
        f"/api/v1/firewall/groups/{name}/members", json={"elements": elems}
    )
    if isinstance(data, dict) and data.get("success") is False:
        output.error(data.get("message") or "Failed to add members")
        raise typer.Exit(1)
    output.success(f"Added {len(elems)} member(s) to '{name}'")

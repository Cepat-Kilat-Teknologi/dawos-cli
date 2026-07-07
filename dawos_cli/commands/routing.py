"""Routing — BGP, OSPF, RIP, BFD status via FRR/vtysh."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Dynamic routing — BGP, OSPF, RIP, BFD.")


# --- BGP -------------------------------------------------------------------


@app.command("bgp")
def bgp() -> None:
    """Show BGP peer summary."""
    data = client.get("/api/v1/routing/bgp/status")
    output.response(data, title="BGP Status")


@app.command("bgp-routes")
def bgp_routes() -> None:
    """Show BGP routing table."""
    data = client.get("/api/v1/routing/bgp/routes")
    routes = data.get("routes", data) if isinstance(data, dict) else data
    if isinstance(routes, list):
        output.table(
            routes,
            ["prefix", "next_hop", "metric", "as_path", "status"],
            title="BGP Routes",
        )
    else:
        output.response(data)


# --- OSPF ------------------------------------------------------------------


@app.command("ospf")
def ospf() -> None:
    """Show OSPF status and neighbors."""
    data = client.get("/api/v1/routing/ospf/status")
    output.response(data, title="OSPF Status")


@app.command("ospf-neighbors")
def ospf_neighbors() -> None:
    """Show OSPF neighbor adjacencies."""
    data = client.get("/api/v1/routing/ospf/neighbors")
    neighbors = data.get("neighbors", data) if isinstance(data, dict) else data
    if isinstance(neighbors, list):
        output.table(
            neighbors,
            ["neighbor_id", "state", "address", "interface", "dead_time"],
            title="OSPF Neighbors",
        )
    else:
        output.response(data)


@app.command("ospf-routes")
def ospf_routes() -> None:
    """Show OSPF routing table."""
    data = client.get("/api/v1/routing/ospf/routes")
    output.response(data, title="OSPF Routes")


# --- RIP -------------------------------------------------------------------


@app.command("rip")
def rip() -> None:
    """Show RIP status."""
    data = client.get("/api/v1/routing/rip/status")
    output.response(data, title="RIP Status")


@app.command("rip-routes")
def rip_routes() -> None:
    """Show RIP routing table."""
    data = client.get("/api/v1/routing/rip/routes")
    output.response(data, title="RIP Routes")


# --- BFD -------------------------------------------------------------------


@app.command("bfd")
def bfd() -> None:
    """Show BFD summary."""
    data = client.get("/api/v1/routing/bfd/summary")
    output.response(data, title="BFD Summary")


@app.command("bfd-peers")
def bfd_peers() -> None:
    """Show BFD peer sessions."""
    data = client.get("/api/v1/routing/bfd/peers")
    peers = data.get("peers", data) if isinstance(data, dict) else data
    if isinstance(peers, list):
        output.table(
            peers, ["peer", "status", "interface", "uptime"], title="BFD Peers"
        )
    else:
        output.response(data)

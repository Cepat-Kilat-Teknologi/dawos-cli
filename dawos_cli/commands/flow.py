"""Flow accounting — NetFlow/sFlow/IPFIX status, collectors, stats."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Flow accounting (NetFlow / sFlow / IPFIX).")


@app.command("status")
def status() -> None:
    """Show flow accounting status."""
    data = client.get("/api/v1/flow/status")
    output.response(data, title="Flow Accounting Status")


@app.command("collectors")
def collectors() -> None:
    """List configured flow collectors."""
    data = client.get("/api/v1/flow/collectors")
    coll = data.get("collectors", data) if isinstance(data, dict) else data
    if isinstance(coll, list):
        output.table(
            coll,
            ["name", "address", "port", "protocol", "status"],
            title="Flow Collectors",
            col_styles={"name": "bold", "address": "cyan"},
        )
    else:
        output.response(data)


@app.command("stats")
def stats() -> None:
    """Show flow accounting statistics."""
    data = client.get("/api/v1/flow/stats")
    output.response(data, title="Flow Stats")


@app.command("restart")
def restart(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart the flow accounting daemon."""
    if not force:
        typer.confirm("Restart flow accounting?", abort=True)
    client.post("/api/v1/flow/restart")
    output.success("Flow accounting restarted")

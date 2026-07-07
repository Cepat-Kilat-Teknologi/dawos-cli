"""NTP — time sync status and sources."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="NTP time synchronisation.")


@app.command("status")
def status() -> None:
    """Show NTP synchronisation status."""
    data = client.get("/api/v1/ntp/status")
    output.response(data, title="NTP Status")


@app.command("sources")
def sources() -> None:
    """List NTP upstream sources."""
    data = client.get("/api/v1/ntp/sources")
    src_list = data.get("sources", data) if isinstance(data, dict) else data
    if isinstance(src_list, list):
        output.table(
            src_list,
            ["server", "stratum", "offset", "delay", "jitter", "reach"],
            title="NTP Sources",
            col_styles={"server": "bold"},
        )
    else:
        output.response(data)

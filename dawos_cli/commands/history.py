"""Session history — snapshot, query, purge, stats."""

from __future__ import annotations

from typing import Optional
from urllib.parse import quote

import typer

from .. import client, output

app = typer.Typer(help="Session history database management.")


@app.command("list")
def list_history(
    username: Optional[str] = typer.Option(None, help="Filter by username"),
    ip: Optional[str] = typer.Option(None, help="Filter by IP address"),
    start: Optional[str] = typer.Option(None, help="ISO-8601 lower bound"),
    end: Optional[str] = typer.Option(None, help="ISO-8601 upper bound"),
    limit: int = typer.Option(100, help="Max records (1-1000)"),
    offset: int = typer.Option(0, help="Pagination offset"),
) -> None:
    """Query session history with optional filters."""
    params: dict = {"limit": limit, "offset": offset}
    if username:
        params["username"] = username
    if ip:
        params["ip"] = ip
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    data = client.get("/api/v1/sessions/history", **params)
    records = output.unwrap(data, "records")
    if isinstance(records, list) and records:
        output.table(
            records,
            [
                "snapshot_at",
                "username",
                "ip",
                "ifname",
                "state",
                "uptime",
            ],
            title="Session History",
            col_styles={"username": "bold", "ip": "cyan"},
        )
    elif isinstance(records, list):
        output.warning("No history records found.")
    else:
        output.response(data)


@app.command("snapshot")
def snapshot() -> None:
    """Capture a snapshot of all active PPPoE sessions.

    Records the current state of every active session in the
    history database for later review.
    """
    data = client.post("/api/v1/sessions/history/snapshot")
    count = data.get("captured", "?")
    output.success(f"Snapshot captured: {count} session(s) recorded")


@app.command("purge")
def purge(
    before: str = typer.Argument(
        ..., help="ISO-8601 cutoff timestamp (delete records older than this)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Purge session history records older than a timestamp.

    Deletes all records with snapshot_at < before.
    This is a destructive operation for disk management / GDPR.
    """
    if not force:
        typer.confirm(f"Purge history records before {before}?", abort=True)
    encoded = quote(before, safe="")
    data = client.delete(f"/api/v1/sessions/history?before={encoded}")
    deleted = data.get("deleted", "?")
    output.success(f"Purged {deleted} history record(s)")


@app.command("stats")
def stats() -> None:
    """Show session history database statistics.

    Returns record counts, unique users, date range,
    and database file size.
    """
    data = client.get("/api/v1/sessions/history/stats")
    output.response(data, title="History Statistics")

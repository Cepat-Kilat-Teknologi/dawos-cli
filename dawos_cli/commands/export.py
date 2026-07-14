"""CSV export — download sessions and history as CSV files."""

from __future__ import annotations

import pathlib
from typing import Optional

import typer

from .. import client, output

app = typer.Typer(help="Export data as CSV files.")


@app.command("sessions")
def sessions_csv(
    out: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save to file instead of stdout"
    ),
) -> None:
    """Export all active PPPoE sessions as CSV.

    Downloads the session table as an RFC 4180-compliant CSV.
    Prints to stdout by default, or saves to a file with --output.
    """
    csv_text = client.get_text("/api/v1/export/sessions")
    _write_csv(csv_text, out, "sessions")


@app.command("history")
def history_csv(
    username: Optional[str] = typer.Option(None, help="Filter by username"),
    ip: Optional[str] = typer.Option(None, help="Filter by IP address"),
    start: Optional[str] = typer.Option(None, help="ISO-8601 lower bound"),
    end: Optional[str] = typer.Option(None, help="ISO-8601 upper bound"),
    limit: int = typer.Option(10000, help="Max records (1-50000)"),
    out: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save to file instead of stdout"
    ),
) -> None:
    """Export session history records as CSV.

    Downloads history as an RFC 4180-compliant CSV file.
    Prints to stdout by default, or saves to a file with --output.
    """
    params: dict = {"limit": limit}
    if username:
        params["username"] = username
    if ip:
        params["ip"] = ip
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    csv_text = client.get_text("/api/v1/export/history", **params)
    _write_csv(csv_text, out, "history")


def _write_csv(csv_text: str, filepath: Optional[str], label: str) -> None:
    """Write CSV data to stdout or a file."""
    if filepath:
        pathlib.Path(filepath).write_text(csv_text, encoding="utf-8")
        output.success(f"Saved {label} CSV to {filepath}")
    else:
        output.print_raw(csv_text)

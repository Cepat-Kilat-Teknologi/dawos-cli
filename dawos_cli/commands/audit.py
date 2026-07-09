"""Audit log — query the in-memory audit trail."""

from __future__ import annotations

from typing import Optional

import typer

from .. import client, output

app = typer.Typer(help="Audit log viewer (admin only).")


@app.command("list")
def list_entries(
    limit: int = typer.Option(100, "--limit", "-n", help="Max entries (1-1000)"),
    method: Optional[str] = typer.Option(
        None, "--method", help="Filter by HTTP method"
    ),
    path: Optional[str] = typer.Option(None, "--path", help="Filter by path prefix"),
    role: Optional[str] = typer.Option(None, "--role", help="Filter by RBAC role"),
    status: Optional[int] = typer.Option(
        None, "--status", help="Filter by status code"
    ),
) -> None:
    """List recent audit log entries (newest first)."""
    params: dict = {"limit": limit}
    if method:
        params["method"] = method
    if path:
        params["path"] = path
    if role:
        params["role"] = role
    if status is not None:
        params["status"] = status
    data = client.get("/api/v1/audit", **params)
    entries = data.get("entries", data) if isinstance(data, dict) else data
    if isinstance(entries, list):
        count = (
            data.get("count", len(entries)) if isinstance(data, dict) else len(entries)
        )
        output.table(
            entries,
            ["timestamp", "method", "path", "role", "status", "duration_ms"],
            title=f"Audit Log ({count} entries)",
        )
    else:
        output.response(data)

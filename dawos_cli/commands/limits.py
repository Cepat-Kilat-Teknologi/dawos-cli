"""Connection limits — global and per-interface limits."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Connection limits management.")


@app.command("show")
def show() -> None:
    """Show current connection limits."""
    data = client.get("/api/v1/limits")
    output.response(data, title="Connection Limits")


@app.command("set")
def set_limits(
    max_sessions: int = typer.Option(
        None, "--max-sessions", help="Maximum total sessions"
    ),
    max_starting: int = typer.Option(
        None, "--max-starting", help="Maximum sessions in starting state"
    ),
) -> None:
    """Update global connection limits."""
    payload: dict = {}
    if max_sessions is not None:
        payload["max_sessions"] = max_sessions
    if max_starting is not None:
        payload["max_starting"] = max_starting
    if not payload:
        output.warning("No limits specified. Use --max-sessions or --max-starting.")
        raise typer.Exit(1)
    client.put("/api/v1/limits", json=payload)
    output.success("Connection limits updated")


@app.command("interface")
def interface(
    name: str = typer.Argument(..., help="Interface name"),
) -> None:
    """Show connection limits for a specific interface."""
    data = client.get(f"/api/v1/limits/interface/{name}")
    output.response(data, title=f"Limits: {name}")

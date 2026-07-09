"""Service management — start, stop, restart accel-ppp, raw accel-cmd."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Manage accel-ppp service.")


@app.command("status")
def status() -> None:
    """Show accel-ppp service status."""
    data = client.get("/api/v1/service/status")
    output.response(data, title="Service Status")


@app.command("start")
def start() -> None:
    """Start accel-ppp service."""
    data = client.post("/api/v1/service/start")
    output.success(f"accel-ppp: {data.get('message', 'started')}")


@app.command("stop")
def stop(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Stop accel-ppp service (drops all sessions)."""
    if not force:
        typer.confirm("This will drop ALL active sessions. Continue?", abort=True)
    data = client.post("/api/v1/service/stop")
    output.success(f"accel-ppp: {data.get('message', 'stopped')}")


@app.command("restart")
def restart(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart accel-ppp service."""
    if not force:
        typer.confirm("This will briefly drop all sessions. Continue?", abort=True)
    data = client.post("/api/v1/service/restart")
    output.success(f"accel-ppp: {data.get('message', 'restarted')}")


@app.command("cmd")
def cmd(
    command: str = typer.Argument(..., help="Raw accel-cmd command (e.g. 'show stat')"),
) -> None:
    """Execute a raw accel-cmd command on the BNG."""
    data = client.post("/api/v1/service/command", json={"command": command})
    if isinstance(data, dict) and "output" in data:
        output.print_raw(data["output"])
    else:
        output.response(data)


@app.command("shutdown")
def shutdown(
    mode: str = typer.Option("soft", "--mode", "-m", help="'soft' (drain) or 'hard'"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Initiate graceful shutdown of accel-ppp.

    Soft (drain) mode stops accepting new connections but keeps existing
    sessions alive until they disconnect naturally.  Hard mode drops all
    sessions immediately.
    """
    label = "drain (keep existing sessions)" if mode == "soft" else "HARD (drop all)"
    if not force:
        typer.confirm(f"Shutdown accel-ppp in {label} mode?", abort=True)
    data = client.post(
        "/api/v1/service/shutdown",
        json={"mode": mode, "confirm": True},
    )
    sessions = data.get("active_sessions", 0)
    msg = data.get("message", f"Shutdown ({mode}) initiated")
    output.success(f"{msg} — {sessions} active session(s)")


@app.command("shutdown-cancel")
def shutdown_cancel() -> None:
    """Cancel a pending soft shutdown and resume normal operation."""
    data = client.post("/api/v1/service/shutdown/cancel")
    sessions = data.get("active_sessions", 0)
    output.success(
        f"{data.get('message', 'Shutdown cancelled')} — {sessions} active session(s)"
    )

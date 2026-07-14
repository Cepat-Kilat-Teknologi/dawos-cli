"""Session management — list, find, stats, terminate, control."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="PPPoE session management.")


@app.command("list")
def list_sessions() -> None:
    """List all active PPPoE sessions."""
    data = client.get("/api/v1/sessions")
    sessions = output.unwrap(data, "sessions")
    if isinstance(sessions, list):
        output.table(
            sessions,
            ["username", "ip", "rate_limit", "type", "state", "uptime"],
            title="Active Sessions",
            col_styles={"username": "bold", "ip": "cyan", "state": "green"},
        )
    else:
        output.response(data)


@app.command("stats")
def stats() -> None:
    """Show session statistics."""
    data = client.get("/api/v1/sessions/stats")
    output.response(data, title="Session Statistics")


@app.command("find")
def find(
    username: str = typer.Argument(..., help="Username to search for"),
) -> None:
    """Find a subscriber's active session by username."""
    data = client.get(f"/api/v1/sessions/find/{username}")
    sessions = output.unwrap(data, "sessions")
    if isinstance(sessions, list) and sessions:
        output.table(
            sessions,
            [
                "username",
                "ip",
                "rate_limit",
                "type",
                "state",
                "uptime",
                "rx_bytes",
                "tx_bytes",
            ],
            title=f"Sessions for '{username}'",
        )
    elif isinstance(sessions, list):
        output.warning(f"No active session found for '{username}'.")
    else:
        output.response(data)


@app.command("terminate")
def terminate(
    username: str = typer.Argument(..., help="Username to terminate"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Terminate a session by username."""
    if not force:
        typer.confirm(f"Terminate session for {username}?", abort=True)
    data = client.post("/api/v1/sessions/terminate", json={"username": username})
    output.success(f"Session {username}: {data.get('message', 'terminated')}")


@app.command("by-sid")
def by_sid(
    sid: str = typer.Argument(..., help="Session ID"),
) -> None:
    """Look up a session by its SID."""
    data = client.get(f"/api/v1/sessions/control/by-sid/{sid}")
    output.response(data, title=f"Session {sid}")


@app.command("by-ip")
def by_ip(
    ip: str = typer.Argument(..., help="IP address"),
) -> None:
    """Look up a session by its IP address."""
    data = client.get(f"/api/v1/sessions/control/by-ip/{ip}")
    output.response(data, title=f"Session {ip}")


@app.command("snapshot")
def snapshot(
    username: str = typer.Argument(..., help="Username"),
) -> None:
    """Get a full snapshot of a subscriber's session."""
    data = client.get(f"/api/v1/sessions/control/snapshot/{username}")
    output.response(data, title=f"Snapshot: {username}")


@app.command("restart")
def restart_session(
    username: str = typer.Argument(..., help="Username to restart"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restart a subscriber's session (drop + reconnect)."""
    if not force:
        typer.confirm(f"Restart session for {username}?", abort=True)
    data = client.post("/api/v1/sessions/control/restart", json={"username": username})
    output.success(f"Session restart: {data.get('message', 'done')}")


@app.command("drop-by-mac")
def drop_by_mac(
    mac: str = typer.Argument(..., help="MAC address"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Drop a session by MAC address."""
    if not force:
        typer.confirm(f"Drop session with MAC {mac}?", abort=True)
    data = client.post("/api/v1/sessions/control/drop-by-mac", json={"mac": mac})
    output.success(f"Drop by MAC: {data.get('message', 'done')}")


# --- Session Search --------------------------------------------------------


@app.command("search-mac")
def search_mac(
    mac: str = typer.Argument(..., help="MAC address (AA:BB:CC:DD:EE:FF)"),
) -> None:
    """Search sessions by calling-station-id (MAC address)."""
    data = client.get(f"/api/v1/sessions/search/mac/{mac}")
    sessions = output.unwrap(data, "sessions")
    if isinstance(sessions, list) and sessions:
        output.table(
            sessions,
            ["username", "ip", "rate_limit", "type", "state", "uptime"],
            title=f"Sessions matching MAC {mac}",
            col_styles={"username": "bold", "ip": "cyan"},
        )
    elif isinstance(sessions, list):
        output.warning(f"No sessions found for MAC {mac}.")
    else:
        output.response(data)


@app.command("search-ip")
def search_ip(
    ip: str = typer.Argument(..., help="IP address to search"),
) -> None:
    """Search sessions by assigned IP address."""
    data = client.get(f"/api/v1/sessions/search/ip/{ip}")
    sessions = output.unwrap(data, "sessions")
    if isinstance(sessions, list) and sessions:
        output.table(
            sessions,
            ["username", "ip", "rate_limit", "type", "state", "uptime"],
            title=f"Sessions matching IP {ip}",
            col_styles={"username": "bold", "ip": "cyan"},
        )
    elif isinstance(sessions, list):
        output.warning(f"No sessions found for IP {ip}.")
    else:
        output.response(data)


@app.command("search-sid")
def search_sid(
    sid: str = typer.Argument(..., help="Session ID to search"),
) -> None:
    """Search sessions by accel-ppp session ID."""
    data = client.get(f"/api/v1/sessions/search/sid/{sid}")
    sessions = output.unwrap(data, "sessions")
    if isinstance(sessions, list) and sessions:
        output.table(
            sessions,
            ["username", "ip", "rate_limit", "type", "state", "uptime"],
            title=f"Sessions matching SID {sid}",
            col_styles={"username": "bold", "ip": "cyan"},
        )
    elif isinstance(sessions, list):
        output.warning(f"No sessions found for SID {sid}.")
    else:
        output.response(data)

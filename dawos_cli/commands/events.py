"""Event hooks — create, list, delete hooks; fire events; view history."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Event hooks and webhook management.")


@app.command("hooks")
def hooks() -> None:
    """List all configured event hooks."""
    data = client.get("/api/v1/events/hooks")
    hook_list = output.unwrap(data, "hooks")
    if isinstance(hook_list, list):
        output.table(
            hook_list,
            ["name", "event", "action", "url"],
            title="Event Hooks",
            col_styles={"name": "bold", "event": "cyan"},
        )
    else:
        output.response(data)


@app.command("hook-add")
def hook_add(
    name: str = typer.Argument(..., help="Hook name"),
    event: str = typer.Option(
        ...,
        "--event",
        "-e",
        help="Event type (session-up, session-down, config-reload, etc.)",
    ),
    action: str = typer.Option(..., "--action", "-a", help="Webhook URL or command"),
) -> None:
    """Create an event hook."""
    client.post(
        "/api/v1/events/hooks", json={"name": name, "event": event, "action": action}
    )
    output.success(f"Hook '{name}' created for event '{event}'")


@app.command("hook-del")
def hook_del(
    name: str = typer.Argument(..., help="Hook name to delete"),
) -> None:
    """Delete an event hook."""
    client.delete(f"/api/v1/events/hooks/{name}")
    output.success(f"Hook '{name}' deleted")


@app.command("fire")
def fire(
    event: str = typer.Argument(..., help="Event name to fire"),
    payload: str = typer.Option("{}", "--payload", "-d", help="JSON payload"),
) -> None:
    """Manually fire an event (triggers all matching hooks)."""
    import json  # pylint: disable=import-outside-toplevel

    try:
        payload_data = json.loads(payload)
    except json.JSONDecodeError as exc:
        output.error("Invalid JSON payload.")
        raise typer.Exit(1) from exc
    data = client.post(
        "/api/v1/events/fire", json={"event": event, "payload": payload_data}
    )
    output.success(f"Event '{event}' fired")
    output.response(data)


@app.command("history")
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries"),
) -> None:
    """Show event history."""
    data = client.get("/api/v1/events/history", limit=limit)
    entries = output.unwrap(data, "entries")
    if isinstance(entries, list):
        output.table(
            entries,
            ["timestamp", "event", "hook", "status", "duration_ms"],
            title="Event History",
        )
    else:
        output.response(data)


@app.command("history-clear")
def history_clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Clear event history."""
    if not force:
        typer.confirm("Clear all event history?", abort=True)
    client.delete("/api/v1/events/history")
    output.success("Event history cleared")

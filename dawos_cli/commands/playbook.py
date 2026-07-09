"""Operational playbooks — pre-defined automation sequences."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Operational playbooks (health-check, backup, safe-restart).")


@app.command("list")
def list_playbooks() -> None:
    """List available operational playbooks."""
    data = client.get("/api/v1/playbooks")
    playbooks = data.get("playbooks", data) if isinstance(data, dict) else data
    if isinstance(playbooks, list):
        count = (
            data.get("count", len(playbooks))
            if isinstance(data, dict)
            else len(playbooks)
        )
        output.table(
            playbooks,
            ["name", "description", "min_role"],
            title=f"Playbooks ({count})",
        )
    else:
        output.response(data)


@app.command("run")
def run(
    name: str = typer.Argument(
        ..., help="Playbook name (health-check, backup-config, safe-restart)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Execute a named operational playbook."""
    if not force:
        typer.confirm(f"Run playbook '{name}'?", abort=True)
    data = client.post(f"/api/v1/playbooks/{name}/run")
    steps = data.get("steps", [])
    all_ok = data.get("success", False)
    status_icon = "✓" if all_ok else "✗"
    output.info(f"Playbook [bold]{name}[/]: {status_icon}")
    if steps:
        output.table(steps, ["name", "success", "output", "error"], title="Steps")

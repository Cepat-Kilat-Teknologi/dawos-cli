"""Config management — read, update, backups, checkpoint, rollback."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="accel-ppp configuration management.")


# --- Config ----------------------------------------------------------------


@app.command("show")
def show() -> None:
    """Show the current accel-ppp configuration."""
    data = client.get("/api/v1/config")
    if isinstance(data, dict) and "content" in data:
        output.print_raw(data["content"])
    else:
        output.response(data, title="Configuration")


@app.command("update")
def update(
    content: str = typer.Argument(
        ..., help="New config content (or @filename to read from file)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Update the accel-ppp configuration."""
    if content.startswith("@"):
        import pathlib  # pylint: disable=import-outside-toplevel

        path = pathlib.Path(content[1:])
        if not path.exists():
            output.error(f"File not found: {path}")
            raise typer.Exit(1)
        content = path.read_text(encoding="utf-8")
    if not force:
        typer.confirm("Update accel-ppp configuration?", abort=True)
    data = client.put("/api/v1/config", json={"content": content})
    output.success(f"Config: {data.get('message', 'updated')}")


@app.command("backups")
def backups() -> None:
    """List configuration backups."""
    data = client.get("/api/v1/config/backups")
    if isinstance(data, dict) and "backups" in data:
        output.response(data["backups"], title="Config Backups")
    else:
        output.response(data)


# --- Checkpoint ------------------------------------------------------------


@app.command("revisions")
def revisions() -> None:
    """List config checkpoint revisions."""
    data = client.get("/api/v1/config/revisions")
    revs = data.get("revisions", data) if isinstance(data, dict) else data
    if isinstance(revs, list):
        output.table(revs, ["name", "timestamp", "size"], title="Checkpoint Revisions")
    else:
        output.response(data)


@app.command("diff")
def diff(
    backup_name: str = typer.Argument(..., help="Backup name to diff against"),
) -> None:
    """Show diff between current config and a backup checkpoint."""
    data = client.get("/api/v1/config/diff", backup_name=backup_name)
    if isinstance(data, dict) and "diff" in data:
        output.print_raw(data["diff"])
    else:
        output.response(data, title="Config Diff")


@app.command("rollback")
def rollback(
    backup_name: str = typer.Argument(..., help="Backup name to rollback to"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Rollback configuration to a specific checkpoint."""
    if not force:
        typer.confirm(f"Rollback config to '{backup_name}'?", abort=True)
    data = client.post(f"/api/v1/config/rollback/{backup_name}")
    output.success(f"Rollback: {data.get('message', 'done')}")


@app.command("apply")
def apply(
    content: str = typer.Argument(
        ..., help="Config content to apply (or @filename to read from file)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Apply configuration with guarded rollback (auto-reverts on failure)."""
    if content.startswith("@"):
        import pathlib  # pylint: disable=import-outside-toplevel

        path = pathlib.Path(content[1:])
        if not path.exists():
            output.error(f"File not found: {path}")
            raise typer.Exit(1)
        content = path.read_text(encoding="utf-8")
    if not force:
        typer.confirm("Apply config with guarded rollback?", abort=True)
    data = client.post("/api/v1/config/apply", json={"content": content})
    output.response(data, title="Guarded Apply")
    output.info("Run [bold]dawos config confirm[/] within the timeout to keep changes.")


@app.command("confirm")
def confirm() -> None:
    """Confirm a pending guarded apply (prevents auto-rollback)."""
    data = client.post("/api/v1/config/confirm")
    output.success(f"Confirm: {data.get('message', 'confirmed')}")


@app.command("apply-status")
def apply_status() -> None:
    """Check the status of a pending guarded apply."""
    data = client.get("/api/v1/config/apply/status")
    output.response(data, title="Apply Status")

"""Scheduler — list, create, delete, and run scheduled jobs."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Task scheduler — cron-like jobs on the BNG.")


@app.command("list")
def list_jobs() -> None:
    """List all scheduled jobs."""
    data = client.get("/api/v1/scheduler/jobs")
    jobs = output.unwrap(data, "jobs")
    if isinstance(jobs, list):
        output.table(
            jobs,
            ["name", "command", "interval_seconds", "enabled", "last_run"],
            title="Scheduled Jobs",
            col_styles={"name": "bold"},
        )
    else:
        output.response(data)


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Job name"),
    command: str = typer.Option(
        ..., "--command", "-c", help="Shell command to execute"
    ),
    interval: int = typer.Option(
        ..., "--interval", "-i", help="Repeat interval in seconds (min 10)"
    ),
    enabled: bool = typer.Option(
        True, "--enabled/--disabled", help="Whether the job runs on schedule"
    ),
) -> None:
    """Create a scheduled job."""
    client.post(
        "/api/v1/scheduler/jobs",
        json={
            "name": name,
            "command": command,
            "interval_seconds": interval,
            "enabled": enabled,
        },
    )
    output.success(f"Job '{name}' created: every {interval}s")


@app.command("remove")
def remove(
    name: str = typer.Argument(..., help="Job name to delete"),
) -> None:
    """Delete a scheduled job."""
    client.delete(f"/api/v1/scheduler/jobs/{name}")
    output.success(f"Job '{name}' deleted")


@app.command("run")
def run(
    name: str = typer.Argument(..., help="Job name to run immediately"),
) -> None:
    """Manually trigger a scheduled job now."""
    data = client.post(f"/api/v1/scheduler/jobs/{name}/run")
    output.success(f"Job '{name}' triggered")
    output.response(data)

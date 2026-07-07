"""Diagnostics — system doctor health check."""

from __future__ import annotations

import typer
from rich.panel import Panel

from .. import client, output

app = typer.Typer(help="System diagnostics and health checks.")


@app.command("doctor")
def doctor() -> None:
    """Run a comprehensive system health check.

    Checks services, disk, memory, network, config validity, and more.
    """
    output.info("Running system diagnostics…")
    data = client.get("/api/v1/diagnostics/doctor")

    # Pretty-print the doctor report
    checks = data.get("checks", data) if isinstance(data, dict) else data
    if isinstance(checks, list):
        for check in checks:
            name = check.get("name", "?")
            status = check.get("status", "unknown")
            detail = check.get("detail", "")
            if status == "ok":
                icon = "[green]✓[/]"
            elif status == "warning":
                icon = "[yellow]⚠[/]"
            else:
                icon = "[red]✗[/]"
            output.console.print(f"  {icon} [bold]{name}[/]  {detail}")

        # Summary
        ok = sum(1 for c in checks if c.get("status") == "ok")
        warn = sum(1 for c in checks if c.get("status") == "warning")
        fail = sum(1 for c in checks if c.get("status") not in ("ok", "warning"))
        summary = f"[green]{ok} passed[/]"
        if warn:
            summary += f"  [yellow]{warn} warnings[/]"
        if fail:
            summary += f"  [red]{fail} failed[/]"
        output.console.print(
            Panel(summary, title="Doctor Summary", border_style="blue")
        )
    else:
        output.response(data, title="Diagnostics")

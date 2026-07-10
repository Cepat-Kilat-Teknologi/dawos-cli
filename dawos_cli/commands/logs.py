"""Logs — tail and stream BNG logs."""

from __future__ import annotations

import json

import typer

from .. import client, output

app = typer.Typer(help="BNG log viewer.")


@app.command("tail")
def tail(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines"),
    service: str = typer.Option(None, "--service", "-s", help="Filter by service name"),
) -> None:
    """Show recent log entries."""
    params: dict = {"lines": lines}
    if service:
        params["service"] = service
    data = client.get("/api/v1/logs/tail", **params)
    entries = output.unwrap(data, "lines")
    if isinstance(entries, list):
        for line in entries:
            if isinstance(line, dict):
                ts = line.get("timestamp", "")
                svc = line.get("service", "")
                msg = line.get("message", "")
                level = line.get("level", "info")
                color = {"error": "red", "warning": "yellow", "debug": "dim"}.get(
                    level, "white"
                )
                output.console.print(
                    f"[dim]{ts}[/] [cyan]{svc:12s}[/] [{color}]{msg}[/]"
                )
            else:
                output.console.print(str(line))
    else:
        output.response(data)


@app.command("stream")
def stream(
    service: str = typer.Option(None, "--service", "-s", help="Filter by service name"),
) -> None:
    """Stream logs in real time (SSE). Press Ctrl+C to stop."""
    url = "/api/v1/logs/stream"
    if service:
        url += f"?service={service}"
    output.info("Streaming logs… (Ctrl+C to stop)")
    try:
        for line in client.stream_sse(url):
            try:
                entry = json.loads(line)
                if isinstance(entry, dict):
                    ts = entry.get("timestamp", "")
                    svc = entry.get("service", "")
                    msg = entry.get("message", "")
                    level = entry.get("level", "info")
                    color = {"error": "red", "warning": "yellow", "debug": "dim"}.get(
                        level, "white"
                    )
                    output.console.print(
                        f"[dim]{ts}[/] [cyan]{svc:12s}[/] [{color}]{msg}[/]"
                    )
                else:
                    output.console.print(str(entry))
            except json.JSONDecodeError:
                output.console.print(line)
    except KeyboardInterrupt:
        output.info("Stream stopped.")

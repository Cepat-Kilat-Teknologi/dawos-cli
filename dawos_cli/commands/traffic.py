"""Traffic monitoring — live SSE stream, TC queues, rate limits."""

from __future__ import annotations

import json

import typer

from .. import client, output

app = typer.Typer(help="Traffic monitoring and shaper management.")


@app.command("watch")
def watch() -> None:
    """Watch live traffic stream (SSE). Press Ctrl+C to stop."""
    output.info("Streaming live traffic… (Ctrl+C to stop)")
    try:
        for line in client.stream_sse("/api/v1/traffic/stream"):
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    user = data.get("username", "?")
                    down = data.get("download_mbps", 0)
                    up = data.get("upload_mbps", 0)
                    output.console.print(
                        f"  [bold]{user:20s}[/] "
                        f"[green]↓ {down:7.2f}[/] "
                        f"[cyan]↑ {up:7.2f}[/] Mbps"
                    )
                else:
                    output.print_raw(line)
            except json.JSONDecodeError:
                output.print_raw(line)
    except KeyboardInterrupt:
        output.info("Stream stopped.")


@app.command("watch-user")
def watch_user(
    username: str = typer.Argument(..., help="Username to monitor"),
) -> None:
    """Watch live traffic for a specific user (SSE). Press Ctrl+C to stop."""
    output.info(f"Streaming traffic for {username}… (Ctrl+C to stop)")
    try:
        for line in client.stream_sse(f"/api/v1/traffic/stream/{username}"):
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    down = data.get("download_mbps", 0)
                    up = data.get("upload_mbps", 0)
                    output.console.print(
                        f"  [bold]{username:20s}[/] "
                        f"[green]↓ {down:7.2f}[/] "
                        f"[cyan]↑ {up:7.2f}[/] Mbps"
                    )
            except json.JSONDecodeError:
                output.print_raw(line)
    except KeyboardInterrupt:
        output.info("Stream stopped.")


@app.command("queue")
def queue(
    username: str = typer.Argument(..., help="Username to show TC queue for"),
) -> None:
    """Show TC queue (shaper) statistics for a subscriber."""
    data = client.get(f"/api/v1/traffic/queue/{username}")
    output.response(data, title=f"Queue: {username}")


@app.command("ratelimit")
def ratelimit(
    username: str = typer.Argument(..., help="Username"),
    rate: str = typer.Argument(..., help="Rate in up/down format (e.g. 5M/20M)"),
) -> None:
    """Change a subscriber's shaper live (temporary, bypasses RADIUS)."""
    client.post(f"/api/v1/traffic/ratelimit/{username}", json={"rate": rate})
    output.success(f"{username} shaper → {rate}")


@app.command("ratelimit-restore")
def ratelimit_restore(
    username: str = typer.Argument(..., help="Username"),
) -> None:
    """Restore a subscriber's shaper to the RADIUS-assigned value."""
    client.delete(f"/api/v1/traffic/ratelimit/{username}")
    output.success(f"{username} shaper restored")

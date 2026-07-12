"""Conntrack management — config, table size, timeouts, helpers, profiles, flush."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Connection tracking (conntrack) management.")


@app.command("config")
def config_show() -> None:
    """Show conntrack configuration."""
    data = client.get("/api/v1/conntrack/config")
    output.response(data, title="Conntrack Config")


@app.command("table-size")
def table_size(
    size: int = typer.Argument(None, help="New table size (omit to show current)"),
) -> None:
    """Show or set conntrack table size."""
    if size is None:
        data = client.get("/api/v1/conntrack/config")
    else:
        data = client.put("/api/v1/conntrack/table-size", json={"size": size})
        output.success(f"Conntrack table size → {size}")
    output.response(data, title="Conntrack Table Size")


@app.command("timeouts")
def timeouts() -> None:
    """Show conntrack timeout values."""
    data = client.get("/api/v1/conntrack/timeouts")
    output.response(data, title="Conntrack Timeouts")


@app.command("timeout-set")
def timeout_set(
    key: str = typer.Argument(..., help="Timeout key (e.g. tcp_timeout_established)"),
    seconds: int = typer.Argument(..., help="Timeout in seconds"),
) -> None:
    """Set a conntrack timeout value."""
    client.put("/api/v1/conntrack/timeouts", json={"key": key, "seconds": seconds})
    output.success(f"Conntrack timeout: {key} → {seconds}s")


@app.command("helpers")
def helpers() -> None:
    """List conntrack helpers (ALGs)."""
    data = client.get("/api/v1/conntrack/helpers")
    helpers_list = output.unwrap(data, "helpers")
    if isinstance(helpers_list, list):
        output.table(
            helpers_list, ["name", "protocol", "port"], title="Conntrack Helpers"
        )
    else:
        output.response(data)


@app.command("profiles")
def profiles() -> None:
    """List conntrack tuning profiles."""
    data = client.get("/api/v1/conntrack/profiles")
    output.response(data, title="Conntrack Profiles")


@app.command("profile-apply")
def profile_apply(
    name: str = typer.Argument(..., help="Profile name to apply"),
) -> None:
    """Apply a conntrack tuning profile."""
    client.post("/api/v1/conntrack/profiles/apply", json={"name": name})
    output.success(f"Conntrack profile '{name}' applied")


@app.command("flush")
def flush(
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt."
    ),
) -> None:
    """Flush (clear) the entire conntrack table.

    This is a destructive operation — all tracked connections are removed.
    Active connections will need to be re-established by the kernel.
    Requires operator-level API key.
    """
    if not force:
        typer.confirm(
            "This will flush ALL tracked connections. Continue?",
            abort=True,
        )
    data = client.post("/api/v1/conntrack/flush")
    entries = data.get("entries_before", 0) if isinstance(data, dict) else 0
    output.success(f"Conntrack table flushed ({entries} entries cleared)")
    output.response(data, title="Conntrack Flush")

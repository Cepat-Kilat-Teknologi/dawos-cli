"""Bulk operations — batch commands across multiple sessions."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="Bulk operations on multiple subscribers.")


@app.command("terminate")
def terminate(
    usernames: str = typer.Argument(..., help="Comma-separated usernames to terminate"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Terminate multiple subscriber sessions at once."""
    names = [u.strip() for u in usernames.split(",") if u.strip()]
    if not force:
        typer.confirm(f"Terminate {len(names)} session(s)?", abort=True)
    data = client.post("/api/v1/bulk/terminate", json={"usernames": names})
    ok = data.get("succeeded", 0)
    fail = data.get("failed", 0)
    output.success(f"Bulk terminate: {ok} succeeded, {fail} failed")
    results = data.get("results", [])
    if results:
        output.table(results, ["target", "success", "error"], title="Results")


@app.command("ratelimit")
def ratelimit(
    items: str = typer.Argument(
        ..., help="Comma-separated user:rate pairs (e.g. user1:5M/20M,user2:10M/50M)"
    ),
) -> None:
    """Change rate limits for multiple subscribers at once."""
    parsed = []
    for pair in items.split(","):
        pair = pair.strip()
        if ":" not in pair:
            output.error(f"Invalid format: {pair} (expected user:rate)")
            raise typer.Exit(1)
        user, rate = pair.split(":", 1)
        parsed.append({"username": user.strip(), "rate": rate.strip()})
    data = client.post("/api/v1/bulk/ratelimit", json={"items": parsed})
    ok = data.get("succeeded", 0)
    fail = data.get("failed", 0)
    output.success(f"Bulk ratelimit: {ok} succeeded, {fail} failed")
    results = data.get("results", [])
    if results:
        output.table(results, ["target", "success", "error"], title="Results")


@app.command("shaper-restore")
def shaper_restore(
    usernames: str = typer.Argument(..., help="Comma-separated usernames to restore"),
) -> None:
    """Restore RADIUS-assigned shapers for multiple subscribers."""
    names = [u.strip() for u in usernames.split(",") if u.strip()]
    data = client.post("/api/v1/bulk/shaper-restore", json={"usernames": names})
    ok = data.get("succeeded", 0)
    fail = data.get("failed", 0)
    output.success(f"Bulk shaper-restore: {ok} succeeded, {fail} failed")
    results = data.get("results", [])
    if results:
        output.table(results, ["target", "success", "error"], title="Results")

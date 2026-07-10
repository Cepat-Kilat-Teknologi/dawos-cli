"""Node group management and multi-node command execution.

Allows operators to define named groups of BNG profiles and execute
API requests across all nodes in a group simultaneously.

Example workflow::

    dawos node group-add core --profiles bng1 bng2 bng3
    dawos node status core
    dawos node exec core GET /api/v1/sessions
"""

from __future__ import annotations

import json
from typing import List, Optional

import typer
from rich.table import Table

from .. import config, output
from ..multi import execute_multi

app = typer.Typer(help="Multi-node group management and parallel execution.")

_VALID_METHODS = frozenset({"GET", "POST", "PUT", "DELETE", "PATCH"})


# ---------------------------------------------------------------------------
# Group CRUD
# ---------------------------------------------------------------------------


@app.command("group-add")
def group_add(
    name: str = typer.Argument(..., help="Group name (e.g. core, edge, all)."),
    profiles: List[str] = typer.Option(
        ..., "--profiles", "-p", help="Profile names to include in the group."
    ),
) -> None:
    """Create or update a node group with the specified profiles."""
    try:
        config.add_group(name, profiles)
    except ValueError as exc:
        output.error(str(exc))
        raise typer.Exit(1) from exc
    output.success(
        f"Group [bold]{name}[/] saved with {len(profiles)} profile(s): "
        f"{', '.join(profiles)}"
    )


@app.command("group-remove")
def group_remove(
    name: str = typer.Argument(..., help="Group name to remove."),
) -> None:
    """Remove a node group."""
    if config.remove_group(name):
        output.success(f"Group [bold]{name}[/] removed.")
    else:
        output.error(f"Group [bold]{name}[/] not found.")
        raise typer.Exit(1)


@app.command("group-list")
def group_list() -> None:
    """List all node groups and their members."""
    groups = config.list_groups()
    if not groups:
        output.warning(
            "No groups configured. Run [bold]dawos node group-add[/] to create one."
        )
        return

    t = Table(title="Node Groups", expand=False)
    t.add_column("Group", style="bold")
    t.add_column("Profiles", style="cyan")
    t.add_column("Count", justify="right")

    for name, profiles in groups.items():
        t.add_row(name, ", ".join(profiles), str(len(profiles)))

    output.console.print(t)


# ---------------------------------------------------------------------------
# Multi-node execution
# ---------------------------------------------------------------------------


@app.command("status")
def status(
    group: str = typer.Argument(..., help="Group name to check."),
    timeout: float = typer.Option(
        10.0, "--timeout", "-t", help="Per-node timeout in seconds."
    ),
) -> None:
    """Check health status of all nodes in a group."""
    profiles = config.get_group(group)
    if profiles is None:
        output.error(f"Group [bold]{group}[/] not found.")
        raise typer.Exit(1)

    if not profiles:
        output.warning(f"Group [bold]{group}[/] has no profiles.")
        return

    output.info(f"Checking {len(profiles)} node(s) in group [bold]{group}[/] ...")

    result = execute_multi(profiles, "GET", "/health", timeout=timeout)

    t = Table(title=f"Node Status — {group}", expand=False)
    t.add_column("Profile", style="bold")
    t.add_column("URL", style="cyan")
    t.add_column("Status")
    t.add_column("Version")
    t.add_column("Node Name")

    for nr in sorted(result.results, key=lambda r: r.profile):
        if nr.success and isinstance(nr.data, dict):
            status_str = "[green]healthy[/]"
            version = nr.data.get("version", "—")
            node_name = nr.data.get("node_name", "—")
        else:
            status_str = (
                f"[red]error[/] {nr.error[:40]}" if nr.error else "[red]down[/]"
            )
            version = "—"
            node_name = "—"
        t.add_row(nr.profile, nr.url, status_str, str(version), str(node_name))

    output.console.print(t)
    output.info(
        f"Total: {result.total}  "
        f"Healthy: [green]{result.succeeded}[/]  "
        f"Failed: [red]{result.failed}[/]"
    )


@app.command("exec")
def exec_cmd(
    group: str = typer.Argument(..., help="Group name to execute against."),
    method: str = typer.Argument(..., help="HTTP method (GET, POST, PUT, DELETE)."),
    path: str = typer.Argument(..., help="API path (e.g. /api/v1/sessions)."),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="JSON request body."),
    timeout: float = typer.Option(
        30.0, "--timeout", "-t", help="Per-node timeout in seconds."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Execute an API request across all nodes in a group.

    Results are displayed per-node with success/failure status.
    """
    profiles = config.get_group(group)
    if profiles is None:
        output.error(f"Group [bold]{group}[/] not found.")
        raise typer.Exit(1)

    if not profiles:
        output.warning(f"Group [bold]{group}[/] has no profiles.")
        return

    # Parse optional JSON body.
    json_body = None
    if body:
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError as exc:
            output.error(f"Invalid JSON body: {exc}")
            raise typer.Exit(1) from exc

    http_method = method.upper()
    if http_method not in _VALID_METHODS:
        output.error(
            f"Invalid HTTP method: {method}. "
            f"Choose from: {', '.join(sorted(_VALID_METHODS))}"
        )
        raise typer.Exit(1)

    # Writes across a whole node group are destructive — confirm first.
    if http_method != "GET" and not force:
        typer.confirm(
            f"Run {http_method} {path} on {len(profiles)} node(s)?", abort=True
        )

    output.info(
        f"Executing [bold]{http_method} {path}[/] "
        f"on {len(profiles)} node(s) in group [bold]{group}[/] ..."
    )

    result = execute_multi(
        profiles,
        http_method,
        path,
        json_body=json_body,
        timeout=timeout,
    )

    t = Table(title=f"Results — {http_method} {path}", expand=False)
    t.add_column("Profile", style="bold")
    t.add_column("Status")
    t.add_column("Response / Error")

    for nr in sorted(result.results, key=lambda r: r.profile):
        if nr.success:
            status_str = f"[green]{nr.status_code}[/]"
            resp_text = json.dumps(nr.data, default=str)
            if len(resp_text) > 80:
                resp_text = resp_text[:77] + "..."
        else:
            status_str = f"[red]{nr.status_code or 'ERR'}[/]"
            resp_text = nr.error[:80] if nr.error else "Unknown error"
        t.add_row(nr.profile, status_str, resp_text)

    output.console.print(t)
    output.info(
        f"Total: {result.total}  "
        f"Succeeded: [green]{result.succeeded}[/]  "
        f"Failed: [red]{result.failed}[/]"
    )

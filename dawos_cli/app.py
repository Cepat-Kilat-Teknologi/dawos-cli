"""dawos — main CLI entry point.

Mounts all command groups, handles global options (--profile, --json, --verbose),
and populates shared state before any sub-command runs.
"""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__, config, state

# ---------------------------------------------------------------------------
# ASCII art logo
# ---------------------------------------------------------------------------

_LOGO = r"""
     _
  __| | __ ___      _____  ___
 / _` |/ _` \ \ /\ / / _ \/ __|
| (_| | (_| |\ V  V / (_) \__ \
 \__,_|\__,_| \_/\_/ \___/|___/
"""

# ---------------------------------------------------------------------------
# Root app
# ---------------------------------------------------------------------------

_VALID_FORMATS = ("table", "json", "csv", "yaml")

app = typer.Typer(
    name="dawos",
    help=(
        "[bold cyan]dawos[/] — remote CLI for dawos-agent BNG management.\n\n"
        "Manage PPPoE sessions, firewall, routing, traffic shaping, and more "
        "on remote accel-ppp nodes via the dawos-agent REST API."
    ),
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Version callback
# ---------------------------------------------------------------------------


def _stdout_is_tty() -> bool:
    """Return True when stdout is attached to an interactive terminal."""
    return sys.stdout.isatty()


def _version_callback(value: bool) -> None:
    if value:
        out = Console()
        out.print(f"[cyan]{_LOGO.rstrip()}[/]")
        out.print(f"  [bold cyan]dawos-cli[/] {__version__}")
        out.print("  [dim]Remote CLI for dawos-agent BNG management[/]\n")
        raise typer.Exit()


# ---------------------------------------------------------------------------
# Global callback — runs before every sub-command
# ---------------------------------------------------------------------------


@app.callback()
def main_callback(
    profile: Optional[str] = typer.Option(  # pylint: disable=redefined-outer-name
        None,
        "--profile",
        "-p",
        help="Profile name to use (overrides active profile).",
        envvar="DAWOS_PROFILE",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output raw JSON (for scripting / piping).",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-F",
        help="Output format: table, json, csv, yaml.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output (show request URLs, timing).",
    ),
    timeout: float = typer.Option(
        30.0,
        "--timeout",
        "-t",
        help="Request timeout in seconds.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Populate shared state from the selected profile."""
    # Validate --format
    if output_format and output_format not in _VALID_FORMATS:
        console.print(
            f"[red]Invalid format:[/] '{output_format}'. "
            f"Choose from: {', '.join(_VALID_FORMATS)}"
        )
        raise typer.Exit(1)

    # Resolve profile name
    name = profile or config.get_active_name()
    prof = config.get_profile(name) if name else None

    s = state.current
    s.json_output = json_output
    s.verbose = verbose
    s.timeout = timeout

    # --json is a shortcut for --format json
    if json_output:
        s.output_format = "json"
    elif output_format:
        s.output_format = output_format

    if prof:
        s.profile_name = name or ""
        s.base_url = prof["url"]
        s.api_key = prof.get("api_key", "")
    # else: state stays empty — commands that need a profile will error in client.py

    # Non-blocking update check (cached, runs at most once per day).
    # Skipped when stdout is not a TTY (pipes, scripts, CI).
    if _stdout_is_tty():
        try:
            from . import updater  # pylint: disable=import-outside-toplevel

            latest = updater.check_for_update()
            if latest:
                console.print(
                    f"[yellow]Update available:[/] {__version__} → [bold]{latest}[/] "
                    f"— run [bold cyan]dawos update[/] to upgrade"
                )
        except Exception:  # pylint: disable=broad-exception-caught
            pass  # Never let update check break the CLI


# ---------------------------------------------------------------------------
# Mount sub-command groups
# ---------------------------------------------------------------------------

from .commands import (  # noqa: E402  # pylint: disable=wrong-import-position
    audit,
    bulk,
    config_cmd,
    conntrack,
    dhcp,
    diagnostics,
    dns,
    events,
    firewall,
    flow,
    limits,
    lldp,
    logs,
    monitoring,
    nat,
    network,
    node,
    ntp,
    playbook,
    pool,
    pppoe,
    profile,
    routing,
    scheduler,
    service,
    sessions,
    system,
    traffic,
    vrrp,
    wizard,
    zone,
)

app.add_typer(profile.app, name="profile", help="Manage connection profiles.")
app.add_typer(system.app, name="system", help="System info and health.")
app.add_typer(
    service.app, name="service", help="BNG service control (start/stop/restart)."
)
app.add_typer(sessions.app, name="session", help="PPPoE session management.")
app.add_typer(config_cmd.app, name="config", help="BNG configuration management.")
app.add_typer(network.app, name="network", help="Network interfaces, routes, VLANs.")
app.add_typer(firewall.app, name="firewall", help="Firewall rules and SNMP.")
app.add_typer(nat.app, name="nat", help="NAT / masquerade / egress management.")
app.add_typer(
    pppoe.app, name="pppoe", help="PPPoE interface and MAC filter management."
)
app.add_typer(traffic.app, name="traffic", help="Live traffic monitoring and shaping.")
app.add_typer(routing.app, name="routing", help="Dynamic routing (BGP/OSPF/RIP/BFD).")
app.add_typer(pool.app, name="pool", help="IP address pool management.")
app.add_typer(conntrack.app, name="conntrack", help="Connection tracking management.")
app.add_typer(events.app, name="events", help="Event hooks and webhooks.")
app.add_typer(scheduler.app, name="scheduler", help="Scheduled job management.")
app.add_typer(dns.app, name="dns", help="DNS forwarding management.")
app.add_typer(dhcp.app, name="dhcp", help="DHCP server and relay.")
app.add_typer(ntp.app, name="ntp", help="NTP time synchronisation.")
app.add_typer(lldp.app, name="lldp", help="LLDP link-layer discovery.")
app.add_typer(vrrp.app, name="vrrp", help="VRRP high-availability.")
app.add_typer(flow.app, name="flow", help="Flow accounting (NetFlow/sFlow).")
app.add_typer(monitoring.app, name="monitoring", help="Monitoring and metrics.")
app.add_typer(limits.app, name="limits", help="Connection limits.")
app.add_typer(zone.app, name="zone", help="Zone-based firewall.")
app.add_typer(diagnostics.app, name="diagnostics", help="System diagnostics.")
app.add_typer(logs.app, name="logs", help="Log viewing and streaming.")
app.add_typer(node.app, name="node", help="Multi-node group management and execution.")
app.add_typer(wizard.app, name="wizard", help="Guided interactive workflows.")
app.add_typer(audit.app, name="audit", help="Audit log viewer.")
app.add_typer(bulk.app, name="bulk", help="Bulk operations on multiple subscribers.")
app.add_typer(playbook.app, name="playbook", help="Operational playbooks (automation).")

# ---------------------------------------------------------------------------
# Short aliases (hidden duplicates for power users)
# ---------------------------------------------------------------------------

app.add_typer(sessions.app, name="s", hidden=True)
app.add_typer(system.app, name="sys", hidden=True)
app.add_typer(config_cmd.app, name="cfg", hidden=True)
app.add_typer(network.app, name="net", hidden=True)
app.add_typer(firewall.app, name="fw", hidden=True)
app.add_typer(routing.app, name="rt", hidden=True)
app.add_typer(monitoring.app, name="mon", hidden=True)
app.add_typer(diagnostics.app, name="diag", hidden=True)

from . import dashboard  # noqa: E402  # pylint: disable=wrong-import-position

# ---------------------------------------------------------------------------
# Standalone top-level commands
# ---------------------------------------------------------------------------


@app.command("top")
def top_cmd(
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Refresh interval in seconds."
    ),
) -> None:
    """Launch the live monitoring dashboard (full-screen)."""
    dashboard.run_dashboard(interval=interval)


@app.command("version")
def version_cmd() -> None:
    """Show version information."""
    out = Console()
    out.print(f"[cyan]{_LOGO.rstrip()}[/]")
    out.print(
        Panel(
            f"[bold cyan]dawos-cli[/] {__version__}\n"
            f"[dim]Remote CLI for dawos-agent BNG management[/]",
            border_style="cyan",
        )
    )


@app.command("status")
def quick_status() -> None:
    """Quick connection + service status (shortcut for system health)."""
    from . import client, output  # pylint: disable=import-outside-toplevel

    try:
        data = client.get("/health")
        output.success(
            f"Connected to [bold]{state.current.profile_name}[/] "
            f"({state.current.base_url})"
        )
        output.response(data, title="Health")
    except SystemExit as exc:
        # client already printed the error — propagate a failure exit code
        # without duplicating the message.
        raise typer.Exit(1) from exc


@app.command("help", hidden=True)
def help_cmd(ctx: typer.Context = typer.Context) -> None:
    """Show help message (alias for --help)."""
    click_ctx = ctx.parent or ctx
    Console().print(click_ctx.get_help())
    raise typer.Exit()


@app.command("update")
def update_cmd(
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt."
    ),
) -> None:
    """Check for updates and upgrade dawos-cli."""
    _run_update(force=force)


@app.command("self-update", hidden=True)
def self_update_cmd() -> None:
    """Update dawos-cli to the latest version (alias for update)."""
    _run_update(force=False)


def _run_update(*, force: bool = False) -> None:
    """Shared update logic for update and self-update commands."""
    from . import updater  # pylint: disable=import-outside-toplevel

    out = Console()
    out.print(f"[dim]Current version:[/] {__version__}")
    out.print("[cyan]Checking for updates...[/]")

    latest = updater.fetch_latest_tag()
    if not latest:
        out.print("[yellow]Could not reach GitHub. Check your connection.[/]")
        raise typer.Exit(1)

    if updater.parse_version(latest) <= updater.parse_version(__version__):
        out.print(f"[green]✓ Already up-to-date ({__version__}).[/]")
        raise typer.Exit()

    out.print(f"[yellow]New version available:[/] {__version__} → [bold]{latest}[/]")

    if not force:
        confirm = typer.confirm("Do you want to update?")
        if not confirm:
            out.print("[dim]Update skipped.[/]")
            raise typer.Exit()

    out.print("[cyan]Updating...[/]")
    if updater.run_self_update(latest):
        out.print(f"[bold green]✓ Updated to {latest}![/] Restart your terminal.")
    else:
        out.print(
            "[red]Update failed.[/] Try manually:\n"
            f"  [dim]pipx install --force dawos-cli=={latest.lstrip('v')}[/]"
        )


@app.command("doctor")
def doctor_cmd() -> None:
    """Run system diagnostics — check environment, connectivity, and config."""
    from . import doctor  # pylint: disable=import-outside-toplevel

    doctor.run_doctor()


@app.command("shell")
def shell_cmd() -> None:
    """Launch interactive REPL shell with auto-complete."""
    from . import shell  # pylint: disable=import-outside-toplevel

    shell.run_shell()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Console script entry point."""
    app()

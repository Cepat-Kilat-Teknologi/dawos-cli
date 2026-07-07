"""dawos — main CLI entry point.

Mounts all command groups, handles global options (--profile, --json, --verbose),
and populates shared state before any sub-command runs.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__, config, state

# ---------------------------------------------------------------------------
# Root app
# ---------------------------------------------------------------------------

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


def _version_callback(value: bool) -> None:
    if value:
        Console().print(f"dawos-cli [bold cyan]{__version__}[/]")
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
    # Resolve profile name
    name = profile or config.get_active_name()
    prof = config.get_profile(name) if name else None

    s = state.current
    s.json_output = json_output
    s.verbose = verbose
    s.timeout = timeout

    if prof:
        s.profile_name = name or ""
        s.base_url = prof["url"]
        s.api_key = prof.get("api_key", "")
    # else: state stays empty — commands that need a profile will error in client.py


# ---------------------------------------------------------------------------
# Mount sub-command groups
# ---------------------------------------------------------------------------

from .commands import (  # noqa: E402  # pylint: disable=wrong-import-position
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
    ntp,
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
    Console().print(
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
    except SystemExit:
        pass  # client already printed the error


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Console script entry point."""
    app()

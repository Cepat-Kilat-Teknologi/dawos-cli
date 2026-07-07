"""dawos top — Rich Live dashboard for real-time BNG monitoring.

Shows a live-updating overview: session stats, resource usage, and recent
sessions in a single terminal view. Refreshes from the dawos-agent API.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

import typer
from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import client, state

console = Console()


def _build_stat_panel(stats: Dict[str, Any]) -> Panel:
    """Build the session statistics panel (top-left)."""
    t = Table(show_header=False, expand=True, pad_edge=True, box=None)
    t.add_column("Key", style="bold cyan", ratio=1)
    t.add_column("Value", ratio=1)

    active = stats.get("active_sessions", stats.get("sessions", "?"))
    t.add_row("Active Sessions", f"[bold green]{active}[/]")

    for key in ("starting", "active", "finishing"):
        val = stats.get(key, "—")
        t.add_row(key.title(), str(val))

    uptime = stats.get("uptime", stats.get("uptime_seconds", "—"))
    t.add_row("Uptime", str(uptime))

    for key in ("total_sessions", "total_bytes_in", "total_bytes_out"):
        val = stats.get(key)
        if val is not None:
            label = key.replace("_", " ").title()
            if "bytes" in key:
                val = _fmt_bytes(int(val))
            t.add_row(label, str(val))

    return Panel(t, title="[bold]Session Stats[/]", border_style="cyan", expand=True)


def _build_resource_panel(resources: Dict[str, Any]) -> Panel:
    """Build the system resource panel (top-right)."""
    t = Table(show_header=False, expand=True, pad_edge=True, box=None)
    t.add_column("Key", style="bold yellow", ratio=1)
    t.add_column("Value", ratio=1)

    # CPU
    cpu = resources.get("cpu", {})
    if isinstance(cpu, dict):
        usage = cpu.get("usage_percent", cpu.get("percent", "?"))
        cores = cpu.get("cores", "?")
        t.add_row("CPU Usage", f"[bold]{usage}%[/]")
        t.add_row("CPU Cores", str(cores))
    elif cpu:
        t.add_row("CPU", str(cpu))

    # Memory
    mem = resources.get("memory", {})
    if isinstance(mem, dict):
        used = mem.get("used_percent", mem.get("percent", "?"))
        total = mem.get("total", "")
        t.add_row(
            "Memory",
            f"[bold]{used}%[/]" + (f" of {_fmt_bytes(total)}" if total else ""),
        )
    elif mem:
        t.add_row("Memory", str(mem))

    # Disk
    disk = resources.get("disk", {})
    if isinstance(disk, dict):
        used = disk.get("used_percent", disk.get("percent", "?"))
        t.add_row("Disk", f"{used}%")

    # Load
    load = resources.get("load_average", resources.get("load", None))
    if load:
        if isinstance(load, list):
            t.add_row("Load", " / ".join(str(x) for x in load))
        else:
            t.add_row("Load", str(load))

    return Panel(t, title="[bold]Resources[/]", border_style="yellow", expand=True)


def _build_sessions_table(sessions: List[Dict[str, Any]]) -> Panel:
    """Build the recent sessions table (bottom)."""
    t = Table(expand=True, pad_edge=True)
    t.add_column("#", style="dim", width=4)
    t.add_column("Username", style="bold", min_width=15)
    t.add_column("IP Address", style="cyan", min_width=13)
    t.add_column("MAC", style="dim", min_width=17)
    t.add_column("Interface", min_width=8)
    t.add_column("Uptime", min_width=8)
    t.add_column("↓ RX", justify="right", min_width=8)
    t.add_column("↑ TX", justify="right", min_width=8)
    t.add_column("Rate", min_width=10)

    for i, s in enumerate(sessions[:25], 1):
        t.add_row(
            str(i),
            str(s.get("username", "?")),
            str(s.get("ip", s.get("ip_address", "—"))),
            str(s.get("mac", s.get("calling_station_id", "—"))),
            str(s.get("interface", s.get("ifname", "—"))),
            str(s.get("uptime", "—")),
            _fmt_bytes(s.get("rx_bytes", s.get("bytes_in", 0))),
            _fmt_bytes(s.get("tx_bytes", s.get("bytes_out", 0))),
            str(s.get("rate_limit", s.get("rate", "—"))),
        )

    if not sessions:
        t.add_row("—", "No active sessions", "—", "—", "—", "—", "—", "—", "—")

    return Panel(t, title="[bold]Active Sessions[/]", border_style="green", expand=True)


def _build_header(profile: str, url: str) -> Text:
    """Build the header bar."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = Text()
    header.append(" DAWOS ", style="bold white on blue")
    header.append(f"  {profile}", style="bold cyan")
    header.append(f"  ({url})", style="dim")
    header.append(f"  {now}", style="dim")
    header.append("  [q/Ctrl+C to quit]", style="dim italic")
    return header


def _fmt_bytes(val: Any) -> str:
    """Format bytes to human-readable."""
    if val is None or val == "—" or val == "":
        return "—"
    try:
        n = int(val)
    except (ValueError, TypeError):
        return str(val)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _fetch_safe(path: str) -> Dict[str, Any]:
    """Fetch API data, return empty dict on error."""
    try:
        result = client.get(path)
        return result if isinstance(result, dict) else {}
    except (SystemExit, Exception):  # pylint: disable=broad-exception-caught
        return {}


def _fetch_sessions_safe() -> List[Dict[str, Any]]:
    """Fetch session list, return empty list on error."""
    try:
        result = client.get("/api/v1/sessions")
        if isinstance(result, dict):
            return result.get("sessions", [])
        if isinstance(result, list):
            return result
    except (SystemExit, Exception):  # pylint: disable=broad-exception-caught
        pass
    return []


def run_dashboard(interval: float = 2.0) -> None:
    """Run the live dashboard loop."""
    profile_name = state.current.profile_name or "default"
    url = state.current.base_url

    with Live(console=console, refresh_per_second=1, screen=True) as live:
        try:
            while True:
                # Fetch data
                stats = _fetch_safe("/api/v1/sessions/stats")
                resources = _fetch_safe("/api/v1/system/metrics")
                sessions = _fetch_sessions_safe()

                # Build layout
                header = _build_header(profile_name, url)
                top_row = Columns(
                    [_build_stat_panel(stats), _build_resource_panel(resources)],
                    equal=True,
                    expand=True,
                )
                bottom = _build_sessions_table(sessions)

                layout = Group(header, "", top_row, "", bottom)
                live.update(layout)

                time.sleep(interval)
        except KeyboardInterrupt:
            pass


# Typer command (mounted in app.py)
app = typer.Typer(help="Live monitoring dashboard.")


@app.command("top")
def top_cmd(
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Refresh interval in seconds."
    ),
) -> None:
    """Launch the live monitoring dashboard.

    Shows real-time session stats, system resources, and active sessions
    in a full-screen terminal view. Press Ctrl+C to exit.
    """
    run_dashboard(interval=interval)

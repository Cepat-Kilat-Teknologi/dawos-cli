"""Rich output helpers — tables, panels, JSON, status messages.

Every command delegates formatting here so the --json flag works consistently
and the visual style is uniform across all commands.
"""

from __future__ import annotations

import json as _json
from typing import Any, Dict, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import state

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def print_json(data: Any) -> None:
    """Print raw JSON (for --json mode or explicit JSON output)."""
    console.print_json(_json.dumps(data, indent=2, default=str))


def print_raw(text: str) -> None:
    """Print plain text."""
    console.print(text)


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/] {message}")


def warning(message: str) -> None:
    """Print a warning."""
    console.print(f"[bold yellow]⚠[/] {message}")


def error(message: str) -> None:
    """Print an error."""
    err_console.print(f"[bold red]✗[/] {message}")


def info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[dim]ℹ[/] {message}")


# ---------------------------------------------------------------------------
# Structured output
# ---------------------------------------------------------------------------


def table(
    rows: Sequence[Dict[str, Any]],
    columns: Sequence[str],
    *,
    title: str = "",
    col_labels: Optional[Dict[str, str]] = None,
    col_styles: Optional[Dict[str, str]] = None,
) -> None:
    """Render a Rich table from a list of dicts.

    If --json is active, prints raw JSON instead.
    """
    if state.current.json_output:
        print_json(rows)
        return

    labels = col_labels or {}
    styles = col_styles or {}
    t = Table(title=title, show_lines=False, pad_edge=True, expand=False)
    for col in columns:
        t.add_column(
            labels.get(col, col.replace("_", " ").title()), style=styles.get(col, "")
        )
    for row in rows:
        t.add_row(*[str(row.get(col, "—")) for col in columns])
    if not rows:
        t.add_row(*["—" for _ in columns])
    console.print(t)


def detail(data: Dict[str, Any], *, title: str = "") -> None:
    """Render a key-value panel for a single resource.

    If --json is active, prints raw JSON instead.
    """
    if state.current.json_output:
        print_json(data)
        return

    lines = []
    for key, value in data.items():
        label = key.replace("_", " ").title()
        lines.append(f"[bold]{label}:[/] {value}")
    panel_text = "\n".join(lines)
    console.print(Panel(panel_text, title=title, border_style="cyan", expand=False))


def kvtable(data: Dict[str, Any], *, title: str = "") -> None:
    """Render a two-column key→value table.

    If --json is active, prints raw JSON instead.
    """
    if state.current.json_output:
        print_json(data)
        return

    t = Table(title=title, show_header=False, expand=False, pad_edge=True)
    t.add_column("Key", style="bold cyan", min_width=20)
    t.add_column("Value")
    for key, value in data.items():
        label = key.replace("_", " ").title()
        t.add_row(label, str(value))
    console.print(t)


def response(data: Any, *, title: str = "") -> None:
    """Auto-detect output type: dict → kvtable, list → table, else raw."""
    if state.current.json_output:
        print_json(data)
        return

    if isinstance(data, dict):
        kvtable(data, title=title)
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        columns = list(data[0].keys())
        table(data, columns, title=title)
    else:
        console.print(data)

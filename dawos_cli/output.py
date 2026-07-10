"""Rich output helpers — tables, panels, JSON, CSV, YAML, status messages.

Every command delegates formatting here so the --json / --format flag works
consistently and the visual style is uniform across all commands.
"""

from __future__ import annotations

import csv as _csv
import io
import json as _json
import sys
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from . import state

console = Console()
err_console = Console(stderr=True)

_UNWRAP_DEFAULT = object()


def unwrap(data: Any, key: str, default: Any = _UNWRAP_DEFAULT) -> Any:
    """Extract a value from a possibly-wrapped API response.

    Agent endpoints return either a wrapped dict (``{"sessions": [...]}``)
    or the bare payload.  Returns ``data[key]`` when ``data`` is a dict
    containing ``key``; otherwise returns ``default`` — which itself
    defaults to ``data`` unchanged (the common list-unwrap case).

    Args:
        data: The decoded response (a dict, or an already-unwrapped value).
        key: The wrapper key to extract.
        default: Fallback when ``data`` is not a dict or lacks ``key``;
            defaults to ``data`` itself.

    Returns:
        The unwrapped value.
    """
    fallback = data if default is _UNWRAP_DEFAULT else default
    if isinstance(data, dict):
        return data.get(key, fallback)
    return fallback


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------


def _is_alt_format() -> bool:
    """Return True if output should bypass Rich (json/csv/yaml)."""
    s = state.current
    return s.json_output or s.output_format in ("json", "csv", "yaml")


def _print_csv(rows: Sequence[Dict[str, Any]], columns: Sequence[str]) -> None:
    """Write CSV to stdout (bypasses Rich)."""
    buf = io.StringIO()
    writer = _csv.DictWriter(buf, fieldnames=list(columns), extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {k: str(row.get(k, row.get(k.replace("_", "-"), ""))) for k in columns}
        )
    sys.stdout.write(buf.getvalue())


def _print_yaml(data: Any) -> None:
    """Print YAML to stdout. Falls back to JSON if PyYAML is not installed."""
    try:
        import yaml  # pylint: disable=import-outside-toplevel

        sys.stdout.write(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    except ImportError:
        err_console.print(
            "[yellow]PyYAML not installed. Install with:[/] "
            "[bold]pip install pyyaml[/]\n"
            "[dim]Falling back to JSON output.[/]"
        )
        print(_json.dumps(data, indent=2, default=str))


def _emit(
    data: Any,
    columns: Optional[Sequence[str]] = None,
) -> bool:
    """Handle json/csv/yaml output. Returns True if handled, False otherwise."""
    s = state.current
    fmt = "json" if s.json_output else s.output_format

    if fmt == "json":
        console.print_json(_json.dumps(data, indent=2, default=str))
        return True

    if fmt == "csv":
        rows: List[Dict[str, Any]] = []
        cols = columns or []
        if isinstance(data, list) and data:
            rows = data
            if not cols and isinstance(data[0], dict):
                cols = list(data[0].keys())
        elif isinstance(data, dict):
            rows = [data]
            if not cols:
                cols = list(data.keys())
        if rows and cols:
            _print_csv(rows, cols)
        else:
            console.print_json(_json.dumps(data, indent=2, default=str))
        return True

    if fmt == "yaml":
        _print_yaml(data)
        return True

    return False


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def print_json(data: Any) -> None:
    """Print raw JSON (for --json mode or explicit JSON output)."""
    console.print_json(_json.dumps(data, indent=2, default=str))


def print_raw(text: str) -> None:
    """Print plain text (markup disabled to preserve brackets)."""
    console.print(text, markup=False, highlight=False)


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


_LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "::1")


def warn_if_insecure_url(url: str) -> None:
    """Warn when a plain-HTTP URL would send the API key unencrypted.

    Loopback hosts (localhost / 127.0.0.1 / ::1) are exempt because the
    traffic never leaves the machine.
    """
    parsed = urlparse(url)
    if parsed.scheme != "http":
        return
    host = (parsed.hostname or "").lower()
    if host in _LOOPBACK_HOSTS:
        return
    warning(
        f"[bold]{escape(url)}[/] uses plain HTTP — the API key is sent "
        "unencrypted. Prefer HTTPS for non-local agents."
    )


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

    If --json/--format is active, outputs in the requested format instead.
    """
    if _emit(rows, columns):
        return

    labels = col_labels or {}
    styles = col_styles or {}
    t = Table(title=title, show_lines=False, pad_edge=True, expand=False)
    for col in columns:
        t.add_column(
            labels.get(col, col.replace("_", " ").title()), style=styles.get(col, "")
        )
    for row in rows:
        t.add_row(
            *[
                escape(str(row.get(col, row.get(col.replace("_", "-"), "—"))))
                for col in columns
            ]
        )
    if not rows:
        t.add_row(*["—" for _ in columns])
    console.print(t)


def detail(data: Dict[str, Any], *, title: str = "") -> None:
    """Render a key-value panel for a single resource.

    If --json/--format is active, outputs in the requested format instead.
    """
    if _emit(data):
        return

    lines = []
    for key, value in data.items():
        label = escape(key.replace("_", " ").title())
        lines.append(f"[bold]{label}:[/] {escape(str(value))}")
    panel_text = "\n".join(lines)
    console.print(Panel(panel_text, title=title, border_style="cyan", expand=False))


def kvtable(data: Dict[str, Any], *, title: str = "") -> None:
    """Render a two-column key→value table.

    If --json/--format is active, outputs in the requested format instead.
    """
    if _emit(data):
        return

    t = Table(title=title, show_header=False, expand=False, pad_edge=True)
    t.add_column("Key", style="bold cyan", min_width=20)
    t.add_column("Value")
    for key, value in data.items():
        label = escape(key.replace("_", " ").title())
        t.add_row(label, escape(str(value)))
    console.print(t)


def response(data: Any, *, title: str = "") -> None:
    """Auto-detect output type: dict → kvtable, list → table, else raw."""
    if _emit(data):
        return

    if isinstance(data, dict):
        kvtable(data, title=title)
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        columns = list(data[0].keys())
        table(data, columns, title=title)
    else:
        console.print(data)

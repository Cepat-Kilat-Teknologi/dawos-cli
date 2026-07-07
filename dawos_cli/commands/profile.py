"""Profile management — add, list, remove, use, export, import profiles."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from .. import client, config, output

app = typer.Typer(help="Manage connection profiles for BNG nodes.")


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Profile name (e.g. bng1, prod, staging)"),
    url: str = typer.Option(
        ..., "--url", "-u", help="Agent URL (e.g. http://192.168.1.1:8470)"
    ),
    key: str = typer.Option(..., "--key", "-k", help="API key for X-API-Key header"),
    display_name: str = typer.Option(
        "", "--name", "-n", help="Human-readable node name"
    ),
    check: bool = typer.Option(True, help="Verify connectivity before saving"),
) -> None:
    """Add or update a connection profile."""
    if check:
        output.info(f"Checking connectivity to {url} ...")
        health = client.health(url)
        if health is None:
            output.error(
                f"Cannot reach {url}/health — use --no-check to skip verification."
            )
            raise typer.Exit(1)
        node = health.get("node_name", "unknown")
        ver = health.get("version", "?")
        output.success(f"Connected — node=[cyan]{node}[/] version=[cyan]{ver}[/]")
        if not display_name:
            display_name = node

    config.add_profile(name, url, key, display_name)
    output.success(f"Profile [bold]{name}[/] saved.")


@app.command("list")
def list_profiles() -> None:
    """List all saved profiles."""
    profiles = config.list_profiles()
    active = config.get_active_name()
    if not profiles:
        output.warning(
            "No profiles configured. Run [bold]dawos profile add[/] to get started."
        )
        return

    t = Table(title="Profiles", expand=False)
    t.add_column("", width=2)
    t.add_column("Name", style="bold")
    t.add_column("URL", style="cyan")
    t.add_column("Display Name")
    t.add_column("API Key", style="dim")

    for name, prof in profiles.items():
        marker = "[green]●[/]" if name == active else " "
        masked_key = prof.get("api_key", "")[:8] + "…" if prof.get("api_key") else "—"
        t.add_row(
            marker, name, prof.get("url", ""), prof.get("display_name", ""), masked_key
        )
    output.console.print(t)
    output.info(f"Active: [bold]{active}[/]  Config: [dim]{config.config_path()}[/]")


@app.command("remove")
def remove(
    name: str = typer.Argument(..., help="Profile name to remove"),
) -> None:
    """Remove a saved profile."""
    if config.remove_profile(name):
        output.success(f"Profile [bold]{name}[/] removed.")
    else:
        output.error(f"Profile [bold]{name}[/] not found.")
        raise typer.Exit(1)


@app.command("use")
def use(
    name: str = typer.Argument(..., help="Profile name to activate"),
) -> None:
    """Set the active profile."""
    if config.use_profile(name):
        output.success(f"Active profile set to [bold]{name}[/].")
    else:
        output.error(f"Profile [bold]{name}[/] not found.")
        raise typer.Exit(1)


@app.command("test")
def test(
    name: Optional[str] = typer.Argument(
        None, help="Profile to test (default: active)"
    ),
) -> None:
    """Test connectivity to a profile's agent."""
    prof = config.get_profile(name)
    if prof is None:
        label = name or "(active)"
        output.error(f"Profile [bold]{label}[/] not found.")
        raise typer.Exit(1)

    url = prof["url"]
    output.info(f"Testing {url} ...")
    health = client.health(url)
    if health is None:
        output.error(f"Cannot reach {url}/health")
        raise typer.Exit(1)

    output.success("Connection OK")
    output.kvtable(health, title="Health")


@app.command("export")
def export_profiles(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Export a single profile (default: all)."
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Write to file instead of stdout."
    ),
) -> None:
    """Export profiles to JSON (for backup or sharing)."""
    data = config.export_profiles(name)
    if not data.get("profiles"):
        label = name or "any"
        output.error(f"No profile found: {label}")
        raise typer.Exit(1)

    payload = json.dumps(data, indent=2) + "\n"
    if file:
        file.write_text(payload, encoding="utf-8")
        output.success(
            f"Exported {len(data['profiles'])} profile(s) to [bold]{file}[/]"
        )
    else:
        sys.stdout.write(payload)


@app.command("import")
def import_profiles(
    file: Path = typer.Argument(..., help="JSON file to import."),
    replace: bool = typer.Option(
        False, "--replace", help="Replace all profiles instead of merging."
    ),
) -> None:
    """Import profiles from a JSON file."""
    if not file.exists():
        output.error(f"File not found: {file}")
        raise typer.Exit(1)

    try:
        payload = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        output.error(f"Invalid JSON: {exc}")
        raise typer.Exit(1) from exc

    count = config.import_profiles(payload, merge=not replace)
    if count:
        output.success(f"Imported {count} profile(s) from [bold]{file}[/]")
    else:
        output.warning("No profiles found in the import file.")

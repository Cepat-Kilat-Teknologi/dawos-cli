"""System diagnostics — dawos doctor.

Performs a comprehensive health check of the dawos-cli environment:
  - Python version
  - dawos-cli version & update status
  - Active profile & connectivity
  - Shell completion status
  - Config file location
"""

from __future__ import annotations

import os
import shutil
import sys

from rich.console import Console

from . import __version__, config, updater

_console = Console()


def _check(label: str, ok: bool, detail: str) -> None:
    """Print a single check result."""
    icon = "[bold green]✓[/]" if ok else "[bold red]✗[/]"
    _console.print(f"  {icon} {label}: {detail}")


def _check_python() -> None:
    """Check Python version."""
    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    _check("Python", sys.version_info >= (3, 9), f"{py_ver} ({sys.executable})")


def _check_version() -> None:
    """Check dawos-cli version."""
    _check("dawos-cli", True, f"v{__version__}")


def _check_update() -> None:
    """Check for available updates."""
    try:
        latest = updater.fetch_latest_tag()
        if not latest:
            _check("Update", False, "could not reach GitHub")
            return
        is_current = updater.parse_version(latest) <= updater.parse_version(__version__)
        if is_current:
            _check("Update", True, "up-to-date")
        else:
            _check("Update", False, f"v{latest} available — run: dawos update")
    except Exception:  # pylint: disable=broad-exception-caught
        _check("Update", False, "check failed")


def _check_profile() -> None:
    """Check active profile."""
    active = config.get_active_name()
    if not active:
        _check("Profile", False, "none configured — run: dawos profile add")
        return
    prof = config.get_profile(active)
    if prof:
        _check("Profile", True, f"{active} → {prof.get('url', '?')}")
    else:
        _check("Profile", False, f"{active} (not found in config)")


def _check_connection() -> None:
    """Check agent connectivity."""
    active = config.get_active_name()
    if not active:
        _check("Connection", False, "no profile to test")
        return
    prof = config.get_profile(active)
    if not prof:
        _check("Connection", False, "profile missing")
        return
    try:
        from . import client  # pylint: disable=import-outside-toplevel

        health = client.health(prof["url"])
        if health:
            node = health.get("node_name", "?")
            agent_ver = health.get("version", "?")
            _check("Connection", True, f"node={node} agent={agent_ver}")
        else:
            _check("Connection", False, f"cannot reach {prof['url']}")
    except Exception:  # pylint: disable=broad-exception-caught
        _check("Connection", False, "connection error")


def _detect_shell() -> str:
    """Detect the current shell name."""
    shell = os.environ.get("SHELL", "")
    if shell:
        return shell.rsplit("/", 1)[-1]
    comspec = os.environ.get("COMSPEC", "")
    if comspec:
        return comspec.rsplit("\\", 1)[-1]
    return ""


def _check_shell() -> None:
    """Check shell environment."""
    shell_name = _detect_shell()
    _check("Shell", True, shell_name or "unknown — run: dawos --install-completion")


def _check_config_file() -> None:
    """Check config file."""
    cfg_path = config.config_path()
    _check("Config", cfg_path.exists(), str(cfg_path))


def _check_pipx() -> None:
    """Check pipx availability."""
    pipx_path = shutil.which("pipx")
    _check("pipx", pipx_path is not None, pipx_path or "not found")


def run_doctor() -> None:
    """Run all diagnostic checks."""
    _console.print("[bold cyan]dawos doctor[/] — system diagnostics\n")

    _check_python()
    _check_version()
    _check_update()
    _check_profile()
    _check_connection()
    _check_shell()
    _check_config_file()
    _check_pipx()

    _console.print()

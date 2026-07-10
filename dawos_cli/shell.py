"""Interactive REPL shell — dawos shell.

Provides a REPL-style interface with command history and auto-completion.
Uses prompt_toolkit when available, falls back to stdlib readline.
"""

from __future__ import annotations

import logging
import os
import shlex
import sys

from rich.console import Console

from . import __version__

log = logging.getLogger(__name__)

_console = Console()

# All known top-level commands and aliases for auto-complete.
_COMMANDS = [
    "status",
    "top",
    "version",
    "update",
    "doctor",
    "help",
    "exit",
    "quit",
    # Command groups
    "profile",
    "system",
    "service",
    "session",
    "config",
    "network",
    "firewall",
    "nat",
    "pppoe",
    "traffic",
    "routing",
    "pool",
    "conntrack",
    "events",
    "scheduler",
    "dns",
    "dhcp",
    "ntp",
    "lldp",
    "vrrp",
    "flow",
    "monitoring",
    "limits",
    "zone",
    "diagnostics",
    "logs",
    # Aliases
    "s",
    "sys",
    "cfg",
    "net",
    "fw",
    "rt",
    "mon",
    "diag",
]


def _run_with_prompt_toolkit() -> None:
    """Run the REPL using prompt_toolkit for a modern experience."""
    from prompt_toolkit import (  # pylint: disable=import-outside-toplevel,import-error
        PromptSession,
    )
    from prompt_toolkit.completion import (  # pylint: disable=import-outside-toplevel,import-error
        WordCompleter,
    )
    from prompt_toolkit.history import (  # pylint: disable=import-outside-toplevel,import-error
        FileHistory,
    )

    from .config import CONFIG_DIR  # pylint: disable=import-outside-toplevel

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    history_file = CONFIG_DIR / ".shell_history"
    # Pre-create the history file owner-readable only — shell history may
    # contain hostnames, usernames, and pasted secrets.
    history_file.touch(exist_ok=True)
    try:
        os.chmod(history_file, 0o600)
    except OSError:
        pass  # best-effort; Windows may not support Unix permissions

    completer = WordCompleter(_COMMANDS, ignore_case=True)
    session: PromptSession = PromptSession(
        history=FileHistory(str(history_file)),
        completer=completer,
    )

    while True:
        try:
            text = session.prompt("dawos> ").strip()
        except (EOFError, KeyboardInterrupt):
            _console.print("\n[dim]Goodbye![/]")
            break

        if not text:
            continue

        if text in ("exit", "quit", "q"):
            _console.print("[dim]Goodbye![/]")
            break

        _execute_line(text)


def _run_with_readline() -> None:
    """Fallback REPL using stdlib readline (basic completion + history)."""
    try:
        import readline  # pylint: disable=import-outside-toplevel

        def completer(text: str, idx: int) -> str | None:
            matches = [c for c in _COMMANDS if c.startswith(text)]
            return matches[idx] if idx < len(matches) else None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass  # Windows without pyreadline — no completion

    while True:
        try:
            text = input("dawos> ").strip()
        except (EOFError, KeyboardInterrupt):
            _console.print("\n[dim]Goodbye![/]")
            break

        if not text:
            continue

        if text in ("exit", "quit", "q"):
            _console.print("[dim]Goodbye![/]")
            break

        _execute_line(text)


def _execute_line(line: str) -> None:
    """Parse and execute a single command line."""
    from .app import (  # pylint: disable=import-outside-toplevel,cyclic-import
        app as _app,
    )

    try:
        args = shlex.split(line)
    except ValueError as exc:
        _console.print(f"[red]Parse error:[/] {exc}")
        return

    try:
        _app(args, standalone_mode=False)
    except SystemExit:
        pass  # Typer raises SystemExit on --help, errors, etc.
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.debug("Shell command failed: %s", exc, exc_info=True)
        _console.print(
            f"[red]Error:[/] {type(exc).__name__}: {exc}"
            if isinstance(exc, (ValueError, TypeError, KeyError))
            else "[red]Error:[/] Command failed. Run with --verbose for details."
        )


def run_shell() -> None:
    """Entry point for the dawos shell command."""
    _console.print(f"[bold cyan]dawos shell[/] v{__version__}")
    _console.print("[dim]Type commands without 'dawos' prefix. Tab to complete.[/]")
    _console.print("[dim]Type 'exit' or Ctrl+D to quit.[/]\n")

    # Prefer prompt_toolkit for rich features
    try:
        import prompt_toolkit  # noqa: F401  # pylint: disable=import-outside-toplevel,unused-import,import-error

        _run_with_prompt_toolkit()
    except ImportError:
        _run_with_readline()

    sys.exit(0)

"""Shared application state accessible from all command modules.

This avoids threading Typer context objects through every command. The main
callback populates these values before any sub-command runs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppState:
    """Mutable singleton holding the active profile and output preferences."""

    profile_name: str = ""
    base_url: str = ""
    api_key: str = ""
    json_output: bool = False
    verbose: bool = False
    timeout: float = 30.0


# Module-level singleton — imported by commands and populated by app.py callback.
current = AppState()

"""Profile management — cross-platform configuration.

Config location (in priority order):
  1. $DAWOS_CONFIG_DIR          (explicit override)
  2. %APPDATA%/dawos            (Windows)
  3. $XDG_CONFIG_HOME/dawos     (Linux/macOS with XDG set)
  4. ~/.config/dawos             (Linux/macOS default)

Each profile stores a (url, api_key, name) tuple so operators can target different
BNG nodes without re-typing credentials every time.
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _default_config_dir() -> Path:
    """Return the platform-appropriate config directory."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        return Path(base) / "dawos"
    # Linux / macOS — respect XDG_CONFIG_HOME
    base = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    return Path(base) / "dawos"


CONFIG_DIR = Path(os.environ.get("DAWOS_CONFIG_DIR", _default_config_dir()))
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default structure for a fresh install.
_DEFAULT: Dict[str, Any] = {
    "active_profile": "",
    "profiles": {},
}


def _load() -> Dict[str, Any]:
    """Read the config file, or return defaults if it doesn't exist."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return copy.deepcopy(_DEFAULT)


def _save(data: Dict[str, Any]) -> None:
    """Persist config to disk, creating the directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass  # best-effort; Windows may not support Unix permissions


def list_profiles() -> Dict[str, Dict[str, str]]:
    """Return {name: {url, api_key, name}} for all saved profiles."""
    return _load().get("profiles", {})


def get_active_name() -> str:
    """Return the name of the currently active profile ('' if none)."""
    return _load().get("active_profile", "")


def get_profile(name: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Return profile data by name, or the active profile if name is None."""
    data = _load()
    if name is None:
        name = data.get("active_profile", "")
    return data.get("profiles", {}).get(name)


def add_profile(name: str, url: str, api_key: str, display_name: str = "") -> None:
    """Create or overwrite a profile."""
    data = _load()
    data.setdefault("profiles", {})[name] = {
        "url": url.rstrip("/"),
        "api_key": api_key,
        "display_name": display_name or name,
    }
    # Auto-activate the first profile.
    if not data.get("active_profile"):
        data["active_profile"] = name
    _save(data)


def remove_profile(name: str) -> bool:
    """Delete a profile. Returns True if it existed."""
    data = _load()
    if name not in data.get("profiles", {}):
        return False
    del data["profiles"][name]
    if data.get("active_profile") == name:
        remaining = list(data["profiles"])
        data["active_profile"] = remaining[0] if remaining else ""
    _save(data)
    return True


def use_profile(name: str) -> bool:
    """Set the active profile. Returns True if the profile exists."""
    data = _load()
    if name not in data.get("profiles", {}):
        return False
    data["active_profile"] = name
    _save(data)
    return True


def config_path() -> Path:
    """Return the config file path (for display in help text)."""
    return CONFIG_FILE


def export_profiles(name: Optional[str] = None) -> Dict[str, Any]:
    """Export profiles as a portable dict.

    If *name* is given, export only that profile. Otherwise export all.
    """
    data = _load()
    profiles = data.get("profiles", {})
    if name:
        prof = profiles.get(name)
        if prof is None:
            return {}
        profiles = {name: prof}
    return {
        "dawos_cli_export": True,
        "version": 1,
        "active_profile": data.get("active_profile", ""),
        "profiles": profiles,
    }


def import_profiles(payload: Dict[str, Any], *, merge: bool = True) -> int:
    """Import profiles from an exported payload.

    When *merge* is True (default), existing profiles are preserved and
    incoming profiles are added/overwritten.  When False, existing profiles
    are replaced entirely.

    Returns the number of profiles imported.
    """
    incoming = payload.get("profiles", {})
    if not incoming:
        return 0

    data = _load()
    if merge:
        data.setdefault("profiles", {}).update(incoming)
    else:
        data["profiles"] = incoming

    # If no active profile is set, adopt the incoming active.
    if not data.get("active_profile") and payload.get("active_profile"):
        if payload["active_profile"] in data["profiles"]:
            data["active_profile"] = payload["active_profile"]

    # Fallback: just pick the first profile.
    if not data.get("active_profile") and data["profiles"]:
        data["active_profile"] = next(iter(data["profiles"]))

    _save(data)
    return len(incoming)

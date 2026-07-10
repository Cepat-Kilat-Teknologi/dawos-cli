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
import logging
import os
import stat
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer

log = logging.getLogger(__name__)


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
        # Warn if config file has overly permissive permissions (Unix only).
        try:
            mode = CONFIG_FILE.stat().st_mode
            if mode & (stat.S_IROTH | stat.S_IWOTH | stat.S_IRGRP | stat.S_IWGRP):
                log.warning(
                    "Config file %s has permissive permissions (%o). "
                    "Run: chmod 600 %s",
                    CONFIG_FILE,
                    stat.S_IMODE(mode),
                    CONFIG_FILE,
                )
        except OSError:
            pass  # Windows or restricted filesystem — skip check
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            sys.stderr.write(
                f"Error: config file {CONFIG_FILE} is corrupt or unreadable: "
                f"{exc}\nFix or remove the file, then retry.\n"
            )
            raise typer.Exit(1) from exc
    return copy.deepcopy(_DEFAULT)


def _save(data: Dict[str, Any]) -> None:
    """Persist config atomically, owner-readable only (0600) from creation.

    The payload is written to a same-directory temp file opened with mode
    0600 (no world-readable window), then moved over the config file with
    ``os.replace`` so readers never observe a partial write.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_FILE.with_name(CONFIG_FILE.name + ".tmp")
    tmp.unlink(missing_ok=True)  # clear stale temp file from a failed write
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, CONFIG_FILE)


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


_REQUIRED_PROFILE_KEYS = {"url", "api_key"}


def _validate_profile(name: str, prof: Any) -> bool:
    """Return True if a profile dict has the required keys."""
    if not isinstance(prof, dict):
        log.warning("Skipping profile '%s': not a dict", name)
        return False
    missing = _REQUIRED_PROFILE_KEYS - set(prof.keys())
    if missing:
        log.warning(
            "Skipping profile '%s': missing keys %s", name, ", ".join(sorted(missing))
        )
        return False
    return True


def import_profiles(payload: Dict[str, Any], *, merge: bool = True) -> int:
    """Import profiles from an exported payload.

    When *merge* is True (default), existing profiles are preserved and
    incoming profiles are added/overwritten.  When False, existing profiles
    are replaced entirely.

    Profiles without the required ``url`` and ``api_key`` keys are
    silently skipped with a log warning.

    Returns the number of profiles imported.
    """
    incoming = payload.get("profiles", {})
    if not isinstance(incoming, dict) or not incoming:
        return 0

    # Validate each profile before import.
    valid = {k: v for k, v in incoming.items() if _validate_profile(k, v)}
    if not valid:
        return 0

    data = _load()
    if merge:
        data.setdefault("profiles", {}).update(valid)
    else:
        data["profiles"] = valid

    # If no active profile is set, adopt the incoming active.
    if not data.get("active_profile") and payload.get("active_profile"):
        if payload["active_profile"] in data["profiles"]:
            data["active_profile"] = payload["active_profile"]

    # Fallback: just pick the first profile.
    if not data.get("active_profile") and data["profiles"]:
        data["active_profile"] = next(iter(data["profiles"]))

    _save(data)
    return len(valid)


# ---------------------------------------------------------------------------
# Node groups — named sets of profiles for multi-node execution
# ---------------------------------------------------------------------------


def list_groups() -> Dict[str, list]:
    """Return all node groups as {name: [profile_names]}."""
    return _load().get("groups", {})


def get_group(name: str) -> Optional[list]:
    """Return the profile list for a group, or None if not found."""
    return _load().get("groups", {}).get(name)


def add_group(name: str, profiles: list) -> None:
    """Create or overwrite a node group with the given profile names.

    Validates that all referenced profiles exist before saving.

    Args:
        name: Group name.
        profiles: List of profile names to include.

    Raises:
        ValueError: If any referenced profile does not exist.
    """
    data = _load()
    existing = set(data.get("profiles", {}).keys())
    missing = [p for p in profiles if p not in existing]
    if missing:
        raise ValueError(f"Unknown profiles: {', '.join(missing)}")
    data.setdefault("groups", {})[name] = profiles
    _save(data)


def remove_group(name: str) -> bool:
    """Delete a node group. Returns True if it existed."""
    data = _load()
    groups = data.get("groups", {})
    if name not in groups:
        return False
    del groups[name]
    _save(data)
    return True

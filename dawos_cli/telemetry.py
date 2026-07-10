"""Opt-in anonymous usage telemetry — local file-based tracking.

Disabled by default. Enable with DAWOS_TELEMETRY=1.
All data stays local in the config directory. No external server.

Tracks:
  - Command usage counts
  - Feature adoption (which command groups are popular)
  - Error frequency

This helps prioritise development of the most-used features.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional

from .config import CONFIG_DIR

_TELEMETRY_FILE = CONFIG_DIR / ".telemetry.json"


def is_enabled() -> bool:
    """Check if telemetry is enabled (opt-in via env var)."""
    return os.environ.get("DAWOS_TELEMETRY", "").strip() in ("1", "true", "yes")


def _load() -> Dict[str, Any]:
    """Load telemetry data from disk."""
    try:
        if _TELEMETRY_FILE.exists():
            return json.loads(_TELEMETRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {"commands": {}, "errors": 0, "invocations": 0, "first_seen": time.time()}


def _save(data: Dict[str, Any]) -> None:
    """Persist telemetry data to disk."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data["last_seen"] = time.time()
        _TELEMETRY_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass  # Non-critical


def track_command(command: str) -> None:
    """Record a command invocation (if telemetry enabled)."""
    if not is_enabled():
        return
    data = _load()
    cmds = data.setdefault("commands", {})
    cmds[command] = cmds.get(command, 0) + 1
    data["invocations"] = data.get("invocations", 0) + 1
    _save(data)


def track_error(command: str) -> None:
    """Record a command error (if telemetry enabled)."""
    if not is_enabled():
        return
    data = _load()
    data["errors"] = data.get("errors", 0) + 1
    errors = data.setdefault("command_errors", {})
    errors[command] = errors.get(command, 0) + 1
    _save(data)


def get_stats() -> Optional[Dict[str, Any]]:
    """Return telemetry stats (for dawos doctor or debug)."""
    if not _TELEMETRY_FILE.exists():
        return None
    return _load()


def reset() -> None:
    """Clear all telemetry data."""
    try:
        if _TELEMETRY_FILE.exists():
            _TELEMETRY_FILE.unlink()
    except OSError:
        pass

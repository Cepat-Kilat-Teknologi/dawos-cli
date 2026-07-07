"""Version update checker — notifies when a new release is available.

Checks the GitHub API for the latest tag once per day (cached).
Cache is stored alongside config in the platform config directory.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Optional, Tuple

from . import __version__
from .config import CONFIG_DIR

_REPO = "Cepat-Kilat-Teknologi/dawos-cli"
_REPO_URL = f"https://github.com/{_REPO}.git"
_API_URL = f"https://api.github.com/repos/{_REPO}/tags"
_CACHE_FILE = CONFIG_DIR / ".update-check"
_CHECK_INTERVAL = 86400  # 24 hours in seconds


def parse_version(tag: str) -> Tuple[int, ...]:
    """Parse 'v0.1.0' or '0.1.0' into a comparable tuple."""
    clean = tag.lstrip("v").strip()
    parts = []
    for part in clean.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _read_cache() -> Optional[dict]:
    """Read the cached update check result."""
    try:
        if _CACHE_FILE.exists():
            data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _write_cache(latest: str) -> None:
    """Write the update check result to cache."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(
            json.dumps({"latest": latest, "checked_at": time.time()}) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass  # Non-critical — skip silently


def fetch_latest_tag() -> Optional[str]:
    """Fetch the latest tag name from GitHub API (non-blocking, 3s timeout)."""
    try:
        import httpx  # pylint: disable=import-outside-toplevel

        resp = httpx.get(_API_URL, timeout=3.0, follow_redirects=True)
        if resp.status_code == 200:
            tags = resp.json()
            if tags:
                return tags[0]["name"]
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # Network error, timeout, etc. — skip silently
    return None


def check_for_update() -> Optional[str]:
    """Check for a newer version. Returns the latest tag if update available.

    Uses a 24-hour cache to avoid hitting the API on every invocation.
    Returns None if already up-to-date, check fails, or within cache window.
    """
    # Skip in CI or when explicitly disabled
    if os.environ.get("DAWOS_NO_UPDATE_CHECK"):
        return None

    cache = _read_cache()
    now = time.time()

    # Use cache if fresh
    if cache and (now - cache.get("checked_at", 0)) < _CHECK_INTERVAL:
        latest = cache.get("latest", "")
        if latest and parse_version(latest) > parse_version(__version__):
            return latest
        return None

    # Fetch from GitHub
    latest = fetch_latest_tag()
    if latest:
        _write_cache(latest)
        if parse_version(latest) > parse_version(__version__):
            return latest

    return None


def run_self_update() -> bool:
    """Run self-update via pipx. Returns True on success."""
    cmd = [
        sys.executable,
        "-m",
        "pipx",
        "install",
        "--force",
        f"git+{_REPO_URL}",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # pipx not available — try pip
        pip_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            f"git+{_REPO_URL}",
        ]
        try:
            result = subprocess.run(
                pip_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

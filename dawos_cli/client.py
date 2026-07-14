"""HTTP client for the dawos-agent REST API.

Wraps httpx with:
- Auto-attached X-API-Key header
- Rich-formatted error messages
- Timeout handling
- SSE streaming support
"""

from __future__ import annotations

from typing import Any, Dict, Generator, Optional

import httpx
from rich.console import Console

from . import state

console = Console(stderr=True)

# Lazy singleton — created on first call.
_client: Optional[httpx.Client] = None


def _get_client() -> httpx.Client:
    """Return (or create) the httpx client from current state."""
    global _client  # pylint: disable=global-statement
    if _client is None:
        s = state.current
        if not s.base_url:
            console.print(
                "[bold red]Error:[/] No profile configured.\n"
                "Run [bold]dawos profile add <name> --url <url> --key <key>[/] first."
            )
            raise SystemExit(1)
        _client = httpx.Client(
            base_url=s.base_url,
            headers={"X-API-Key": s.api_key},
            timeout=s.timeout,
        )
    return _client


def _handle_error(exc: httpx.HTTPStatusError) -> None:
    """Pretty-print HTTP errors and exit."""
    code = exc.response.status_code
    try:
        body = exc.response.json()
        detail = body.get("detail", str(body))
    except Exception:  # pylint: disable=broad-exception-caught
        detail = exc.response.text[:200]

    if code == 401:
        console.print("[bold red]Authentication failed (401).[/] Check your API key.")
    elif code == 404:
        console.print(f"[bold yellow]Not found (404):[/] {detail}")
    elif code == 422:
        console.print(f"[bold yellow]Validation error (422):[/] {detail}")
    elif code >= 500:
        console.print(f"[bold red]Server error ({code}):[/] {detail}")
    else:
        console.print(f"[bold red]HTTP {code}:[/] {detail}")
    raise SystemExit(1)


def _handle_connection_error(exc: httpx.ConnectError) -> None:
    """Pretty-print connection failures."""
    url = state.current.base_url
    console.print(
        f"[bold red]Connection failed:[/] Cannot reach [cyan]{url}[/]\n"
        "Check that dawos-agent is running and the URL is correct."
    )
    raise SystemExit(1)


def _handle_timeout(exc: httpx.TimeoutException) -> None:
    """Pretty-print timeout errors."""
    url = state.current.base_url
    timeout = state.current.timeout
    console.print(
        f"[bold red]Request timed out:[/] No response from [cyan]{url}[/] "
        f"within {timeout}s.\n"
        "Try increasing the timeout with [bold]--timeout[/] or check the agent."
    )
    raise SystemExit(1)


def _handle_request_error(exc: httpx.RequestError) -> None:
    """Pretty-print generic transport errors (read/write/pool failures)."""
    url = state.current.base_url
    console.print(
        f"[bold red]Request failed:[/] Communication error with [cyan]{url}[/].\n"
        "Check your network connection and try again."
    )
    raise SystemExit(1)


def get(path: str, **params: Any) -> Any:
    """GET request, return parsed JSON."""
    try:
        resp = _get_client().get(path, params=params or None)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    return None  # unreachable — handlers always raise


def get_text(path: str, **params: Any) -> str:
    """GET request, return raw response text (for CSV downloads)."""
    try:
        resp = _get_client().get(path, params=params or None)
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    return ""  # pragma: no cover — unreachable, handlers always raise


def post(path: str, json: Optional[Dict] = None) -> Any:
    """POST request, return parsed JSON."""
    try:
        resp = _get_client().post(path, json=json)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"status": "ok"}
        return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    return None  # unreachable — handlers always raise


def put(path: str, json: Optional[Dict] = None) -> Any:
    """PUT request, return parsed JSON."""
    try:
        resp = _get_client().put(path, json=json)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    return None  # unreachable — handlers always raise


def delete(path: str, json: Optional[Dict] = None) -> Any:
    """DELETE request, return parsed JSON or ok."""
    try:
        resp = _get_client().request("DELETE", path, json=json)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"status": "ok"}
        return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    return None  # unreachable — handlers always raise


def stream_sse(path: str) -> Generator[str, None, None]:
    """Yield SSE data lines from a streaming endpoint."""
    try:
        with _get_client().stream("GET", path) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line.startswith("data: "):
                    yield line[6:]
    except httpx.HTTPStatusError as exc:
        _handle_error(exc)
    except httpx.ConnectError as exc:
        _handle_connection_error(exc)
    except httpx.TimeoutException as exc:
        _handle_timeout(exc)
    except httpx.RequestError as exc:
        _handle_request_error(exc)
    except KeyboardInterrupt:
        pass


def health(base_url: str) -> Optional[Dict]:
    """Quick health check against a URL (no auth). Returns None on failure."""
    try:
        resp = httpx.get(f"{base_url.rstrip('/')}/health", timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return None

"""Multi-node parallel HTTP executor.

Sends the same API request to multiple BNG nodes concurrently using
a thread pool.  Each node gets its own short-lived httpx.Client so
there is no shared state between threads.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from . import config


@dataclass
class NodeResult:
    """Outcome of a single API call against one BNG node."""

    profile: str
    url: str
    success: bool
    status_code: int = 0
    data: Optional[Any] = None
    error: str = ""


@dataclass
class MultiResult:
    """Aggregated results from a parallel multi-node request."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    results: List[NodeResult] = field(default_factory=list)


def _execute_one(
    profile_name: str,
    prof: Dict[str, str],
    method: str,
    path: str,
    *,
    json_body: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: float = 30.0,
) -> NodeResult:
    """Send a single HTTP request to one node and return the result.

    This function is designed to run inside a thread — it creates its
    own httpx.Client and does not touch any shared mutable state.
    """
    base_url = prof["url"]
    api_key = prof.get("api_key", "")

    try:
        with httpx.Client(
            base_url=base_url,
            headers={"X-API-Key": api_key},
            timeout=timeout,
        ) as client:
            resp = client.request(
                method,
                path,
                json=json_body,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json() if resp.content else None
            return NodeResult(
                profile=profile_name,
                url=base_url,
                success=True,
                status_code=resp.status_code,
                data=data,
            )
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text[:200])
        except Exception:  # pylint: disable=broad-exception-caught
            detail = exc.response.text[:200]
        return NodeResult(
            profile=profile_name,
            url=base_url,
            success=False,
            status_code=exc.response.status_code,
            error=str(detail),
        )
    except httpx.ConnectError:
        return NodeResult(
            profile=profile_name,
            url=base_url,
            success=False,
            error=f"Connection failed: cannot reach {base_url}",
        )
    except httpx.TimeoutException:
        return NodeResult(
            profile=profile_name,
            url=base_url,
            success=False,
            error=f"Request timed out after {timeout}s",
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return NodeResult(
            profile=profile_name,
            url=base_url,
            success=False,
            error=str(exc),
        )


def execute_multi(
    profiles: List[str],
    method: str,
    path: str,
    *,
    json_body: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: float = 30.0,
    max_workers: int = 10,
) -> MultiResult:
    """Execute an HTTP request against multiple nodes in parallel.

    Resolves each profile name to its stored URL and API key, then
    dispatches requests concurrently via a thread pool.

    Args:
        profiles: List of profile names to target.
        method: HTTP method (GET, POST, PUT, DELETE).
        path: API path (e.g. ``/health``, ``/api/v1/sessions``).
        json_body: Optional JSON request body.
        params: Optional query parameters.
        timeout: Per-request timeout in seconds.
        max_workers: Maximum concurrent threads.

    Returns:
        MultiResult with per-node outcomes.
    """
    result = MultiResult(total=len(profiles))

    # Resolve profiles to (name, profile_data) pairs.
    resolved: List[tuple] = []
    for name in profiles:
        prof = config.get_profile(name)
        if prof is None:
            result.results.append(
                NodeResult(
                    profile=name,
                    url="",
                    success=False,
                    error=f"Profile '{name}' not found",
                )
            )
            result.failed += 1
        else:
            resolved.append((name, prof))

    if not resolved:
        return result

    with ThreadPoolExecutor(max_workers=min(max_workers, len(resolved))) as pool:
        futures = {
            pool.submit(
                _execute_one,
                name,
                prof,
                method,
                path,
                json_body=json_body,
                params=params,
                timeout=timeout,
            ): name
            for name, prof in resolved
        }

        for future in as_completed(futures):
            node_result = future.result()
            result.results.append(node_result)
            if node_result.success:
                result.succeeded += 1
            else:
                result.failed += 1

    return result

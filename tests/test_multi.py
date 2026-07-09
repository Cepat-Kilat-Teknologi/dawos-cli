"""Tests for multi-node parallel HTTP executor."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from dawos_cli.multi import MultiResult, NodeResult, _execute_one, execute_multi

# ---------------------------------------------------------------------------
# _execute_one
# ---------------------------------------------------------------------------


class TestExecuteOne:
    """Unit tests for the single-node HTTP executor."""

    def test_success_get(self):
        """Successful GET returns parsed JSON."""
        prof = {"url": "http://node1:8470", "api_key": "key1"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = b'{"status":"ok"}'
            mock_resp.json.return_value = {"status": "ok"}
            mock_resp.raise_for_status = MagicMock()
            mock_client.request.return_value = mock_resp

            result = _execute_one("node1", prof, "GET", "/health")

        assert result.success is True
        assert result.profile == "node1"
        assert result.status_code == 200
        assert result.data == {"status": "ok"}

    def test_http_error(self):
        """HTTP 401 returns failure with detail."""
        prof = {"url": "http://node1:8470", "api_key": "bad"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.text = "Unauthorized"
            mock_resp.json.return_value = {"detail": "Invalid API key"}
            mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401", request=MagicMock(), response=mock_resp
            )
            mock_client.request.return_value = mock_resp

            result = _execute_one("node1", prof, "GET", "/api/v1/sessions")

        assert result.success is False
        assert result.status_code == 401
        assert "Invalid API key" in result.error

    def test_connect_error(self):
        """Connection failure returns descriptive error."""
        prof = {"url": "http://unreachable:8470", "api_key": "key"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.request.side_effect = httpx.ConnectError("refused")

            result = _execute_one("down", prof, "GET", "/health")

        assert result.success is False
        assert "Connection failed" in result.error

    def test_timeout_error(self):
        """Timeout returns descriptive error."""
        prof = {"url": "http://slow:8470", "api_key": "key"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.request.side_effect = httpx.ReadTimeout("timeout")

            result = _execute_one("slow", prof, "GET", "/health", timeout=5.0)

        assert result.success is False
        assert "timed out" in result.error

    def test_generic_error(self):
        """Unexpected exception is caught and reported."""
        prof = {"url": "http://node:8470", "api_key": "key"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.request.side_effect = RuntimeError("unexpected")

            result = _execute_one("node", prof, "GET", "/health")

        assert result.success is False
        assert "unexpected" in result.error

    def test_empty_response_body(self):
        """Response with no content returns data=None."""
        prof = {"url": "http://node:8470", "api_key": "key"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            mock_resp = MagicMock()
            mock_resp.status_code = 204
            mock_resp.content = b""
            mock_resp.raise_for_status = MagicMock()
            mock_client.request.return_value = mock_resp

            result = _execute_one("node", prof, "DELETE", "/api/v1/something")

        assert result.success is True
        assert result.data is None

    def test_http_error_non_json_body(self):
        """HTTP error with non-JSON response body uses text fallback."""
        prof = {"url": "http://node:8470", "api_key": "key"}
        with patch("dawos_cli.multi.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.text = "Internal Server Error"
            mock_resp.json.side_effect = ValueError("not json")
            mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500", request=MagicMock(), response=mock_resp
            )
            mock_client.request.return_value = mock_resp

            result = _execute_one("node", prof, "GET", "/health")

        assert result.success is False
        assert result.status_code == 500
        assert "Internal Server Error" in result.error


# ---------------------------------------------------------------------------
# execute_multi
# ---------------------------------------------------------------------------


class TestExecuteMulti:
    """Integration tests for the multi-node executor."""

    def test_unknown_profile(self):
        """Profiles that don't exist are reported as failed."""
        with patch("dawos_cli.multi.config.get_profile", return_value=None):
            result = execute_multi(["missing"], "GET", "/health")

        assert result.total == 1
        assert result.failed == 1
        assert result.succeeded == 0
        assert "not found" in result.results[0].error

    def test_all_success(self):
        """All nodes succeed."""
        profiles = {"a": {"url": "http://a:8470", "api_key": "k"}}
        with (
            patch(
                "dawos_cli.multi.config.get_profile",
                side_effect=lambda n: profiles.get(n),
            ),
            patch(
                "dawos_cli.multi._execute_one",
                return_value=NodeResult(
                    profile="a",
                    url="http://a:8470",
                    success=True,
                    status_code=200,
                    data={"status": "ok"},
                ),
            ),
        ):
            result = execute_multi(["a"], "GET", "/health")

        assert result.total == 1
        assert result.succeeded == 1
        assert result.failed == 0

    def test_mixed_results(self):
        """Some nodes succeed, some fail."""
        profiles = {
            "a": {"url": "http://a:8470", "api_key": "k"},
            "b": {"url": "http://b:8470", "api_key": "k"},
        }

        def mock_execute(name, prof, method, path, **kwargs):
            if name == "a":
                return NodeResult(
                    profile="a", url="http://a:8470", success=True, status_code=200
                )
            return NodeResult(
                profile="b", url="http://b:8470", success=False, error="refused"
            )

        with (
            patch(
                "dawos_cli.multi.config.get_profile",
                side_effect=lambda n: profiles.get(n),
            ),
            patch("dawos_cli.multi._execute_one", side_effect=mock_execute),
        ):
            result = execute_multi(["a", "b"], "GET", "/health")

        assert result.total == 2
        assert result.succeeded == 1
        assert result.failed == 1

    def test_all_unknown_profiles(self):
        """All profiles unknown returns immediately."""
        with patch("dawos_cli.multi.config.get_profile", return_value=None):
            result = execute_multi(["x", "y"], "GET", "/health")

        assert result.total == 2
        assert result.failed == 2
        assert result.succeeded == 0

    def test_empty_profiles(self):
        """Empty profile list returns empty result."""
        result = execute_multi([], "GET", "/health")

        assert result.total == 0
        assert result.succeeded == 0
        assert result.failed == 0


# ---------------------------------------------------------------------------
# Dataclass defaults
# ---------------------------------------------------------------------------


class TestDataclasses:
    """NodeResult and MultiResult field defaults."""

    def test_node_result_defaults(self):
        nr = NodeResult(profile="x", url="http://x:8470", success=True)
        assert nr.status_code == 0
        assert nr.data is None
        assert nr.error == ""

    def test_multi_result_defaults(self):
        mr = MultiResult()
        assert mr.total == 0
        assert mr.succeeded == 0
        assert mr.failed == 0
        assert mr.results == []

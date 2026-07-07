"""Tests for dawos_cli.client module."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from dawos_cli import client as client_mod
from dawos_cli import state

BASE = "http://test-agent:8470"


@pytest.fixture(autouse=True)
def _fresh_client():
    """Ensure a clean client singleton per test."""
    client_mod._client = None
    yield
    client_mod._client = None


class TestGetClient:
    def test_creates_client(self):
        c = client_mod._get_client()
        assert isinstance(c, httpx.Client)

    def test_reuses_singleton(self):
        c1 = client_mod._get_client()
        c2 = client_mod._get_client()
        assert c1 is c2

    def test_no_base_url_exits(self):
        state.current.base_url = ""
        with pytest.raises(SystemExit):
            client_mod._get_client()


class TestGet:
    @respx.mock
    def test_get_success(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        result = client_mod.get("/api/v1/test")
        assert result == {"ok": True}

    @respx.mock
    def test_get_with_params(self):
        route = respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        client_mod.get("/api/v1/test", limit=10)
        assert route.called

    @respx.mock
    def test_get_401(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(401, json={"detail": "bad key"})
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    @respx.mock
    def test_get_404(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(404, json={"detail": "not found"})
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    @respx.mock
    def test_get_422(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(422, json={"detail": "validation"})
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    @respx.mock
    def test_get_500(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(500, json={"detail": "internal"})
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    @respx.mock
    def test_get_other_error(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(403, json={"detail": "forbidden"})
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    @respx.mock
    def test_get_error_non_json_body(self):
        respx.get(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(500, text="server broke")
        )
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    def test_get_connection_error(self):
        state.current.base_url = "http://unreachable:9999"
        client_mod._client = None
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")


class TestPost:
    @respx.mock
    def test_post_success(self):
        respx.post(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        result = client_mod.post("/api/v1/test", json={"foo": "bar"})
        assert result == {"status": "ok"}

    @respx.mock
    def test_post_204(self):
        respx.post(f"{BASE}/api/v1/test").mock(return_value=httpx.Response(204))
        result = client_mod.post("/api/v1/test")
        assert result == {"status": "ok"}

    @respx.mock
    def test_post_error(self):
        respx.post(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(422, json={"detail": "bad"})
        )
        with pytest.raises(SystemExit):
            client_mod.post("/api/v1/test", json={})


class TestPut:
    @respx.mock
    def test_put_success(self):
        respx.put(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"updated": True})
        )
        result = client_mod.put("/api/v1/test", json={"key": "val"})
        assert result == {"updated": True}

    @respx.mock
    def test_put_error(self):
        respx.put(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(500, json={"detail": "fail"})
        )
        with pytest.raises(SystemExit):
            client_mod.put("/api/v1/test", json={})


class TestDelete:
    @respx.mock
    def test_delete_success(self):
        respx.delete(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"deleted": True})
        )
        result = client_mod.delete("/api/v1/test")
        assert result == {"deleted": True}

    @respx.mock
    def test_delete_204(self):
        respx.delete(f"{BASE}/api/v1/test").mock(return_value=httpx.Response(204))
        result = client_mod.delete("/api/v1/test")
        assert result == {"status": "ok"}

    @respx.mock
    def test_delete_with_json(self):
        respx.delete(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        result = client_mod.delete("/api/v1/test", json={"id": 1})
        assert result == {"ok": True}

    @respx.mock
    def test_delete_error(self):
        respx.delete(f"{BASE}/api/v1/test").mock(
            return_value=httpx.Response(404, json={"detail": "gone"})
        )
        with pytest.raises(SystemExit):
            client_mod.delete("/api/v1/test")


class TestPostConnectionError:
    def test_post_connection_error(self):
        state.current.base_url = "http://unreachable:9999"
        client_mod._client = None
        with pytest.raises(SystemExit):
            client_mod.post("/api/v1/test", json={"key": "val"})


class TestPutConnectionError:
    def test_put_connection_error(self):
        state.current.base_url = "http://unreachable:9999"
        client_mod._client = None
        with pytest.raises(SystemExit):
            client_mod.put("/api/v1/test", json={"key": "val"})


class TestDeleteConnectionError:
    def test_delete_connection_error(self):
        state.current.base_url = "http://unreachable:9999"
        client_mod._client = None
        with pytest.raises(SystemExit):
            client_mod.delete("/api/v1/test")


class TestStreamSSE:
    @respx.mock
    def test_stream_sse_success(self):
        respx.get(f"{BASE}/api/v1/events/stream").mock(
            return_value=httpx.Response(
                200,
                text="data: hello\ndata: world\nother: skip\n",
                headers={"content-type": "text/event-stream"},
            )
        )
        lines = list(client_mod.stream_sse("/api/v1/events/stream"))
        assert lines == ["hello", "world"]

    @respx.mock
    def test_stream_sse_http_error(self):
        """stream_sse raises SystemExit on HTTP errors."""
        # Use patch because respx streaming + raise_for_status has content issues
        from contextlib import contextmanager

        @contextmanager
        def _mock_stream(method, path):
            resp = httpx.Response(
                401,
                json={"detail": "unauthorized"},
                request=httpx.Request("GET", f"{BASE}{path}"),
            )
            yield resp

        with patch.object(client_mod, "_get_client") as mc:
            mc.return_value.stream = _mock_stream
            with pytest.raises(SystemExit):
                list(client_mod.stream_sse("/api/v1/events/stream"))

    def test_stream_sse_connection_error(self):
        state.current.base_url = "http://unreachable:9999"
        client_mod._client = None
        with pytest.raises(SystemExit):
            list(client_mod.stream_sse("/api/v1/events/stream"))

    @respx.mock
    def test_stream_sse_keyboard_interrupt(self):
        def _raise_kb(*a, **kw):
            raise KeyboardInterrupt()

        with patch.object(client_mod, "_get_client") as mc:
            mc.return_value.stream.side_effect = _raise_kb
            lines = list(client_mod.stream_sse("/api/v1/events/stream"))
            assert lines == []


class TestHealth:
    @respx.mock
    def test_health_success(self):
        respx.get(f"{BASE}/health").mock(
            return_value=httpx.Response(200, json={"status": "healthy"})
        )
        result = client_mod.health(BASE)
        assert result == {"status": "healthy"}

    @respx.mock
    def test_health_fail(self):
        respx.get(f"{BASE}/health").mock(return_value=httpx.Response(500, text="down"))
        result = client_mod.health(BASE)
        assert result is None

    def test_health_connection_error(self):
        result = client_mod.health("http://unreachable:9999")
        assert result is None

    @respx.mock
    def test_health_strips_slash(self):
        respx.get(f"{BASE}/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        result = client_mod.health(f"{BASE}/")
        assert result == {"status": "ok"}

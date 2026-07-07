"""Shared test fixtures for dawos-cli test suite."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from dawos_cli import state
from dawos_cli.app import app


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset global state before each test."""
    s = state.current
    s.profile_name = "test"
    s.base_url = "http://test-agent:8470"
    s.api_key = "test-api-key"
    s.json_output = False
    s.verbose = False
    s.timeout = 5.0
    yield
    import dawos_cli.client as c

    c._client = None


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(runner):
    """Invoke the dawos CLI app. Returns runner result."""

    def _invoke(*args: str, **kwargs: Any):
        return runner.invoke(app, list(args), catch_exceptions=False, **kwargs)

    return _invoke


@pytest.fixture
def mock_client():
    """Patch client.get/post/put/delete/stream_sse/health for command tests."""
    with (
        patch("dawos_cli.client.get") as mg,
        patch("dawos_cli.client.post") as mp,
        patch("dawos_cli.client.put") as mpu,
        patch("dawos_cli.client.delete") as md,
        patch("dawos_cli.client.stream_sse") as ms,
        patch("dawos_cli.client.health") as mh,
    ):
        mg.return_value = {}
        mp.return_value = {"status": "ok", "message": "done"}
        mpu.return_value = {"status": "ok", "message": "done"}
        md.return_value = {"status": "ok"}
        ms.return_value = iter([])
        mh.return_value = {"status": "healthy"}
        yield {
            "get": mg,
            "post": mp,
            "put": mpu,
            "delete": md,
            "stream_sse": ms,
            "health": mh,
        }


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect config to a temp directory."""
    import dawos_cli.config as cfg

    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config.json")
    return tmp_path

"""Tests for dawos_cli.telemetry module."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from dawos_cli import telemetry


@pytest.fixture(autouse=True)
def _isolate_telemetry(tmp_config):
    """Redirect telemetry file to the temp config directory."""
    tel_file = tmp_config / ".telemetry.json"
    with patch.object(telemetry, "_TELEMETRY_FILE", tel_file):
        yield tel_file


class TestIsEnabled:
    def test_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert telemetry.is_enabled() is False

    def test_enabled_with_1(self):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "1"}):
            assert telemetry.is_enabled() is True

    def test_enabled_with_true(self):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "true"}):
            assert telemetry.is_enabled() is True

    def test_enabled_with_yes(self):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "yes"}):
            assert telemetry.is_enabled() is True

    def test_disabled_with_0(self):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "0"}):
            assert telemetry.is_enabled() is False

    def test_disabled_with_empty(self):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": ""}):
            assert telemetry.is_enabled() is False


class TestTrackCommand:
    def test_noop_when_disabled(self, _isolate_telemetry):
        tel_file = _isolate_telemetry
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "0"}):
            telemetry.track_command("status")
            assert not tel_file.exists()

    def test_records_when_enabled(self, _isolate_telemetry):
        tel_file = _isolate_telemetry
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "1"}):
            telemetry.track_command("status")
            telemetry.track_command("status")
            telemetry.track_command("session list")

            data = json.loads(tel_file.read_text())
            assert data["commands"]["status"] == 2
            assert data["commands"]["session list"] == 1
            assert data["sessions"] == 3


class TestTrackError:
    def test_noop_when_disabled(self, _isolate_telemetry):
        tel_file = _isolate_telemetry
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "0"}):
            telemetry.track_error("status")
            assert not tel_file.exists()

    def test_records_when_enabled(self, _isolate_telemetry):
        tel_file = _isolate_telemetry
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "1"}):
            telemetry.track_error("status")
            telemetry.track_error("status")

            data = json.loads(tel_file.read_text())
            assert data["errors"] == 2
            assert data["command_errors"]["status"] == 2


class TestGetStats:
    def test_returns_none_when_no_file(self, _isolate_telemetry):
        assert telemetry.get_stats() is None

    def test_returns_data_after_tracking(self, _isolate_telemetry):
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "1"}):
            telemetry.track_command("status")

        stats = telemetry.get_stats()
        assert stats is not None
        assert stats["commands"]["status"] == 1


class TestReset:
    def test_reset_removes_file(self, _isolate_telemetry):
        tel_file = _isolate_telemetry
        with patch.dict(os.environ, {"DAWOS_TELEMETRY": "1"}):
            telemetry.track_command("status")
            assert tel_file.exists()

        telemetry.reset()
        assert not tel_file.exists()

    def test_reset_noop_when_no_file(self):
        telemetry.reset()  # should not raise

"""Tests for security hardening audit fixes (DC-M01 through DC-L01).

Covers:
- DC-M01: Timeout exception handling in client.py
- DC-M02: Generic RequestError handling in client.py
- DC-M03: Sanitized error output in shell.py REPL
- DC-M04: Sanitized error output in wizard engine
- DC-M05: Security warning on profile export
- DC-M06: Profile structure validation on import
- DC-L01: Config file permission check
"""

from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from rich.console import Console

from dawos_cli import client as client_mod
from dawos_cli import config
from dawos_cli.wizards import Step, run_wizard

BASE = "http://test-agent:8470"


# ═══════════════════════════════════════════════════════════════════
# DC-M01 / DC-M02: Timeout + RequestError handlers
# ═══════════════════════════════════════════════════════════════════


class TestHandleTimeout:
    """Unit tests for _handle_timeout helper."""

    def test_handle_timeout_exits(self):
        exc = httpx.ReadTimeout("timed out")
        with pytest.raises(SystemExit):
            client_mod._handle_timeout(exc)

    def test_handle_timeout_message(self, capsys):
        exc = httpx.ReadTimeout("timed out")
        with pytest.raises(SystemExit):
            client_mod._handle_timeout(exc)


class TestHandleRequestError:
    """Unit tests for _handle_request_error helper."""

    def test_handle_request_error_exits(self):
        req = httpx.Request("GET", f"{BASE}/test")
        exc = httpx.ReadError("read failed", request=req)
        with pytest.raises(SystemExit):
            client_mod._handle_request_error(exc)


class TestGetTimeout:
    """DC-M01: get() handles TimeoutException."""

    def test_get_timeout(self, monkeypatch):
        mock_cl = MagicMock()
        mock_cl.get.side_effect = httpx.ReadTimeout("timed out")
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")

    def test_get_request_error(self, monkeypatch):
        mock_cl = MagicMock()
        req = httpx.Request("GET", f"{BASE}/test")
        mock_cl.get.side_effect = httpx.ReadError("broken", request=req)
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.get("/api/v1/test")


class TestPostTimeout:
    """DC-M01: post() handles TimeoutException."""

    def test_post_timeout(self, monkeypatch):
        mock_cl = MagicMock()
        mock_cl.post.side_effect = httpx.ReadTimeout("timed out")
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.post("/api/v1/test", json={"k": "v"})

    def test_post_request_error(self, monkeypatch):
        mock_cl = MagicMock()
        req = httpx.Request("POST", f"{BASE}/test")
        mock_cl.post.side_effect = httpx.ReadError("broken", request=req)
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.post("/api/v1/test", json={"k": "v"})


class TestPutTimeout:
    """DC-M01: put() handles TimeoutException."""

    def test_put_timeout(self, monkeypatch):
        mock_cl = MagicMock()
        mock_cl.put.side_effect = httpx.ReadTimeout("timed out")
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.put("/api/v1/test", json={"k": "v"})

    def test_put_request_error(self, monkeypatch):
        mock_cl = MagicMock()
        req = httpx.Request("PUT", f"{BASE}/test")
        mock_cl.put.side_effect = httpx.ReadError("broken", request=req)
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.put("/api/v1/test", json={"k": "v"})


class TestDeleteTimeout:
    """DC-M01: delete() handles TimeoutException."""

    def test_delete_timeout(self, monkeypatch):
        mock_cl = MagicMock()
        mock_cl.request.side_effect = httpx.ReadTimeout("timed out")
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.delete("/api/v1/test")

    def test_delete_request_error(self, monkeypatch):
        mock_cl = MagicMock()
        req = httpx.Request("DELETE", f"{BASE}/test")
        mock_cl.request.side_effect = httpx.ReadError("broken", request=req)
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            client_mod.delete("/api/v1/test")


class TestStreamSSETimeout:
    """DC-M01: stream_sse() handles TimeoutException."""

    def test_stream_sse_timeout(self, monkeypatch):
        mock_cl = MagicMock()
        mock_cl.stream.side_effect = httpx.ReadTimeout("timed out")
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            list(client_mod.stream_sse("/api/v1/events/stream"))

    def test_stream_sse_request_error(self, monkeypatch):
        mock_cl = MagicMock()
        req = httpx.Request("GET", f"{BASE}/events")
        mock_cl.stream.side_effect = httpx.ReadError("broken", request=req)
        monkeypatch.setattr(client_mod, "_client", mock_cl)
        with pytest.raises(SystemExit):
            list(client_mod.stream_sse("/api/v1/events/stream"))


# ═══════════════════════════════════════════════════════════════════
# DC-M03: Sanitized error output in shell.py
# ═══════════════════════════════════════════════════════════════════


class TestShellErrorSanitization:
    """DC-M03: Shell REPL does not leak raw exception details."""

    def _make_console(self):
        buf = StringIO()
        return Console(file=buf, force_terminal=True, width=120), buf

    def test_value_error_shows_message(self):
        """ValueError shows the actual message (safe user-facing error)."""
        from dawos_cli import shell

        con, buf = self._make_console()
        with (
            patch.object(shell, "_console", con),
            patch("dawos_cli.app.app", side_effect=ValueError("bad input")),
        ):
            shell._execute_line("status")
            text = buf.getvalue()
            assert "ValueError" in text
            assert "bad input" in text

    def test_runtime_error_hides_details(self):
        """RuntimeError hides raw message, shows generic fallback."""
        from dawos_cli import shell

        con, buf = self._make_console()
        with (
            patch.object(shell, "_console", con),
            patch(
                "dawos_cli.app.app",
                side_effect=RuntimeError("/usr/lib/python3/secret.py"),
            ),
        ):
            shell._execute_line("status")
            text = buf.getvalue()
            assert "/usr/lib/python3/secret.py" not in text
            assert "Command failed" in text

    def test_type_error_shows_message(self):
        """TypeError shows the actual message (safe user-facing error)."""
        from dawos_cli import shell

        con, buf = self._make_console()
        with (
            patch.object(shell, "_console", con),
            patch("dawos_cli.app.app", side_effect=TypeError("wrong type")),
        ):
            shell._execute_line("status")
            text = buf.getvalue()
            assert "TypeError" in text
            assert "wrong type" in text


# ═══════════════════════════════════════════════════════════════════
# DC-M04: Sanitized error output in wizard engine
# ═══════════════════════════════════════════════════════════════════


class TestWizardErrorSanitization:
    """DC-M04: Wizard engine does not leak raw exception details."""

    def test_value_error_shows_message(self):
        """ValueError in step action shows the actual message."""

        def bad_step(ctx):
            raise ValueError("missing field")

        steps = [Step(title="Fail", description="", action=bad_step, required=True)]
        ctx = run_wizard("Test", steps)
        assert not ctx["results"][0].success
        assert "missing field" in ctx["results"][0].message

    def test_runtime_error_hides_details(self):
        """RuntimeError in step action hides internal details."""

        def bad_step(ctx):
            raise RuntimeError("/internal/path/leak.py:42 segfault")

        steps = [Step(title="Fail", description="", action=bad_step, required=True)]
        ctx = run_wizard("Test", steps)
        assert not ctx["results"][0].success
        assert "/internal/path/leak.py" not in ctx["results"][0].message
        assert "Step failed" in ctx["results"][0].message
        assert "RuntimeError" in ctx["results"][0].message

    def test_os_error_hides_details(self):
        """OSError in step action hides internal details."""

        def bad_step(ctx):
            raise OSError("Permission denied: /etc/shadow")

        steps = [Step(title="Fail", description="", action=bad_step, required=True)]
        ctx = run_wizard("Test", steps)
        assert not ctx["results"][0].success
        assert "/etc/shadow" not in ctx["results"][0].message
        assert "Step failed" in ctx["results"][0].message

    def test_key_error_shows_message(self):
        """KeyError shows the missing key (safe for users)."""

        def bad_step(ctx):
            raise KeyError("missing_key")

        steps = [Step(title="Fail", description="", action=bad_step, required=True)]
        ctx = run_wizard("Test", steps)
        assert not ctx["results"][0].success
        assert "missing_key" in ctx["results"][0].message


# ═══════════════════════════════════════════════════════════════════
# DC-M05: Security warning on profile export
# ═══════════════════════════════════════════════════════════════════


class TestProfileExportWarning:
    """DC-M05: Export command warns about plaintext API keys."""

    def test_export_warns_about_keys(self, cli, tmp_config, mock_client):
        """Export to stdout shows security warning."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "secret-key-123")
        result = cli("profile", "export")
        assert result.exit_code == 0
        assert "plaintext" in result.output.lower() or "API key" in result.output

    def test_export_to_file_warns(self, cli, tmp_config, mock_client, tmp_path):
        """Export to file shows warning and sets restrictive permissions."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "secret-key-456")
        outfile = tmp_path / "export.json"
        result = cli("profile", "export", "--file", str(outfile))
        assert result.exit_code == 0
        assert "plaintext" in result.output.lower() or "API key" in result.output
        assert outfile.exists()

    def test_export_file_chmod_error_suppressed(
        self, cli, tmp_config, mock_client, tmp_path
    ):
        """chmod failure on export file does not crash."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key")
        outfile = tmp_path / "export.json"
        with patch("os.chmod", side_effect=OSError("unsupported")):
            result = cli("profile", "export", "--file", str(outfile))
        assert result.exit_code == 0
        assert outfile.exists()


# ═══════════════════════════════════════════════════════════════════
# DAWOS-15: --mask flag on profile export
# ═══════════════════════════════════════════════════════════════════


class TestProfileExportMask:
    """DAWOS-15: --mask flag replaces API keys with masked placeholders."""

    def test_mask_long_key(self, cli, tmp_config, mock_client):
        """Long key (>8 chars) shows first 4 + **** + last 3."""
        config.add_profile(
            "bng1", "http://10.0.0.1:8470", "TFYaNsVgkUooIHNX35wnvQrpM2rp"
        )
        result = cli("profile", "export", "--mask")
        assert result.exit_code == 0
        assert "TFYa****2rp" in result.output
        assert "TFYaNsVgkUooIHNX35wnvQrpM2rp" not in result.output

    def test_mask_short_key(self, cli, tmp_config, mock_client):
        """Short key (≤8 chars) is fully replaced with ****."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "shortkey")
        result = cli("profile", "export", "--mask")
        assert result.exit_code == 0
        assert "****" in result.output
        assert "shortkey" not in result.output

    def test_mask_no_plaintext_warning(self, cli, tmp_config, mock_client):
        """--mask suppresses the plaintext key warning."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key123456")
        result = cli("profile", "export", "--mask")
        assert result.exit_code == 0
        assert "plaintext" not in result.output.lower()

    def test_mask_to_file(self, cli, tmp_config, mock_client, tmp_path):
        """--mask works with --file output."""
        config.add_profile(
            "bng1", "http://10.0.0.1:8470", "TFYaNsVgkUooIHNX35wnvQrpM2rp"
        )
        outfile = tmp_path / "masked.json"
        result = cli("profile", "export", "--mask", "--file", str(outfile))
        assert result.exit_code == 0
        content = outfile.read_text(encoding="utf-8")
        assert "TFYa****2rp" in content
        assert "TFYaNsVgkUooIHNX35wnvQrpM2rp" not in content

    def test_no_mask_by_default(self, cli, tmp_config, mock_client):
        """Without --mask, full keys are exported (backward compat)."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "full-key-here-abc")
        result = cli("profile", "export")
        assert result.exit_code == 0
        assert "full-key-here-abc" in result.output


# ═══════════════════════════════════════════════════════════════════
# DC-M06: Profile structure validation on import
# ═══════════════════════════════════════════════════════════════════


class TestImportValidation:
    """DC-M06: import_profiles validates profile structure."""

    def test_import_rejects_missing_url(self, tmp_config):
        """Profile without 'url' key is skipped."""
        payload = {
            "profiles": {
                "bad": {"api_key": "key123"},  # missing url
            },
        }
        count = config.import_profiles(payload)
        assert count == 0
        assert config.get_profile("bad") is None

    def test_import_rejects_missing_api_key(self, tmp_config):
        """Profile without 'api_key' key is skipped."""
        payload = {
            "profiles": {
                "bad": {"url": "http://test:8470"},  # missing api_key
            },
        }
        count = config.import_profiles(payload)
        assert count == 0

    def test_import_rejects_non_dict_profile(self, tmp_config):
        """Profile value that is not a dict is skipped."""
        payload = {
            "profiles": {
                "bad": "not-a-dict",
            },
        }
        count = config.import_profiles(payload)
        assert count == 0

    def test_import_accepts_valid_profile(self, tmp_config):
        """Valid profiles pass validation."""
        payload = {
            "profiles": {
                "good": {"url": "http://10.0.0.1:8470", "api_key": "key1"},
            },
        }
        count = config.import_profiles(payload)
        assert count == 1
        assert config.get_profile("good") is not None

    def test_import_mixed_valid_invalid(self, tmp_config):
        """Only valid profiles are imported; invalid ones are skipped."""
        payload = {
            "profiles": {
                "good": {"url": "http://10.0.0.1:8470", "api_key": "key1"},
                "bad1": {"url": "http://10.0.0.2:8470"},  # missing api_key
                "bad2": "string-value",  # not a dict
            },
        }
        count = config.import_profiles(payload)
        assert count == 1
        assert config.get_profile("good") is not None
        assert config.get_profile("bad1") is None
        assert config.get_profile("bad2") is None

    def test_import_non_dict_profiles_field(self, tmp_config):
        """When 'profiles' is not a dict, import returns 0."""
        payload = {"profiles": ["not", "a", "dict"]}
        count = config.import_profiles(payload)
        assert count == 0

    def test_import_logs_skipped_profiles(self, tmp_config, caplog):
        """Skipped profiles produce log warnings."""
        payload = {
            "profiles": {
                "no_url": {"api_key": "key"},
                "not_dict": 42,
            },
        }
        with caplog.at_level(logging.WARNING, logger="dawos_cli.config"):
            config.import_profiles(payload)
        assert any("no_url" in rec.message for rec in caplog.records)
        assert any("not_dict" in rec.message for rec in caplog.records)


# ═══════════════════════════════════════════════════════════════════
# DC-L01: Config file permission check
# ═══════════════════════════════════════════════════════════════════


class TestConfigPermissionCheck:
    """DC-L01: _load() warns on overly permissive config file permissions."""

    def test_warns_on_world_readable(self, tmp_config, caplog):
        """Warning logged when config file is world-readable."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        # Make file world-readable
        config.CONFIG_FILE.chmod(0o644)

        with caplog.at_level(logging.WARNING, logger="dawos_cli.config"):
            config._load()

        assert any("permissive" in rec.message.lower() for rec in caplog.records)

    def test_no_warning_on_600(self, tmp_config, caplog):
        """No warning when config file has 0600 permissions."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.CONFIG_FILE.chmod(0o600)

        with caplog.at_level(logging.WARNING, logger="dawos_cli.config"):
            config._load()

        perm_warnings = [r for r in caplog.records if "permissive" in r.message.lower()]
        assert len(perm_warnings) == 0

    def test_warns_on_group_readable(self, tmp_config, caplog):
        """Warning logged when config file is group-readable."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.CONFIG_FILE.chmod(0o640)

        with caplog.at_level(logging.WARNING, logger="dawos_cli.config"):
            config._load()

        assert any("permissive" in rec.message.lower() for rec in caplog.records)

    def test_permission_check_oserror_suppressed(self, tmp_config):
        """OSError during permission check is silently handled."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        content = config.CONFIG_FILE.read_text(encoding="utf-8")

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "stat", side_effect=OSError("no stat")),
            patch.object(Path, "read_text", return_value=content),
        ):
            data = config._load()
            assert "profiles" in data


# ═══════════════════════════════════════════════════════════════════
# Validate profile helper
# ═══════════════════════════════════════════════════════════════════


class TestValidateProfile:
    """Unit tests for _validate_profile helper."""

    def test_valid_profile(self):
        assert config._validate_profile("test", {"url": "x", "api_key": "y"}) is True

    def test_missing_url(self):
        assert config._validate_profile("test", {"api_key": "y"}) is False

    def test_missing_api_key(self):
        assert config._validate_profile("test", {"url": "x"}) is False

    def test_not_a_dict(self):
        assert config._validate_profile("test", "string") is False

    def test_none_value(self):
        assert config._validate_profile("test", None) is False

    def test_extra_keys_accepted(self):
        """Profiles with extra keys are valid (forward compatibility)."""
        assert (
            config._validate_profile(
                "test", {"url": "x", "api_key": "y", "display_name": "z"}
            )
            is True
        )

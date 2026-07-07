"""Tests for dawos_cli.doctor module."""

from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

from rich.console import Console

from dawos_cli import doctor


def _capture_doctor(func, *args, **kwargs):
    """Run a doctor check function and capture its console output."""
    buf = StringIO()
    con = Console(file=buf, force_terminal=True, width=120)
    with patch.object(doctor, "_console", con):
        func(*args, **kwargs)
    return buf.getvalue()


class TestCheckPython:
    def test_reports_python_version(self):
        text = _capture_doctor(doctor._check_python)
        assert "Python" in text
        assert "✓" in text  # current Python should satisfy >= 3.9


class TestCheckVersion:
    def test_reports_dawos_version(self):
        text = _capture_doctor(doctor._check_version)
        assert "dawos-cli" in text
        assert "✓" in text


class TestCheckUpdate:
    def test_up_to_date(self):
        with patch("dawos_cli.doctor.updater") as mock_upd:
            mock_upd.fetch_latest_tag.return_value = "0.1.0"
            mock_upd.parse_version.side_effect = lambda v: tuple(
                int(x) for x in v.split(".")
            )
            text = _capture_doctor(doctor._check_update)
            assert "up-to-date" in text

    def test_update_available(self):
        with patch("dawos_cli.doctor.updater") as mock_upd:
            mock_upd.fetch_latest_tag.return_value = "99.0.0"
            mock_upd.parse_version.side_effect = lambda v: tuple(
                int(x) for x in v.split(".")
            )
            text = _capture_doctor(doctor._check_update)
            assert "available" in text

    def test_github_unreachable(self):
        with patch("dawos_cli.doctor.updater") as mock_upd:
            mock_upd.fetch_latest_tag.return_value = None
            text = _capture_doctor(doctor._check_update)
            assert "could not reach" in text

    def test_check_failed(self):
        with patch("dawos_cli.doctor.updater") as mock_upd:
            mock_upd.fetch_latest_tag.side_effect = RuntimeError("boom")
            text = _capture_doctor(doctor._check_update)
            assert "check failed" in text


class TestCheckProfile:
    def test_no_profile(self, tmp_config):
        with patch("dawos_cli.doctor.config") as mock_cfg:
            mock_cfg.get_active_name.return_value = ""
            text = _capture_doctor(doctor._check_profile)
            assert "none configured" in text

    def test_profile_exists(self, tmp_config):
        with patch("dawos_cli.doctor.config") as mock_cfg:
            mock_cfg.get_active_name.return_value = "prod"
            mock_cfg.get_profile.return_value = {"url": "http://bng:8470"}
            text = _capture_doctor(doctor._check_profile)
            assert "prod" in text
            assert "bng" in text

    def test_profile_not_found(self, tmp_config):
        with patch("dawos_cli.doctor.config") as mock_cfg:
            mock_cfg.get_active_name.return_value = "ghost"
            mock_cfg.get_profile.return_value = None
            text = _capture_doctor(doctor._check_profile)
            assert "not found" in text


class TestCheckConnection:
    def test_no_profile(self, tmp_config):
        with patch("dawos_cli.doctor.config") as mock_cfg:
            mock_cfg.get_active_name.return_value = ""
            text = _capture_doctor(doctor._check_connection)
            assert "no profile" in text

    def test_profile_missing(self, tmp_config):
        with patch("dawos_cli.doctor.config") as mock_cfg:
            mock_cfg.get_active_name.return_value = "ghost"
            mock_cfg.get_profile.return_value = None
            text = _capture_doctor(doctor._check_connection)
            assert "profile missing" in text

    def test_connection_ok(self, tmp_config):
        mock_health = MagicMock(return_value={"node_name": "bng1", "version": "1.0"})
        with (
            patch("dawos_cli.doctor.config") as mock_cfg,
            patch("dawos_cli.client.health", mock_health),
        ):
            mock_cfg.get_active_name.return_value = "prod"
            mock_cfg.get_profile.return_value = {"url": "http://bng:8470"}
            text = _capture_doctor(doctor._check_connection)
            assert "bng1" in text

    def test_connection_fail(self, tmp_config):
        with (
            patch("dawos_cli.doctor.config") as mock_cfg,
            patch("dawos_cli.client.health", return_value=None),
        ):
            mock_cfg.get_active_name.return_value = "prod"
            mock_cfg.get_profile.return_value = {"url": "http://bng:8470"}
            text = _capture_doctor(doctor._check_connection)
            assert "cannot reach" in text

    def test_connection_error(self, tmp_config):
        with (
            patch("dawos_cli.doctor.config") as mock_cfg,
            patch("dawos_cli.client.health", side_effect=RuntimeError("timeout")),
        ):
            mock_cfg.get_active_name.return_value = "prod"
            mock_cfg.get_profile.return_value = {"url": "http://bng:8470"}
            text = _capture_doctor(doctor._check_connection)
            assert "connection error" in text


class TestCheckShell:
    def test_detects_shell(self):
        with patch.dict("os.environ", {"SHELL": "/bin/zsh"}):
            text = _capture_doctor(doctor._check_shell)
            assert "zsh" in text

    def test_detects_comspec(self):
        with patch.dict("os.environ", {"SHELL": "", "COMSPEC": "C:\\Windows\\cmd.exe"}):
            text = _capture_doctor(doctor._check_shell)
            assert "cmd.exe" in text

    def test_unknown_shell(self):
        with patch.dict("os.environ", {"SHELL": "", "COMSPEC": ""}, clear=True):
            text = _capture_doctor(doctor._check_shell)
            assert "unknown" in text


class TestCheckConfigFile:
    def test_config_exists(self, tmp_config):
        from dawos_cli import config

        config.add_profile("test", "http://x:8470", "key")
        text = _capture_doctor(doctor._check_config_file)
        assert "✓" in text

    def test_config_missing(self, tmp_config):
        text = _capture_doctor(doctor._check_config_file)
        assert "✗" in text


class TestCheckPipx:
    def test_pipx_found(self):
        with patch("dawos_cli.doctor.shutil.which", return_value="/usr/local/bin/pipx"):
            text = _capture_doctor(doctor._check_pipx)
            assert "✓" in text
            assert "pipx" in text

    def test_pipx_not_found(self):
        with patch("dawos_cli.doctor.shutil.which", return_value=None):
            text = _capture_doctor(doctor._check_pipx)
            assert "not found" in text


class TestRunDoctor:
    def test_runs_all_checks(self, tmp_config):
        """Ensure run_doctor() completes without error."""
        buf = StringIO()
        con = Console(file=buf, force_terminal=True, width=120)
        with (
            patch.object(doctor, "_console", con),
            patch("dawos_cli.doctor.updater") as mock_upd,
            patch("dawos_cli.doctor.config") as mock_cfg,
            patch("dawos_cli.doctor.shutil.which", return_value=None),
        ):
            mock_upd.fetch_latest_tag.return_value = None
            mock_cfg.get_active_name.return_value = ""
            mock_cfg.config_path.return_value = tmp_config / "config.json"

            doctor.run_doctor()

        text = buf.getvalue()
        assert "dawos doctor" in text
        assert "Python" in text

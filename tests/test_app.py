"""Tests for dawos_cli.app module — root app, callbacks, top-level commands."""

from __future__ import annotations

from unittest.mock import patch

from dawos_cli import __version__, state


class TestVersionCallback:
    def test_version_flag(self, cli, mock_client):
        result = cli("--version")
        assert __version__ in result.output

    def test_version_command(self, cli, mock_client):
        result = cli("version")
        assert result.exit_code == 0
        assert __version__ in result.output


class TestMainCallback:
    def test_json_flag(self, cli, mock_client):
        result = cli("-j", "system", "info")
        assert result.exit_code == 0
        assert state.current.json_output is True

    def test_profile_flag(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("prod", "http://prod:8470", "key_prod")
        result = cli("--profile", "prod", "system", "info")
        assert result.exit_code == 0

    def test_no_args_shows_help(self, runner):
        from dawos_cli.app import app

        result = runner.invoke(app, [])
        # Typer returns exit code 0 or 2 for no_args_is_help
        assert result.exit_code in (0, 2)
        assert "dawos" in result.output.lower() or "usage" in result.output.lower()


class TestStatusCommand:
    def test_status_ok(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "healthy"}
        result = cli("status")
        assert result.exit_code == 0

    def test_status_connection_error(self, cli, mock_client):
        mock_client["get"].side_effect = SystemExit(1)
        result = cli("status")
        assert result.exit_code == 0  # caught SystemExit


class TestTopCommand:
    def test_top_invokes_dashboard(self, cli, mock_client):
        with patch("dawos_cli.app.dashboard.run_dashboard") as mock_rd:
            result = cli("top")
            assert result.exit_code == 0
            mock_rd.assert_called_once_with(interval=2.0)

    def test_top_custom_interval(self, cli, mock_client):
        with patch("dawos_cli.app.dashboard.run_dashboard") as mock_rd:
            result = cli("top", "--interval", "5")
            assert result.exit_code == 0
            mock_rd.assert_called_once_with(interval=5.0)


class TestMainEntryPoint:
    def test_main_calls_app(self):
        with patch("dawos_cli.app.app") as mock_app:
            from dawos_cli.app import main

            main()
            mock_app.assert_called_once()

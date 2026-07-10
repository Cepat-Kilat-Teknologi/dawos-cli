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

    def test_format_csv(self, cli, mock_client):
        result = cli("--format", "csv", "system", "info")
        assert result.exit_code == 0
        assert state.current.output_format == "csv"

    def test_format_yaml(self, cli, mock_client):
        result = cli("--format", "yaml", "system", "info")
        assert result.exit_code == 0
        assert state.current.output_format == "yaml"

    def test_format_invalid(self, cli, mock_client):
        result = cli("--format", "xml", "system", "info")
        assert result.exit_code == 1

    def test_format_shorthand(self, cli, mock_client):
        result = cli("-F", "json", "system", "info")
        assert result.exit_code == 0
        assert state.current.output_format == "json"


class TestStatusCommand:
    def test_status_ok(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "healthy"}
        result = cli("status")
        assert result.exit_code == 0

    def test_status_connection_error(self, cli, mock_client):
        """Connection failure must propagate a non-zero exit code."""
        mock_client["get"].side_effect = SystemExit(1)
        result = cli("status")
        assert result.exit_code == 1


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


class TestDoctorCommand:
    def test_doctor_runs(self, cli, mock_client):
        with patch("dawos_cli.doctor.run_doctor") as mock_doc:
            result = cli("doctor")
            assert result.exit_code == 0
            mock_doc.assert_called_once()


class TestShellCommand:
    def test_shell_runs(self, cli, mock_client):
        with patch("dawos_cli.shell.run_shell", side_effect=SystemExit(0)):
            result = cli("shell")
            assert result.exit_code == 0


class TestMainEntryPoint:
    def test_main_calls_app(self):
        with patch("dawos_cli.app.app") as mock_app:
            from dawos_cli.app import main

            main()
            mock_app.assert_called_once()


class TestCommandAliases:
    def test_alias_s(self, cli, mock_client):
        mock_client["get"].return_value = []
        result = cli("s", "list")
        assert result.exit_code == 0

    def test_alias_sys(self, cli, mock_client):
        result = cli("sys", "info")
        assert result.exit_code == 0


class TestProfileExportImport:
    def test_export_all(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        result = cli("profile", "export")
        assert result.exit_code == 0
        assert "dawos_cli_export" in result.output

    def test_export_single(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        result = cli("profile", "export", "--name", "bng1")
        assert result.exit_code == 0
        assert "bng1" in result.output

    def test_export_not_found(self, cli, mock_client, tmp_config):
        result = cli("profile", "export", "--name", "nope")
        assert result.exit_code == 1

    def test_export_to_file(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        out_file = tmp_config / "export.json"
        result = cli("profile", "export", "--file", str(out_file))
        assert result.exit_code == 0
        assert out_file.exists()

    def test_import_file(self, cli, mock_client, tmp_config):
        import json

        from dawos_cli import config

        payload = {
            "dawos_cli_export": True,
            "version": 1,
            "active_profile": "bng1",
            "profiles": {
                "bng1": {
                    "url": "http://10.0.0.1:8470",
                    "api_key": "key1",
                    "display_name": "bng1",
                }
            },
        }
        import_file = tmp_config / "import.json"
        import_file.write_text(json.dumps(payload))
        result = cli("profile", "import", str(import_file))
        assert result.exit_code == 0
        assert config.get_profile("bng1") is not None

    def test_import_file_not_found(self, cli, mock_client, tmp_config):
        result = cli("profile", "import", "/nonexistent/path.json")
        assert result.exit_code == 1

    def test_import_invalid_json(self, cli, mock_client, tmp_config):
        bad_file = tmp_config / "bad.json"
        bad_file.write_text("not json at all{{{")
        result = cli("profile", "import", str(bad_file))
        assert result.exit_code == 1

    def test_import_replace_mode(self, cli, mock_client, tmp_config):
        import json

        from dawos_cli import config

        config.add_profile("old", "http://old:8470", "key_old")
        payload = {
            "profiles": {
                "new": {
                    "url": "http://new:8470",
                    "api_key": "key_new",
                    "display_name": "new",
                }
            }
        }
        import_file = tmp_config / "import.json"
        import_file.write_text(json.dumps(payload))
        result = cli("profile", "import", str(import_file), "--replace")
        assert result.exit_code == 0
        assert config.get_profile("old") is None
        assert config.get_profile("new") is not None

    def test_import_empty_profiles(self, cli, mock_client, tmp_config):
        import json

        payload = {"profiles": {}}
        import_file = tmp_config / "empty.json"
        import_file.write_text(json.dumps(payload))
        result = cli("profile", "import", str(import_file))
        assert result.exit_code == 0

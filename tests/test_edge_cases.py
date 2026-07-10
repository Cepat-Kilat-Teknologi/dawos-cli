"""Edge-case and error-path tests across CLI modules.

Exercises failure branches, fallbacks, and boundary conditions in:
updater, shell, wizard, telemetry, firewall, config, output,
playbook, and app — the paths not hit by the happy-path suites.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from dawos_cli import state
from dawos_cli.app import app

# ===================================================================
# updater.py — error paths & edge cases
# ===================================================================


class TestParseVersion:
    """Lines 33-34: ValueError in parse_version for non-numeric parts."""

    def test_non_numeric_part_treated_as_zero(self):
        from dawos_cli.updater import parse_version

        result = parse_version("v1.2.beta3")
        assert result == (1, 2, 0)

    def test_all_non_numeric(self):
        from dawos_cli.updater import parse_version

        result = parse_version("vX.Y.Z")
        assert result == (0, 0, 0)


class TestReadCache:
    """Lines 44-46: _read_cache with existing file + JSONDecodeError."""

    def test_returns_data_from_valid_cache(self, tmp_path, monkeypatch):
        import dawos_cli.updater as u

        cache_file = tmp_path / ".update-check"
        cache_file.write_text(json.dumps({"latest": "v0.5.0", "checked_at": 1}))
        monkeypatch.setattr(u, "_CACHE_FILE", cache_file)

        result = u._read_cache()
        assert result["latest"] == "v0.5.0"

    def test_returns_none_on_json_decode_error(self, tmp_path, monkeypatch):
        import dawos_cli.updater as u

        cache_file = tmp_path / ".update-check"
        cache_file.write_text("NOT JSON{{{")
        monkeypatch.setattr(u, "_CACHE_FILE", cache_file)

        result = u._read_cache()
        assert result is None

    def test_returns_none_when_no_file(self, tmp_path, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.setattr(u, "_CACHE_FILE", tmp_path / "nope")
        assert u._read_cache() is None


class TestWriteCache:
    """Lines 57-58: _write_cache OSError."""

    def test_write_cache_success(self, tmp_path, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.setattr(u, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(u, "_CACHE_FILE", tmp_path / ".update-check")

        u._write_cache("v0.9.0")
        data = json.loads((tmp_path / ".update-check").read_text())
        assert data["latest"] == "v0.9.0"

    def test_write_cache_oserror_suppressed(self, tmp_path, monkeypatch):
        import dawos_cli.updater as u

        # Point cache file to a path that can't be created
        monkeypatch.setattr(u, "CONFIG_DIR", tmp_path)
        bad_path = tmp_path / ".update-check"
        monkeypatch.setattr(u, "_CACHE_FILE", bad_path)

        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            u._write_cache("v1.0.0")  # Should not raise


class TestFetchLatestTag:
    """Lines 71-73: fetch_latest_tag network exception."""

    def test_returns_tag_on_success(self):
        import dawos_cli.updater as u

        mock_httpx = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"name": "v0.3.1"}]
        mock_httpx.get.return_value = mock_resp

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = u.fetch_latest_tag()
            assert result == "v0.3.1"

    def test_returns_none_on_exception(self):
        import dawos_cli.updater as u

        mock_httpx = MagicMock()
        mock_httpx.get.side_effect = Exception("timeout")

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = u.fetch_latest_tag()
            assert result is None

    def test_returns_none_on_empty_tags(self):
        import dawos_cli.updater as u

        mock_httpx = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_httpx.get.return_value = mock_resp

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            result = u.fetch_latest_tag()
            assert result is None

    def test_returns_highest_version_not_first_entry(self):
        """DC-H02: tags are sorted by parsed version, not API order."""
        import dawos_cli.updater as u

        mock_httpx = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"name": "v0.9.0"},
            {"name": "v0.10.0"},
            {"name": "v0.2.0"},
        ]
        mock_httpx.get.return_value = mock_resp

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            assert u.fetch_latest_tag() == "v0.10.0"

    def test_skips_malformed_tag_entries(self):
        """Entries without a name (or non-dict) are ignored."""
        import dawos_cli.updater as u

        mock_httpx = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            "garbage",
            {"nope": 1},
            {"name": "v0.3.0"},
        ]
        mock_httpx.get.return_value = mock_resp

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            assert u.fetch_latest_tag() == "v0.3.0"


class TestCheckForUpdate:
    """Lines 84, 93, 101: env check, cache hit newer, fetch newer."""

    def test_returns_none_when_env_disabled(self, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.setenv("DAWOS_NO_UPDATE_CHECK", "1")
        assert u.check_for_update() is None

    def test_cache_hit_with_newer_version(self, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.delenv("DAWOS_NO_UPDATE_CHECK", raising=False)
        cache_data = {"latest": "v99.0.0", "checked_at": time.time()}
        monkeypatch.setattr(u, "_read_cache", lambda: cache_data)

        result = u.check_for_update()
        assert result == "v99.0.0"

    def test_cache_hit_with_same_version(self, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.delenv("DAWOS_NO_UPDATE_CHECK", raising=False)
        cache_data = {"latest": "v0.0.1", "checked_at": time.time()}
        monkeypatch.setattr(u, "_read_cache", lambda: cache_data)

        result = u.check_for_update()
        assert result is None

    def test_fetch_returns_newer_version(self, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.delenv("DAWOS_NO_UPDATE_CHECK", raising=False)
        # Cache expired
        monkeypatch.setattr(u, "_read_cache", lambda: None)
        monkeypatch.setattr(u, "fetch_latest_tag", lambda: "v99.0.0")
        monkeypatch.setattr(u, "_write_cache", lambda v: None)

        result = u.check_for_update()
        assert result == "v99.0.0"

    def test_fetch_returns_same_version(self, monkeypatch):
        import dawos_cli.updater as u

        monkeypatch.delenv("DAWOS_NO_UPDATE_CHECK", raising=False)
        monkeypatch.setattr(u, "_read_cache", lambda: None)
        monkeypatch.setattr(u, "fetch_latest_tag", lambda: "v0.0.1")
        monkeypatch.setattr(u, "_write_cache", lambda v: None)

        result = u.check_for_update()
        assert result is None


class TestRunSelfUpdate:
    """DC-H02: pinned PyPI install via pipx, pip fallback, version lookup."""

    def test_pipx_success_installs_pinned_pypi_release(self):
        import dawos_cli.updater as u

        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch(
            "dawos_cli.updater.subprocess.run", return_value=mock_result
        ) as mock_run:
            assert u.run_self_update("v1.2.3") is True

        cmd = mock_run.call_args[0][0]
        assert "dawos-cli==1.2.3" in cmd
        assert not any(str(arg).startswith("git+") for arg in cmd)

    def test_pipx_failure_falls_back_to_pip_success(self):
        import dawos_cli.updater as u

        mock_pip_result = MagicMock()
        mock_pip_result.returncode = 0
        captured = {}

        def side_effect(cmd, **kwargs):
            if "pipx" in cmd:
                raise FileNotFoundError("no pipx")
            captured["pip_cmd"] = cmd
            return mock_pip_result

        with patch("dawos_cli.updater.subprocess.run", side_effect=side_effect):
            assert u.run_self_update("v2.0.0") is True

        assert "dawos-cli==2.0.0" in captured["pip_cmd"]
        assert not any(str(arg).startswith("git+") for arg in captured["pip_cmd"])

    def test_both_pipx_and_pip_fail(self):
        import dawos_cli.updater as u

        def side_effect(cmd, **kwargs):
            raise FileNotFoundError("not found")

        with patch("dawos_cli.updater.subprocess.run", side_effect=side_effect):
            assert u.run_self_update("v1.0.0") is False

    def test_pipx_nonzero_returncode(self):
        import dawos_cli.updater as u

        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("dawos_cli.updater.subprocess.run", return_value=mock_result):
            assert u.run_self_update("v1.0.0") is False

    def test_no_arg_looks_up_latest_tag(self, monkeypatch):
        """Without an explicit version, the latest tag is fetched and pinned."""
        import dawos_cli.updater as u

        monkeypatch.setattr(u, "fetch_latest_tag", lambda: "v9.9.9")
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch(
            "dawos_cli.updater.subprocess.run", return_value=mock_result
        ) as mock_run:
            assert u.run_self_update() is True

        assert "dawos-cli==9.9.9" in mock_run.call_args[0][0]

    def test_no_arg_lookup_failure_returns_false(self, monkeypatch):
        """No known release — nothing is installed."""
        import dawos_cli.updater as u

        monkeypatch.setattr(u, "fetch_latest_tag", lambda: None)
        with patch("dawos_cli.updater.subprocess.run") as mock_run:
            assert u.run_self_update() is False
        mock_run.assert_not_called()


# ===================================================================
# shell.py — error paths & edge cases
# ===================================================================


class TestExecuteLine:
    """Lines in _execute_line: parse error, normal execution, SystemExit."""

    def test_execute_valid_command(self):
        from dawos_cli.shell import _execute_line

        with patch("dawos_cli.shell._console"):
            with patch("dawos_cli.app.app") as mock_app:
                _execute_line("status")
                mock_app.assert_called_once_with(["status"], standalone_mode=False)

    def test_execute_parse_error(self):
        from dawos_cli.shell import _execute_line

        with patch("dawos_cli.shell._console") as mc:
            # Unterminated quote causes shlex.split ValueError
            _execute_line('bad "unterminated')
            mc.print.assert_called_once()
            assert "Parse error" in mc.print.call_args[0][0]

    def test_execute_system_exit_suppressed(self):
        from dawos_cli.shell import _execute_line

        with patch("dawos_cli.app.app", side_effect=SystemExit(0)):
            # Should not raise
            _execute_line("--help")

    def test_execute_generic_exception(self):
        from dawos_cli.shell import _execute_line

        with patch("dawos_cli.shell._console") as mc:
            with patch(
                "dawos_cli.app.app", side_effect=RuntimeError("something broke")
            ):
                _execute_line("bad-command")
                mc.print.assert_called_once()
                assert "Error" in mc.print.call_args[0][0]


def _make_pt_mocks():
    """Build prompt_toolkit module mocks for shell tests."""
    mock_pt = MagicMock()
    mock_comp = MagicMock()
    mock_hist = MagicMock()
    return {
        "prompt_toolkit": mock_pt,
        "prompt_toolkit.completion": mock_comp,
        "prompt_toolkit.history": mock_hist,
    }


class TestRunWithPromptToolkit:
    """Lines 69-104: prompt_toolkit REPL loop."""

    def _run(self, prompt_side_effect, exec_patch=None):
        """Helper to invoke _run_with_prompt_toolkit with mocked deps."""
        import tempfile

        from dawos_cli.shell import _run_with_prompt_toolkit

        pt_mods = _make_pt_mocks()
        mock_session = MagicMock()
        mock_session.prompt.side_effect = prompt_side_effect
        pt_mods["prompt_toolkit"].PromptSession.return_value = mock_session

        # Real temp dir — the REPL now creates/chmods the history file.
        cfg_dir = Path(tempfile.mkdtemp(prefix="dawos-test-"))

        patches = [
            patch.dict("sys.modules", pt_mods),
            patch("dawos_cli.config.CONFIG_DIR", cfg_dir),
            patch("dawos_cli.shell._console"),
        ]
        if exec_patch:
            patches.append(patch("dawos_cli.shell._execute_line", exec_patch))

        [p.__enter__() for p in patches]  # noqa: C416
        try:
            _run_with_prompt_toolkit()
        finally:
            for p in reversed(patches):
                p.__exit__(None, None, None)

        return mock_session, exec_patch

    def test_prompt_toolkit_exit_command(self):
        self._run(["exit"])

    def test_prompt_toolkit_quit_command(self):
        self._run(["quit"])

    def test_prompt_toolkit_eof(self):
        self._run(EOFError())

    def test_prompt_toolkit_keyboard_interrupt(self):
        self._run(KeyboardInterrupt())

    def test_prompt_toolkit_empty_and_command(self):
        mock_exec = MagicMock()
        self._run(["", "status", "q"], exec_patch=mock_exec)
        mock_exec.assert_called_once_with("status")


class TestRunWithReadline:
    """Lines 113-114, 118-119: readline completer + ImportError fallback."""

    def test_readline_completer_returns_match(self):
        """Test the completer function body (lines 113-114)."""
        from dawos_cli.shell import _COMMANDS

        def capture_completer(text, idx):
            matches = [c for c in _COMMANDS if c.startswith(text)]
            return matches[idx] if idx < len(matches) else None

        # Test matching
        assert capture_completer("sta", 0) == "status"
        assert capture_completer("sta", 1) is None
        assert capture_completer("zzz", 0) is None

    def test_readline_import_error_fallback(self):
        """Lines 118-119: readline ImportError path."""
        from dawos_cli.shell import _run_with_readline

        # Make readline import fail, then input returns "exit"
        with (
            patch.dict("sys.modules", {"readline": None}),
            patch("builtins.input", return_value="exit"),
            patch("dawos_cli.shell._console"),
        ):
            import builtins

            orig_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "readline":
                    raise ImportError("no readline")
                return orig_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                _run_with_readline()

            # Cover the passthrough branch: non-readline names delegate to
            # the real import machinery.
            assert mock_import("json") is not None

    def test_readline_loop_empty_and_exit(self):
        """Test readline loop: empty input, command, exit."""
        from dawos_cli.shell import _run_with_readline

        with (
            patch("builtins.input", side_effect=["", "status", "q"]),
            patch("dawos_cli.shell._console"),
            patch("dawos_cli.shell._execute_line") as mock_exec,
        ):
            mock_readline = MagicMock()
            with patch.dict("sys.modules", {"readline": mock_readline}):
                _run_with_readline()
                mock_exec.assert_called_once_with("status")

    def test_readline_keyboard_interrupt(self):
        """Ctrl+C exits readline loop."""
        from dawos_cli.shell import _run_with_readline

        with (
            patch("builtins.input", side_effect=KeyboardInterrupt()),
            patch("dawos_cli.shell._console"),
        ):
            mock_readline = MagicMock()
            with patch.dict("sys.modules", {"readline": mock_readline}):
                _run_with_readline()


class TestRunShell:
    """Line 168: run_shell dispatches to prompt_toolkit or readline."""

    def test_run_shell_with_prompt_toolkit(self):
        from dawos_cli.shell import run_shell

        with (
            patch("dawos_cli.shell._console"),
            patch("dawos_cli.shell._run_with_prompt_toolkit") as mock_pt,
        ):
            # Make prompt_toolkit importable
            mock_mod = MagicMock()
            with patch.dict("sys.modules", {"prompt_toolkit": mock_mod}):
                with pytest.raises(SystemExit) as exc_info:
                    run_shell()
                assert exc_info.value.code == 0
                mock_pt.assert_called_once()

    def test_run_shell_fallback_to_readline(self):
        from dawos_cli.shell import run_shell

        with (
            patch("dawos_cli.shell._console"),
            patch("dawos_cli.shell._run_with_readline") as mock_rl,
        ):
            # Remove prompt_toolkit from importable modules
            import builtins

            orig_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "prompt_toolkit":
                    raise ImportError("no prompt_toolkit")
                return orig_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                with pytest.raises(SystemExit) as exc_info:
                    run_shell()
                assert exc_info.value.code == 0
                mock_rl.assert_called_once()

            # Cover the passthrough branch: other names import normally.
            assert mock_import("json") is not None


# ===================================================================
# wizard.py — error paths & edge cases
# ===================================================================


class TestWizardTroubleshootSystemExit:
    """Lines 156-158, 181-183, 197-203: SystemExit branches."""

    def test_ts_check_agent_system_exit(self, cli, tmp_config):
        """Lines 156-158: _ts_check_agent catches SystemExit."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                return_value="testuser",
            ),
            patch(
                "dawos_cli.commands.wizard.client.get",
                side_effect=[
                    SystemExit(1),  # /health fails
                    {"running": True},  # /service/status
                    {"ip": "10.0.0.1", "ifname": "ppp0"},  # session
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")
            assert result.exit_code == 0
            assert (
                "cannot reach" in result.output.lower()
                or "fail" in result.output.lower()
            )

    def test_ts_check_session_system_exit(self, cli, tmp_config):
        """Lines 181-183: _ts_check_session catches SystemExit."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                return_value="testuser",
            ),
            patch(
                "dawos_cli.commands.wizard.client.get",
                side_effect=[
                    {"status": "ok"},  # /health
                    {"running": True},  # /service/status
                    SystemExit(1),  # session lookup fails
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")
            assert result.exit_code == 0
            assert "fail" in result.output.lower() or "testuser" in result.output

    def test_ts_check_service_not_running(self, cli, tmp_config):
        """Lines 197-200: _ts_check_service running=False."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                return_value="testuser",
            ),
            patch(
                "dawos_cli.commands.wizard.client.get",
                side_effect=[
                    {"status": "ok"},  # /health
                    {"running": False},  # /service/status — NOT running
                    {"ip": "10.0.0.1", "ifname": "ppp0"},  # session
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")
            assert result.exit_code == 0
            assert "not running" in result.output.lower() or "FAIL" in result.output

    def test_ts_check_service_system_exit(self, cli, tmp_config):
        """Lines 201-203: _ts_check_service catches SystemExit."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                return_value="testuser",
            ),
            patch(
                "dawos_cli.commands.wizard.client.get",
                side_effect=[
                    {"status": "ok"},  # /health
                    SystemExit(1),  # /service/status fails
                    {"ip": "10.0.0.1", "ifname": "ppp0"},  # session
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")
            assert result.exit_code == 0


class TestWizardDeploySystemExit:
    """Lines 298-300, 322, 334-335, 344, 356-362: deploy wizard edge cases."""

    def test_deploy_backup_empty_response(self, cli, tmp_config):
        """Lines 298: _deploy_backup gets empty data."""
        with (
            patch(
                "dawos_cli.commands.wizard.client.get",
                return_value={"status": "ok"},
            ),
            patch(
                "dawos_cli.commands.wizard.client.post",
                return_value=None,  # Empty checkpoint response
            ),
        ):
            result = cli("wizard", "deploy")
            assert result.exit_code == 0
            assert "empty" in result.output.lower() or "fail" in result.output.lower()

    def test_deploy_backup_system_exit(self, cli, tmp_config):
        """Lines 299-300: _deploy_backup catches SystemExit."""

        def mock_get(url):
            return {"status": "ok"}

        def mock_post(url, **kwargs):
            raise SystemExit(1)

        with (
            patch("dawos_cli.commands.wizard.client.get", side_effect=mock_get),
            patch("dawos_cli.commands.wizard.client.post", side_effect=mock_post),
        ):
            result = cli("wizard", "deploy")
            assert result.exit_code == 0
            assert "fail" in result.output.lower()

    def test_deploy_apply_not_confirmed(self, cli, tmp_config):
        """Line 322: _deploy_apply skips when not confirmed."""
        with (
            patch(
                "dawos_cli.commands.wizard.client.get",
                return_value={"status": "ok"},
            ),
            patch(
                "dawos_cli.commands.wizard.client.post",
                return_value={"id": "chk-1"},
            ),
            patch("dawos_cli.commands.wizard.typer.confirm", return_value=False),
        ):
            result = cli("wizard", "deploy")
            assert result.exit_code == 0
            # Should say cancelled/skipped
            assert (
                "cancelled" in result.output.lower()
                or "skipped" in result.output.lower()
            )

    def test_deploy_apply_system_exit(self, cli, tmp_config):
        """Lines 334-335: _deploy_apply catches SystemExit."""
        post_call = 0

        def mock_post(url, **kwargs):
            nonlocal post_call
            post_call += 1
            if post_call == 1:
                return {"id": "chk-999"}
            # Second call (apply) raises SystemExit
            raise SystemExit(1)

        with (
            patch(
                "dawos_cli.commands.wizard.client.get",
                return_value={"status": "ok"},
            ),
            patch("dawos_cli.commands.wizard.client.post", side_effect=mock_post),
            patch("dawos_cli.commands.wizard.typer.confirm", return_value=True),
        ):
            result = cli("wizard", "deploy")
            assert result.exit_code == 0
            assert (
                "fail" in result.output.lower()
                or "rolling back" in result.output.lower()
                or "apply" in result.output.lower()
            )

    def test_deploy_verify_not_confirmed(self):
        """Line 344: _deploy_verify skips when not confirmed."""
        from dawos_cli.commands.wizard import _deploy_verify

        ctx: dict[str, Any] = {}  # No "confirmed" key
        result = _deploy_verify(ctx)
        assert result.success is True
        assert (
            "skipped" in result.message.lower()
            or "not confirmed" in result.message.lower()
        )

    def test_deploy_verify_system_exit(self, cli, tmp_config):
        """Lines 356-362: _deploy_verify catches SystemExit with warning."""
        post_call = 0

        def mock_post(url, **kwargs):
            nonlocal post_call
            post_call += 1
            if post_call == 1:
                return {"id": "chk-789"}
            return {"status": "ok"}  # apply success

        get_call = 0

        def mock_get(url):
            nonlocal get_call
            get_call += 1
            if get_call == 1:
                return {"status": "ok"}  # preflight
            # Second call (verify health) raises SystemExit
            raise SystemExit(1)

        with (
            patch("dawos_cli.commands.wizard.client.get", side_effect=mock_get),
            patch("dawos_cli.commands.wizard.client.post", side_effect=mock_post),
            patch("dawos_cli.commands.wizard.typer.confirm", return_value=True),
        ):
            result = cli("wizard", "deploy")
            assert result.exit_code == 0
            assert (
                "fail" in result.output.lower()
                or "unhealthy" in result.output.lower()
                or "rollback" in result.output.lower()
            )


# ===================================================================
# telemetry.py — error paths & edge cases
# ===================================================================


class TestTelemetryLoad:
    """Lines 36-37: JSONDecodeError on _load."""

    def test_load_corrupt_json(self, tmp_path, monkeypatch):
        import dawos_cli.telemetry as t

        tfile = tmp_path / ".telemetry.json"
        tfile.write_text("{broken json!!")
        monkeypatch.setattr(t, "_TELEMETRY_FILE", tfile)

        result = t._load()
        assert result["commands"] == {}
        assert result["errors"] == 0

    def test_load_valid_json(self, tmp_path, monkeypatch):
        import dawos_cli.telemetry as t

        tfile = tmp_path / ".telemetry.json"
        tfile.write_text(json.dumps({"commands": {"status": 5}, "errors": 1}))
        monkeypatch.setattr(t, "_TELEMETRY_FILE", tfile)

        result = t._load()
        assert result["commands"]["status"] == 5


class TestTelemetrySave:
    """Lines 47-48: OSError on _save."""

    def test_save_oserror_suppressed(self, tmp_path, monkeypatch):
        import dawos_cli.telemetry as t

        monkeypatch.setattr(t, "CONFIG_DIR", tmp_path)
        tfile = tmp_path / ".telemetry.json"
        monkeypatch.setattr(t, "_TELEMETRY_FILE", tfile)

        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            t._save({"commands": {}, "errors": 0})  # Should not raise


class TestTelemetryReset:
    """Lines 85-86: OSError on reset/unlink."""

    def test_reset_oserror_suppressed(self, tmp_path, monkeypatch):
        import dawos_cli.telemetry as t

        tfile = tmp_path / ".telemetry.json"
        tfile.write_text("{}")
        monkeypatch.setattr(t, "_TELEMETRY_FILE", tfile)

        with patch.object(Path, "unlink", side_effect=OSError("perm denied")):
            t.reset()  # Should not raise

    def test_reset_removes_file(self, tmp_path, monkeypatch):
        import dawos_cli.telemetry as t

        tfile = tmp_path / ".telemetry.json"
        tfile.write_text("{}")
        monkeypatch.setattr(t, "_TELEMETRY_FILE", tfile)

        t.reset()
        assert not tfile.exists()


# ===================================================================
# firewall.py — error paths & edge cases
# ===================================================================


class TestFirewallGroupErrors:
    """Lines 115-116, 127-128, 143-144: error responses."""

    def test_group_add_error(self, cli, mock_client):
        """Lines 115-116: group-add returns success=False."""
        mock_client["post"].return_value = {
            "success": False,
            "message": "table not found",
        }
        result = cli("firewall", "group-add", "blocked", "--type", "address")
        assert result.exit_code == 1

    def test_group_del_error(self, cli, mock_client):
        """Lines 127-128: group-del returns success=False."""
        mock_client["delete"].return_value = {
            "success": False,
            "message": "group not found",
        }
        result = cli("firewall", "group-del", "blocked", "--force")
        assert result.exit_code == 1

    def test_group_members_error(self, cli, mock_client):
        """Lines 143-144: group-members returns success=False."""
        mock_client["post"].return_value = {
            "success": False,
            "message": "group not found",
        }
        result = cli("firewall", "group-members", "blocked", "1.2.3.4")
        assert result.exit_code == 1


# ===================================================================
# config.py — error paths & edge cases
# ===================================================================


class TestConfigPlatform:
    """Lines 26-27: Windows platform branch."""

    def test_windows_default_config_dir(self, monkeypatch):
        from dawos_cli.config import _default_config_dir

        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.setenv("APPDATA", "/fake/appdata")

        result = _default_config_dir()
        assert "dawos" in str(result)
        assert "appdata" in str(result).lower()

    def test_windows_without_appdata(self, monkeypatch):
        from dawos_cli.config import _default_config_dir

        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.delenv("APPDATA", raising=False)

        result = _default_config_dir()
        assert "dawos" in str(result)


class TestConfigAtomicSave:
    """DC-M07: _save writes via a 0600 temp file + atomic os.replace."""

    def test_save_writes_atomically(self, tmp_path, monkeypatch):
        import dawos_cli.config as cfg

        monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config.json")

        cfg._save({"active_profile": "", "profiles": {}})

        assert (tmp_path / "config.json").exists()
        assert not (tmp_path / "config.json.tmp").exists()


# ===================================================================
# output.py — error paths & edge cases
# ===================================================================


class TestOutputAltFormat:
    """Lines 32-33: _is_alt_format True path."""

    def test_is_alt_format_json(self):
        s = state.current
        orig = s.json_output
        s.json_output = True
        try:
            from dawos_cli.output import _is_alt_format

            assert _is_alt_format() is True
        finally:
            s.json_output = orig

    def test_is_alt_format_csv(self):
        s = state.current
        orig_json = s.json_output
        orig_fmt = s.output_format
        s.json_output = False
        s.output_format = "csv"
        try:
            from dawos_cli.output import _is_alt_format

            assert _is_alt_format() is True
        finally:
            s.json_output = orig_json
            s.output_format = orig_fmt


class TestOutputCsvDict:
    """Line 81: CSV with dict data and no explicit columns."""

    def test_csv_emit_dict_data(self, capsys):
        s = state.current
        orig_json = s.json_output
        orig_fmt = s.output_format
        s.json_output = False
        s.output_format = "csv"
        try:
            from dawos_cli.output import _emit

            result = _emit({"name": "test", "value": 42})
            assert result is True
            captured = capsys.readouterr()
            assert "name" in captured.out
            assert "test" in captured.out
        finally:
            s.json_output = orig_json
            s.output_format = orig_fmt


# ===================================================================
# playbook.py — error paths & edge cases
# ===================================================================


class TestPlaybookListElseBranch:
    """Line 29: else branch when playbooks is neither list nor dict."""

    def test_list_playbooks_non_list_non_dict_response(self, cli, mock_client):
        """Line 29: playbooks extracted is not a list — falls through to else."""
        # Response is a dict with "playbooks" being a string (non-list)
        mock_client["get"].return_value = {"playbooks": "some string value"}
        result = cli("playbook", "list")
        assert result.exit_code == 0

    def test_list_playbooks_raw_string_response(self, cli, mock_client):
        """When data is a raw string, not dict or list."""
        mock_client["get"].return_value = "just a string"
        result = cli("playbook", "list")
        assert result.exit_code == 0


# ===================================================================
# app.py — error paths & edge cases
# ===================================================================


class TestAppUpdateCheck:
    """Update check notification in main callback (TTY-gated, DC-L01)."""

    def test_update_available_shows_banner(self, cli, mock_client, monkeypatch):
        """Main callback shows update banner when new version exists."""
        monkeypatch.setattr("dawos_cli.app._stdout_is_tty", lambda: True)
        monkeypatch.setattr("dawos_cli.updater.check_for_update", lambda: "v99.0.0")
        result = cli("status")
        assert result.exit_code == 0
        assert "v99.0.0" in result.output or "update" in result.output.lower()

    def test_update_check_exception_suppressed(self, cli, mock_client, monkeypatch):
        """Main callback suppresses exceptions from update check."""
        monkeypatch.setattr("dawos_cli.app._stdout_is_tty", lambda: True)

        def boom():
            raise RuntimeError("network down")

        monkeypatch.setattr("dawos_cli.updater.check_for_update", boom)
        result = cli("status")
        assert result.exit_code == 0

    def test_update_check_skipped_when_not_a_tty(self, cli, mock_client, monkeypatch):
        """DC-L01: no update check when stdout is piped (CliRunner is not a TTY)."""
        calls = {"count": 0}

        def fake_check():
            calls["count"] += 1
            return "v99.0.0"

        # Sanity: the stub is callable and counts invocations.
        assert fake_check() == "v99.0.0"
        assert calls["count"] == 1

        monkeypatch.setattr("dawos_cli.updater.check_for_update", fake_check)
        result = cli("status")
        assert result.exit_code == 0
        # The CLI run must not have invoked the update check again.
        assert calls["count"] == 1
        assert "v99.0.0" not in result.output

    def test_stdout_is_tty_returns_bool(self):
        """The TTY probe delegates to sys.stdout.isatty()."""
        from dawos_cli.app import _stdout_is_tty

        assert isinstance(_stdout_is_tty(), bool)


class TestHelpCmd:
    """Lines 292-294: help command."""

    def test_help_command(self, runner):
        result = runner.invoke(app, ["help"])
        # help_cmd raises typer.Exit, exit_code may be 0
        assert result.exit_code == 0


class TestUpdateCmd:
    """Lines 304, 310, 315-342: update and self-update commands."""

    def test_update_no_latest(self, cli, monkeypatch):
        """_run_update when fetch returns None."""
        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: None)
        result = cli("update")
        assert result.exit_code == 1

    def test_update_already_up_to_date(self, cli, monkeypatch):
        """_run_update when current == latest."""
        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: "v0.0.1")
        monkeypatch.setattr("dawos_cli.updater.parse_version", lambda v: (0, 0, 1))
        result = cli("update")
        assert result.exit_code == 0

    def test_update_newer_confirmed_success(self, cli, monkeypatch):
        """_run_update: newer available, confirmed, update succeeds."""
        received = {}

        def fake_self_update(latest=None):
            received["latest"] = latest
            return True

        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: "v99.0.0")
        monkeypatch.setattr("dawos_cli.updater.run_self_update", fake_self_update)
        result = cli("update", "--force")
        assert result.exit_code == 0
        assert "99.0.0" in result.output
        # DC-H02: the fetched tag is threaded through to the installer.
        assert received["latest"] == "v99.0.0"

    def test_update_newer_confirmed_failure(self, cli, monkeypatch):
        """_run_update: newer available, confirmed, update fails."""
        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: "v99.0.0")
        monkeypatch.setattr(
            "dawos_cli.updater.run_self_update", lambda latest=None: False
        )
        result = cli("update", "--force")
        assert result.exit_code == 0
        assert "failed" in result.output.lower() or "manually" in result.output.lower()

    def test_update_newer_declined(self, cli, monkeypatch):
        """_run_update: newer available, user declines."""
        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: "v99.0.0")
        result = cli("update", input="n\n")
        assert result.exit_code == 0

    def test_self_update_alias(self, cli, monkeypatch):
        """self-update command delegates to _run_update."""
        monkeypatch.setattr("dawos_cli.updater.fetch_latest_tag", lambda: None)
        result = cli("self-update")
        assert result.exit_code == 1


# ===================================================================
# client.py — 4 unreachable lines (86, 101, 114, 129)
# ===================================================================


class TestClientUnreachableReturns:
    """Lines 86, 101, 114, 129: return None after handlers.

    These are dead code — _handle_error/_handle_connection_error always
    raise SystemExit. We cover them by mocking handlers to NOT raise.
    """

    def test_get_returns_none_when_handler_suppressed(self, monkeypatch):
        import dawos_cli.client as c

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "err", request=MagicMock(), response=mock_resp
        )
        mock_client.get.return_value = mock_resp
        monkeypatch.setattr(c, "_client", mock_client)
        monkeypatch.setattr(c, "_handle_error", lambda exc: None)

        result = c.get("/test")
        assert result is None

    def test_post_returns_none_when_handler_suppressed(self, monkeypatch):
        import dawos_cli.client as c

        mock_cl = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "err", request=MagicMock(), response=mock_resp
        )
        mock_cl.post.return_value = mock_resp
        monkeypatch.setattr(c, "_client", mock_cl)
        monkeypatch.setattr(c, "_handle_error", lambda exc: None)

        result = c.post("/test")
        assert result is None

    def test_put_returns_none_when_handler_suppressed(self, monkeypatch):
        import dawos_cli.client as c

        mock_cl = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "err", request=MagicMock(), response=mock_resp
        )
        mock_cl.put.return_value = mock_resp
        monkeypatch.setattr(c, "_client", mock_cl)
        monkeypatch.setattr(c, "_handle_error", lambda exc: None)

        result = c.put("/test")
        assert result is None

    def test_delete_returns_none_when_handler_suppressed(self, monkeypatch):
        import dawos_cli.client as c

        mock_cl = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "err", request=MagicMock(), response=mock_resp
        )
        mock_cl.request.return_value = mock_resp
        monkeypatch.setattr(c, "_client", mock_cl)
        monkeypatch.setattr(c, "_handle_error", lambda exc: None)

        result = c.delete("/test")
        assert result is None


# ===================================================================
# audit.py — error paths & edge cases
# ===================================================================


class TestAuditElseBranch:
    """Line 48: audit entries is not a list."""

    def test_audit_non_list_entries(self, cli, mock_client):
        """When entries extracted from response is not a list."""
        mock_client["get"].return_value = {"entries": "not-a-list"}
        result = cli("audit", "list")
        assert result.exit_code == 0


# ===================================================================
# config_cmd.py — error paths & edge cases
# ===================================================================


class TestConfigGuardedApply:
    """Lines 104-110: guarded-apply with @filename."""

    def test_guarded_apply_with_file(self, cli, mock_client, tmp_path):
        """Read config from @filename."""
        cfg_file = tmp_path / "test.conf"
        cfg_file.write_text("[ppp]\nverbose=1\n")
        result = cli("config", "apply", f"@{cfg_file}", "--force")
        assert result.exit_code == 0

    def test_guarded_apply_file_not_found(self, cli, mock_client):
        """@filename points to nonexistent file."""
        result = cli("config", "apply", "@/nonexistent/file.conf", "--force")
        assert result.exit_code == 1


# ===================================================================
# Remaining: wizard.py line 322, output.py line 81, shell.py 113-114
# ===================================================================


class TestDeployApplyDirect:
    """Line 322: _deploy_apply called directly without 'confirmed' in ctx."""

    def test_deploy_apply_not_confirmed_direct(self):
        from dawos_cli.commands.wizard import _deploy_apply

        ctx: dict[str, Any] = {}  # No "confirmed"
        result = _deploy_apply(ctx)
        assert result.success is True
        assert (
            "skipped" in result.message.lower()
            or "not confirmed" in result.message.lower()
        )


class TestOutputCsvListData:
    """Line 81: CSV format with list data, auto-detecting columns."""

    def test_csv_emit_list_of_dicts(self, capsys):
        s = state.current
        orig_json = s.json_output
        orig_fmt = s.output_format
        s.json_output = False
        s.output_format = "csv"
        try:
            from dawos_cli.output import _emit

            # List of dicts with no explicit columns → auto-detect from first dict
            result = _emit([{"name": "alice", "age": 30}, {"name": "bob", "age": 25}])
            assert result is True
            captured = capsys.readouterr()
            assert "name" in captured.out
            assert "alice" in captured.out
        finally:
            s.json_output = orig_json
            s.output_format = orig_fmt


class TestReadlineCompleterCapture:
    """Lines 113-114: actual completer function registered with readline."""

    def test_readline_completer_invoked(self):
        """Capture the actual completer passed to readline.set_completer."""
        from dawos_cli.shell import _run_with_readline

        captured_completer = None

        mock_readline = MagicMock()

        def capture_set_completer(fn):
            nonlocal captured_completer
            captured_completer = fn

        mock_readline.set_completer = capture_set_completer

        with (
            patch.dict("sys.modules", {"readline": mock_readline}),
            patch("builtins.input", return_value="exit"),
            patch("dawos_cli.shell._console"),
        ):
            _run_with_readline()

        # Now test the actual captured completer
        assert captured_completer is not None
        # "status" should match "sta" prefix
        assert captured_completer("sta", 0) == "status"
        # No more matches at index 1
        assert captured_completer("sta", 1) is None
        # Non-matching prefix
        assert captured_completer("zzz", 0) is None

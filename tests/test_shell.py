"""Tests for dawos_cli.shell module."""

from __future__ import annotations

import stat
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from dawos_cli import shell


def _make_console():
    """Create a captured console for testing."""
    buf = StringIO()
    return Console(file=buf, force_terminal=True, width=120), buf


class TestExecuteLine:
    def test_valid_command(self):
        with patch("dawos_cli.app.app") as mock_app:
            shell._execute_line("version")
            mock_app.assert_called_once()

    def test_parse_error(self):
        con, buf = _make_console()
        with patch.object(shell, "_console", con):
            shell._execute_line("'unclosed")
            text = buf.getvalue()
            assert "Parse error" in text

    def test_system_exit_suppressed(self):
        with patch("dawos_cli.app.app", side_effect=SystemExit(0)):
            # Should not raise
            shell._execute_line("--help")

    def test_generic_exception_caught(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("dawos_cli.app.app", side_effect=RuntimeError("boom")),
        ):
            shell._execute_line("status")
            assert "Error" in buf.getvalue()


class TestRunWithReadline:
    def test_exit_command(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=["exit"]),
        ):
            shell._run_with_readline()
            assert "Goodbye" in buf.getvalue()

    def test_quit_command(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=["quit"]),
        ):
            shell._run_with_readline()
            assert "Goodbye" in buf.getvalue()

    def test_eof(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=EOFError),
        ):
            shell._run_with_readline()
            assert "Goodbye" in buf.getvalue()

    def test_keyboard_interrupt(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=KeyboardInterrupt),
        ):
            shell._run_with_readline()
            assert "Goodbye" in buf.getvalue()

    def test_empty_line_skipped(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=["", "exit"]),
            patch.object(shell, "_execute_line") as mock_exec,
        ):
            shell._run_with_readline()
            mock_exec.assert_not_called()

    def test_command_execution(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch("builtins.input", side_effect=["version", "exit"]),
            patch.object(shell, "_execute_line") as mock_exec,
        ):
            shell._run_with_readline()
            mock_exec.assert_called_once_with("version")


class TestRunShell:
    def test_run_shell_with_readline_fallback(self):
        con, buf = _make_console()
        with (
            patch.object(shell, "_console", con),
            patch.object(shell, "_run_with_readline") as mock_rl,
            patch.dict("sys.modules", {"prompt_toolkit": None}),
        ):
            try:
                shell.run_shell()
            except SystemExit:
                pass
            assert "dawos shell" in buf.getvalue()
            mock_rl.assert_called_once()


class TestHistoryFilePermissions:
    """DC-M05: shell history is created owner-readable only (0600)."""

    def _run_repl_once(self, tmp_path):
        """Run the prompt_toolkit REPL once with mocked modules."""
        pt_mods = {
            "prompt_toolkit": MagicMock(),
            "prompt_toolkit.completion": MagicMock(),
            "prompt_toolkit.history": MagicMock(),
        }
        mock_session = MagicMock()
        mock_session.prompt.side_effect = ["exit"]
        pt_mods["prompt_toolkit"].PromptSession.return_value = mock_session
        con, _ = _make_console()
        with (
            patch.dict("sys.modules", pt_mods),
            patch("dawos_cli.config.CONFIG_DIR", tmp_path),
            patch.object(shell, "_console", con),
        ):
            shell._run_with_prompt_toolkit()
        return tmp_path / ".shell_history"

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
    def test_history_file_mode_is_0600(self, tmp_path):
        history = self._run_repl_once(tmp_path)
        assert history.exists()
        assert stat.S_IMODE(history.stat().st_mode) == 0o600

    def test_history_chmod_oserror_suppressed(self, tmp_path):
        """chmod failure (e.g. exotic filesystems) must not break the shell."""
        with patch("dawos_cli.shell.os.chmod", side_effect=OSError("nope")):
            history = self._run_repl_once(tmp_path)
        assert history.exists()


class TestCommands:
    def test_commands_list_populated(self):
        assert "status" in shell._COMMANDS
        assert "exit" in shell._COMMANDS
        assert "profile" in shell._COMMANDS
        # Aliases
        assert "s" in shell._COMMANDS
        assert "sys" in shell._COMMANDS
        assert "cfg" in shell._COMMANDS

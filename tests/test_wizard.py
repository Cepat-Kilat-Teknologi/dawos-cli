"""Tests for the wizard engine and wizard commands."""

from __future__ import annotations

from unittest.mock import patch

from dawos_cli.wizards import Step, StepResult, print_summary, run_wizard

# ---------------------------------------------------------------------------
# Wizard engine
# ---------------------------------------------------------------------------


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_defaults(self):
        r = StepResult(success=True)
        assert r.message == ""
        assert r.data == {}
        assert r.skip_remaining is False

    def test_with_data(self):
        r = StepResult(success=False, message="err", data={"k": "v"})
        assert not r.success
        assert r.data == {"k": "v"}


class TestRunWizard:
    """Tests for run_wizard()."""

    def test_all_steps_pass(self):
        """Wizard completes when all steps succeed."""
        steps = [
            Step(
                title="Step 1",
                description="First",
                action=lambda ctx: StepResult(success=True, message="ok"),
            ),
            Step(
                title="Step 2",
                description="Second",
                action=lambda ctx: StepResult(success=True, message="done"),
            ),
        ]
        ctx = run_wizard("Test Wizard", steps)
        assert len(ctx["results"]) == 2
        assert all(r.success for r in ctx["results"])

    def test_required_step_fails_aborts(self):
        """Wizard aborts on required step failure."""
        steps = [
            Step(
                title="Fail",
                description="Will fail",
                action=lambda ctx: StepResult(success=False, message="broken"),
                required=True,
            ),
            Step(
                title="Never",
                description="Should not run",
                action=lambda ctx: StepResult(success=True),
            ),
        ]
        ctx = run_wizard("Abort Test", steps)
        assert len(ctx["results"]) == 1
        assert not ctx["results"][0].success

    def test_optional_step_fails_continues(self):
        """Wizard continues past optional step failure."""
        steps = [
            Step(
                title="Optional Fail",
                description="Fails but optional",
                action=lambda ctx: StepResult(success=False, message="skip"),
                required=False,
            ),
            Step(
                title="Continue",
                description="Should run",
                action=lambda ctx: StepResult(success=True, message="ran"),
            ),
        ]
        ctx = run_wizard("Continue Test", steps)
        assert len(ctx["results"]) == 2
        assert ctx["results"][1].success

    def test_skip_if_condition(self):
        """Steps with skip_if=True are skipped."""
        steps = [
            Step(
                title="Skipped",
                description="",
                action=lambda ctx: StepResult(success=True),
                skip_if=lambda ctx: True,
            ),
            Step(
                title="Runs",
                description="",
                action=lambda ctx: StepResult(success=True, message="yes"),
            ),
        ]
        ctx = run_wizard("Skip Test", steps)
        assert len(ctx["results"]) == 2
        assert ctx["results"][0].message == "Skipped"

    def test_skip_remaining_flag(self):
        """skip_remaining=True stops wizard early."""
        steps = [
            Step(
                title="Stop here",
                description="",
                action=lambda ctx: StepResult(success=True, skip_remaining=True),
            ),
            Step(
                title="Never",
                description="",
                action=lambda ctx: StepResult(success=True),
            ),
        ]
        ctx = run_wizard("Early Stop", steps)
        assert len(ctx["results"]) == 1

    def test_context_shared_between_steps(self):
        """Steps can write to and read from the shared context."""

        def step1(ctx):
            ctx["value"] = 42
            return StepResult(success=True)

        def step2(ctx):
            return StepResult(success=True, message=f"got {ctx.get('value')}")

        steps = [
            Step(title="Write", description="", action=step1),
            Step(title="Read", description="", action=step2),
        ]
        ctx = run_wizard("Context Test", steps)
        assert ctx["value"] == 42
        assert "42" in ctx["results"][1].message

    def test_exception_in_step_handled(self):
        """Unhandled exceptions in steps are caught gracefully."""

        def bad_step(ctx):
            raise ValueError("boom")

        steps = [
            Step(
                title="Explode",
                description="",
                action=bad_step,
                required=True,
            ),
        ]
        ctx = run_wizard("Exception Test", steps)
        assert len(ctx["results"]) == 1
        assert not ctx["results"][0].success
        assert "boom" in ctx["results"][0].message

    def test_keyboard_interrupt_cancels(self):
        """KeyboardInterrupt sets cancelled flag."""

        def interrupt_step(ctx):
            raise KeyboardInterrupt

        steps = [
            Step(title="Cancel", description="", action=interrupt_step),
        ]
        ctx = run_wizard("Cancel Test", steps)
        assert ctx.get("cancelled") is True


class TestPrintSummary:
    """Tests for print_summary()."""

    def test_prints_table(self, capsys):
        """Summary table renders without error."""
        print_summary(
            "Test Summary",
            [
                ("Check A", True, "all good"),
                ("Check B", False, "not ok"),
            ],
        )
        # No exception means success — Rich outputs to console.


# ---------------------------------------------------------------------------
# Wizard commands
# ---------------------------------------------------------------------------


class TestSetupWizard:
    """Tests for 'dawos wizard setup'."""

    def test_setup_success(self, cli, tmp_config):
        """Full setup wizard flow with mocked prompts."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                side_effect=["http://test:8470", "test-key", "myprofile"],
            ),
            patch(
                "dawos_cli.commands.wizard.client.health",
                return_value={
                    "status": "ok",
                    "version": "0.1.0",
                    "node_name": "bng1",
                },
            ),
        ):
            result = cli("wizard", "setup")

        assert result.exit_code == 0
        assert "completed" in result.output.lower() or "5/5" in result.output

    def test_setup_connection_failure(self, cli, tmp_config):
        """Setup wizard handles connection failure."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                side_effect=["http://dead:8470", "key"],
            ),
            patch("dawos_cli.commands.wizard.client.health", return_value=None),
        ):
            result = cli("wizard", "setup")

        assert result.exit_code == 0
        assert "fail" in result.output.lower() or "aborted" in result.output.lower()

    def test_setup_empty_key_rejected(self, cli, tmp_config):
        """Empty API key fails the step."""
        with patch(
            "dawos_cli.commands.wizard.Prompt.ask",
            side_effect=["http://test:8470", ""],
        ):
            result = cli("wizard", "setup")

        assert result.exit_code == 0
        assert "empty" in result.output.lower() or "fail" in result.output.lower()

    def test_api_key_prompt_is_hidden(self):
        """DC-M05: the API key prompt must not echo input."""
        from dawos_cli.commands.wizard import _setup_collect_key

        with patch(
            "dawos_cli.commands.wizard.Prompt.ask", return_value="secret"
        ) as mock_ask:
            result = _setup_collect_key({})

        assert result.success
        assert mock_ask.call_args.kwargs.get("password") is True

    def test_url_step_warns_on_insecure_remote(self, capsys):
        """DC-M06: plain-HTTP remote URL warns about unencrypted API key."""
        from dawos_cli.commands.wizard import _setup_collect_url

        with patch(
            "dawos_cli.commands.wizard.Prompt.ask",
            return_value="http://10.1.1.1:8470",
        ):
            result = _setup_collect_url({})

        assert result.success
        assert "unencrypted" in capsys.readouterr().out

    def test_url_step_silent_for_localhost(self, capsys):
        from dawos_cli.commands.wizard import _setup_collect_url

        with patch(
            "dawos_cli.commands.wizard.Prompt.ask",
            return_value="http://localhost:8470",
        ):
            result = _setup_collect_url({})

        assert result.success
        assert "unencrypted" not in capsys.readouterr().out


class TestTroubleshootWizard:
    """Tests for 'dawos wizard troubleshoot'."""

    def test_troubleshoot_session_found(self, cli, tmp_config):
        """Troubleshoot wizard finds an active session."""
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
                    {"ip": "10.0.0.1", "ifname": "ppp0"},  # /sessions/testuser
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")

        assert result.exit_code == 0
        assert "testuser" in result.output

    def test_troubleshoot_no_session(self, cli, tmp_config):
        """Troubleshoot wizard handles missing session."""
        with (
            patch(
                "dawos_cli.commands.wizard.Prompt.ask",
                return_value="missing",
            ),
            patch(
                "dawos_cli.commands.wizard.client.get",
                side_effect=[
                    {"status": "ok"},  # /health
                    {"running": True},  # /service/status
                    None,  # /sessions/missing — no data
                ],
            ),
        ):
            result = cli("wizard", "troubleshoot")

        assert result.exit_code == 0
        assert "FAIL" in result.output or "missing" in result.output

    def test_troubleshoot_empty_username(self, cli, tmp_config):
        """Empty username fails the step."""
        with patch("dawos_cli.commands.wizard.Prompt.ask", return_value=""):
            result = cli("wizard", "troubleshoot")

        assert result.exit_code == 0
        assert "empty" in result.output.lower() or "fail" in result.output.lower()


class TestDeployWizard:
    """Tests for 'dawos wizard deploy'."""

    def test_deploy_cancelled(self, cli, tmp_config):
        """Deploy wizard aborted by user."""
        with (
            patch(
                "dawos_cli.commands.wizard.client.get",
                return_value={"status": "ok"},
            ),
            patch(
                "dawos_cli.commands.wizard.client.post",
                return_value={"id": "chk-123"},
            ),
            patch("dawos_cli.commands.wizard.typer.confirm", return_value=False),
        ):
            result = cli("wizard", "deploy")

        assert result.exit_code == 0
        assert (
            "cancelled" in result.output.lower() or "skipped" in result.output.lower()
        )

    def test_deploy_confirmed_success(self, cli, tmp_config):
        """Deploy wizard completes successfully."""
        with (
            patch(
                "dawos_cli.commands.wizard.client.get",
                return_value={"status": "ok"},
            ),
            patch(
                "dawos_cli.commands.wizard.client.post",
                side_effect=[
                    {"id": "chk-123"},  # checkpoint
                    {"status": "ok"},  # apply
                ],
            ),
            patch("dawos_cli.commands.wizard.typer.confirm", return_value=True),
        ):
            result = cli("wizard", "deploy")

        assert result.exit_code == 0
        assert "chk-123" in result.output

    def test_deploy_preflight_failure(self, cli, tmp_config):
        """Deploy wizard aborts on preflight failure."""
        with patch(
            "dawos_cli.commands.wizard.client.get",
            side_effect=SystemExit(1),
        ):
            result = cli("wizard", "deploy")

        assert result.exit_code == 0
        assert "aborted" in result.output.lower() or "fail" in result.output.lower()

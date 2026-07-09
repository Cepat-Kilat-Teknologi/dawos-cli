"""Interactive wizard commands for guided multi-step operations.

Provides three guided workflows:

- ``dawos wizard setup`` — First-time profile configuration.
- ``dawos wizard troubleshoot`` — Customer session diagnostics.
- ``dawos wizard deploy`` — Safe configuration deployment.

Each wizard collects input, executes checks, and reports results.
"""

from __future__ import annotations

from typing import Any, Dict

import typer
from rich.prompt import Prompt

from .. import client, config, output
from ..wizards import Step, StepResult, console, print_summary, run_wizard

app = typer.Typer(help="Guided workflows for common operations.")


# ===================================================================
# Setup Wizard
# ===================================================================


def _setup_collect_url(ctx: Dict[str, Any]) -> StepResult:
    """Prompt for the dawos-agent URL."""
    url = Prompt.ask(
        "  Enter dawos-agent URL",
        default="http://localhost:8470",
        console=console,
    )
    url = url.rstrip("/")
    ctx["url"] = url
    return StepResult(success=True, message=f"URL: {url}")


def _setup_collect_key(ctx: Dict[str, Any]) -> StepResult:
    """Prompt for the API key."""
    key = Prompt.ask("  Enter API key", console=console)
    if not key.strip():
        return StepResult(success=False, message="API key cannot be empty")
    ctx["api_key"] = key.strip()
    return StepResult(success=True, message="API key collected")


def _setup_test_connection(ctx: Dict[str, Any]) -> StepResult:
    """Test connectivity to the dawos-agent."""
    url = ctx.get("url", "")
    data = client.health(url)
    if data:
        version = data.get("version", "unknown")
        node = data.get("node_name", "unknown")
        ctx["agent_version"] = version
        ctx["node_name"] = node
        return StepResult(
            success=True,
            message=f"Connected — agent v{version} on {node}",
            data=data,
        )
    return StepResult(
        success=False,
        message=f"Cannot reach {url}. Check the URL and try again.",
    )


def _setup_collect_name(ctx: Dict[str, Any]) -> StepResult:
    """Prompt for the profile name."""
    default = ctx.get("node_name", "default")
    name = Prompt.ask(
        "  Profile name",
        default=default,
        console=console,
    )
    ctx["profile_name"] = name.strip() or default
    return StepResult(success=True, message=f"Profile: {ctx['profile_name']}")


def _setup_save_profile(ctx: Dict[str, Any]) -> StepResult:
    """Save the profile and set as active."""
    name = ctx.get("profile_name", "default")
    url = ctx.get("url", "")
    key = ctx.get("api_key", "")
    config.add_profile(name, url, key)
    config.use_profile(name)
    return StepResult(
        success=True,
        message=f"Profile '{name}' saved and set as active",
    )


@app.command("setup")
def setup_wizard() -> None:
    """Guided first-time setup — configure a connection profile.

    Walks through entering the dawos-agent URL, API key, testing
    connectivity, and saving the profile.
    """
    steps = [
        Step(
            title="Agent URL",
            description="The HTTP address of the dawos-agent service.",
            action=_setup_collect_url,
        ),
        Step(
            title="API Key",
            description="Authentication key configured in agent.env.",
            action=_setup_collect_key,
        ),
        Step(
            title="Test Connection",
            description="Verify the agent is reachable and responding.",
            action=_setup_test_connection,
        ),
        Step(
            title="Profile Name",
            description="Choose a name for this connection profile.",
            action=_setup_collect_name,
        ),
        Step(
            title="Save Profile",
            description="Save the profile and set it as active.",
            action=_setup_save_profile,
        ),
    ]
    ctx = run_wizard("Setup Wizard", steps)

    if not ctx.get("cancelled"):
        output.info("Run [bold]dawos status[/] to verify your connection.")


# ===================================================================
# Troubleshoot Wizard
# ===================================================================


def _ts_collect_username(ctx: Dict[str, Any]) -> StepResult:
    """Prompt for the PPPoE username to troubleshoot."""
    username = Prompt.ask("  Enter PPPoE username", console=console)
    if not username.strip():
        return StepResult(success=False, message="Username cannot be empty")
    ctx["username"] = username.strip()
    return StepResult(success=True, message=f"Username: {ctx['username']}")


def _ts_check_agent(ctx: Dict[str, Any]) -> StepResult:
    """Verify the agent is reachable."""
    try:
        data = client.get("/health")
        ctx["agent_ok"] = True
        return StepResult(success=True, message="Agent is healthy", data=data)
    except SystemExit:
        ctx["agent_ok"] = False
        return StepResult(success=False, message="Cannot reach dawos-agent")


def _ts_check_session(ctx: Dict[str, Any]) -> StepResult:
    """Look up the user's active PPPoE session."""
    username = ctx.get("username", "")
    try:
        data = client.get(f"/api/v1/sessions/{username}")
        if data:
            ctx["session"] = data
            ctx["session_found"] = True
            ip = data.get("ip", "—")
            ifname = data.get("ifname", "—")
            return StepResult(
                success=True,
                message=f"Session active — IP: {ip}, Interface: {ifname}",
                data=data,
            )
        ctx["session_found"] = False
        return StepResult(
            success=False,
            message=f"No active session for '{username}'",
        )
    except SystemExit:
        ctx["session_found"] = False
        return StepResult(
            success=False,
            message=f"Session lookup failed for '{username}'",
        )


def _ts_check_service(ctx: Dict[str, Any]) -> StepResult:
    """Check if accel-ppp service is running."""
    try:
        data = client.get("/api/v1/service/status")
        running = data.get("running", False) if data else False
        ctx["service_running"] = running
        if running:
            return StepResult(success=True, message="accel-ppp is running")
        return StepResult(
            success=False,
            message="accel-ppp is NOT running",
        )
    except SystemExit:
        ctx["service_running"] = False
        return StepResult(success=False, message="Could not check service status")


def _ts_summary(ctx: Dict[str, Any]) -> StepResult:
    """Print a diagnostic summary."""
    items = [
        ("Agent reachable", ctx.get("agent_ok", False), ""),
        ("Service running", ctx.get("service_running", False), ""),
        (
            f"Session '{ctx.get('username', '?')}'",
            ctx.get("session_found", False),
            ctx.get("session", {}).get("ip", "No session"),
        ),
    ]
    print_summary("Troubleshooting Summary", items)

    if not ctx.get("session_found"):
        output.info("Session not found. Check RADIUS logs and PPPoE interface status.")

    return StepResult(success=True, message="Diagnostics complete")


@app.command("troubleshoot")
def troubleshoot_wizard() -> None:
    """Diagnose why a customer's PPPoE session is not working.

    Checks agent connectivity, service status, and session state
    for a given username, then prints a diagnostic summary.
    """
    steps = [
        Step(
            title="Customer Username",
            description="The PPPoE username to investigate.",
            action=_ts_collect_username,
        ),
        Step(
            title="Agent Health",
            description="Verify the dawos-agent is reachable.",
            action=_ts_check_agent,
        ),
        Step(
            title="Service Status",
            description="Check if accel-ppp is running on the BNG.",
            action=_ts_check_service,
            required=False,
        ),
        Step(
            title="Session Lookup",
            description="Search for the customer's active PPPoE session.",
            action=_ts_check_session,
            required=False,
        ),
        Step(
            title="Summary",
            description="Compile and display diagnostic results.",
            action=_ts_summary,
        ),
    ]
    run_wizard("Troubleshoot Wizard", steps)


# ===================================================================
# Deploy Wizard
# ===================================================================


def _deploy_preflight(ctx: Dict[str, Any]) -> StepResult:
    """Run pre-flight checks before deployment."""
    try:
        data = client.get("/health")
        ctx["pre_health"] = data
        return StepResult(
            success=True,
            message="Agent is healthy and ready for deployment",
            data=data,
        )
    except SystemExit:
        return StepResult(
            success=False,
            message="Agent is not reachable. Deployment aborted.",
        )


def _deploy_backup(ctx: Dict[str, Any]) -> StepResult:
    """Create a configuration checkpoint before deploying."""
    try:
        data = client.post("/api/v1/config/checkpoint")
        if data:
            checkpoint_id = data.get("id", data.get("checkpoint", "unknown"))
            ctx["checkpoint_id"] = checkpoint_id
            return StepResult(
                success=True,
                message=f"Checkpoint created: {checkpoint_id}",
                data=data,
            )
        return StepResult(success=False, message="Checkpoint creation returned empty")
    except SystemExit:
        return StepResult(success=False, message="Failed to create checkpoint")


def _deploy_confirm(ctx: Dict[str, Any]) -> StepResult:
    """Ask for deployment confirmation."""
    checkpoint = ctx.get("checkpoint_id", "none")
    console.print(f"  [dim]Rollback checkpoint: {checkpoint}[/]")

    confirm = typer.confirm("  Proceed with deployment?", default=False)
    if not confirm:
        return StepResult(
            success=True,
            message="Deployment cancelled by user",
            skip_remaining=True,
        )
    ctx["confirmed"] = True
    return StepResult(success=True, message="Deployment confirmed")


def _deploy_apply(ctx: Dict[str, Any]) -> StepResult:
    """Apply the configuration (reload accel-ppp)."""
    if not ctx.get("confirmed"):
        return StepResult(
            success=True,
            message="Skipped — not confirmed",
            skip_remaining=True,
        )
    try:
        data = client.post("/api/v1/config/apply")
        return StepResult(
            success=True,
            message="Configuration applied successfully",
            data=data or {},
        )
    except SystemExit:
        return StepResult(
            success=False,
            message="Configuration apply failed. Consider rolling back.",
        )


def _deploy_verify(ctx: Dict[str, Any]) -> StepResult:
    """Verify the service is healthy after deployment."""
    if not ctx.get("confirmed"):
        return StepResult(success=True, message="Skipped — not confirmed")
    try:
        data = client.get("/health")
        ctx["post_health"] = data
        items = [
            ("Pre-deploy health", bool(ctx.get("pre_health")), ""),
            ("Checkpoint created", bool(ctx.get("checkpoint_id")), ""),
            ("Config applied", True, ""),
            ("Post-deploy health", bool(data), ""),
        ]
        print_summary("Deployment Summary", items)
        return StepResult(success=True, message="Service is healthy after deployment")
    except SystemExit:
        output.warning(
            f"Service may be unhealthy. "
            f"Rollback with: dawos config checkpoint rollback "
            f"{ctx.get('checkpoint_id', '')}"
        )
        return StepResult(
            success=False,
            message="Post-deployment health check failed",
        )


@app.command("deploy")
def deploy_wizard() -> None:
    """Guided safe configuration deployment workflow.

    Creates a rollback checkpoint, asks for confirmation, applies
    configuration changes, and verifies service health afterward.
    """
    steps = [
        Step(
            title="Pre-flight Check",
            description="Verify the agent is reachable and healthy.",
            action=_deploy_preflight,
        ),
        Step(
            title="Create Checkpoint",
            description="Back up the current config for rollback.",
            action=_deploy_backup,
        ),
        Step(
            title="Confirm Deployment",
            description="Review and confirm before applying changes.",
            action=_deploy_confirm,
        ),
        Step(
            title="Apply Configuration",
            description="Reload accel-ppp with the new configuration.",
            action=_deploy_apply,
            skip_if=lambda ctx: not ctx.get("confirmed"),
        ),
        Step(
            title="Verify Health",
            description="Confirm the service is healthy after deployment.",
            action=_deploy_verify,
            skip_if=lambda ctx: not ctx.get("confirmed"),
        ),
    ]
    ctx = run_wizard("Deploy Wizard", steps)

    if ctx.get("confirmed") and not ctx.get("cancelled"):
        checkpoint = ctx.get("checkpoint_id", "")
        if checkpoint:
            output.info(
                f"Rollback available: "
                f"[bold]dawos config checkpoint rollback {checkpoint}[/]"
            )

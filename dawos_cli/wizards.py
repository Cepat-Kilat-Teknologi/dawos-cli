"""Interactive wizard engine for guided multi-step CLI operations.

Provides a step-based runner that walks operators through complex
tasks with Rich-formatted prompts, progress indicators, and automatic
error recovery.

Each wizard is a sequence of :class:`Step` objects executed by
:func:`run_wizard`.  Steps can be interactive (prompt for input),
automated (run an API call), or conditional (skip based on prior
results).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

log = logging.getLogger(__name__)

console = Console()


@dataclass
class StepResult:
    """Outcome of a single wizard step."""

    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    skip_remaining: bool = False


@dataclass
class Step:
    """A single step in a wizard workflow.

    Attributes:
        title: Short display title for the step.
        description: Explanation shown before execution.
        action: Callable that receives the wizard context dict and
            returns a :class:`StepResult`.
        required: If ``True``, a failure aborts the wizard.
        skip_if: Optional predicate — when it returns ``True`` the
            step is skipped.
    """

    title: str
    description: str
    action: Callable[[Dict[str, Any]], StepResult]
    required: bool = True
    skip_if: Optional[Callable[[Dict[str, Any]], bool]] = None


def run_wizard(
    name: str,
    steps: List[Step],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a wizard workflow step by step.

    Args:
        name: Display name for the wizard.
        steps: Ordered list of steps to execute.
        context: Shared mutable dict passed to every step action.

    Returns:
        The final context dict with all accumulated data.
    """
    ctx = context or {}
    ctx.setdefault("results", [])
    total = len(steps)

    console.print(
        Panel(
            f"[bold]{name}[/]\n"
            f"[dim]This wizard will guide you through {total} step(s).[/]",
            border_style="cyan",
            expand=False,
        )
    )
    console.print()

    completed = 0
    for i, step in enumerate(steps, 1):
        # Check skip condition.
        if step.skip_if and step.skip_if(ctx):
            console.print(
                f"  [dim]Step {i}/{total}:[/] {step.title} — [yellow]skipped[/]"
            )
            ctx["results"].append(StepResult(success=True, message="Skipped"))
            continue

        console.print(f"  [bold cyan]Step {i}/{total}:[/] {step.title}")
        if step.description:
            console.print(f"  [dim]{step.description}[/]")

        try:
            result = step.action(ctx)
        except KeyboardInterrupt:
            console.print("\n  [yellow]Wizard cancelled by user.[/]")
            ctx["cancelled"] = True
            break
        except Exception as exc:  # pylint: disable=broad-exception-caught
            result = StepResult(success=False, message=str(exc))

        ctx["results"].append(result)

        if result.success:
            msg = result.message or "Done"
            console.print(f"  [green]OK[/] — {msg}")
            completed += 1
        else:
            msg = result.message or "Failed"
            console.print(f"  [red]FAIL[/] — {msg}")
            if step.required:
                console.print("  [red]This step is required. Wizard aborted.[/]")
                break

        if result.skip_remaining:
            break

        console.print()

    # Summary
    console.print()
    status = "completed" if completed == total else "incomplete"
    style = "green" if completed == total else "yellow"
    console.print(
        f"[bold {style}]Wizard {status}:[/] " f"{completed}/{total} step(s) passed."
    )

    return ctx


def print_summary(
    title: str,
    items: List[tuple],
) -> None:
    """Print a summary table of check results.

    Args:
        title: Table title.
        items: List of ``(label, status, detail)`` tuples.
    """
    t = Table(title=title, expand=False)
    t.add_column("Check", style="bold")
    t.add_column("Status")
    t.add_column("Detail", style="dim")

    for label, passed, detail in items:
        status_str = "[green]PASS[/]" if passed else "[red]FAIL[/]"
        t.add_row(label, status_str, str(detail))

    console.print(t)

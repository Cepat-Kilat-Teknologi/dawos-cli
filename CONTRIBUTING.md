# Contributing to dawos-cli

Thank you for your interest in contributing to **dawos-cli**! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Adding New Commands](#adding-new-commands)

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/dawos-cli.git
   cd dawos-cli
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Environment

### Prerequisites

- Python 3.9 or later
- Git

### Setup

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # Linux / macOS
# .venv\Scripts\activate     # Windows

# Install the package with development dependencies
pip install -e ".[dev]"
```

### Verify Setup

```bash
# Run tests
pytest

# Check formatting
black --check dawos_cli/ tests/

# Run linting
pylint dawos_cli/
ruff check dawos_cli/ tests/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code on commit:

```bash
pip install pre-commit
pre-commit install
```

This runs Black, Ruff, and Pylint checks before each commit.

---

## Code Style

This project enforces consistent code style through automated tooling:

### Formatting — Black

All Python code must be formatted with [Black](https://black.readthedocs.io/) using the project configuration (88-character line length, Python 3.9 target).

```bash
# Format all files
black dawos_cli/ tests/

# Check without modifying
black --check dawos_cli/ tests/
```

### Linting — Pylint

All source code must pass [Pylint](https://pylint.readthedocs.io/) with a score of **10.0/10**.

```bash
pylint dawos_cli/
```

### Linting — Ruff

[Ruff](https://docs.astral.sh/ruff/) is used as a complementary fast linter:

```bash
ruff check dawos_cli/ tests/
```

### Style Guidelines

- **Imports**: Use `from __future__ import annotations` at the top of every module.
- **Type hints**: Annotate all function signatures with return types.
- **Docstrings**: Every module must have a module-level docstring. Command functions use Typer's `help` parameter instead of docstrings.
- **Naming**: Follow PEP 8. Use `snake_case` for functions and variables, `PascalCase` for classes.
- **Line length**: 88 characters (enforced by Black).

---

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-snmp-traps` — New features
- `fix/session-terminate-payload` — Bug fixes
- `docs/update-readme` — Documentation changes
- `refactor/simplify-client` — Code refactoring

### Commit Messages

Write clear, concise commit messages in **English**:

```
Add SNMP trap forwarding to firewall command group

Implement hook-based SNMP trap forwarding with configurable
destinations. Includes unit tests and documentation updates.
```

- Use the imperative mood ("Add feature" not "Added feature").
- Keep the subject line under 72 characters.
- Include a blank line between the subject and body.
- Reference issues where applicable: `Fixes #42`.

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_commands.py

# Run a specific test class or method
pytest tests/test_commands.py::TestSessionCommands
pytest tests/test_commands.py::TestSessionCommands::test_terminate
```

### Coverage

The project maintains a **minimum 90% code coverage** requirement (currently at 100%):

```bash
# Run with coverage
pytest --cov=dawos_cli --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=dawos_cli --cov-report=html
open htmlcov/index.html
```

### Writing Tests

- **Location**: Tests go in the `tests/` directory.
- **Naming**: Test files follow `test_<module>.py`. Test functions follow `test_<description>`.
- **Mocking**: Mock at the `dawos_cli.client.get/post/put/delete` level, never at `httpx`.
- **Fixtures**: Use shared fixtures from `tests/conftest.py`.
- **Edge cases**: Test error responses (401, 404, 422, 500), empty data, and non-standard response shapes.
- **Confirmation prompts**: Test both confirmed and aborted paths.

Example test:

```python
class TestMyCommands:
    def test_my_command(self, cli, mock_get):
        mock_get.return_value = {"status": "ok", "data": []}
        result = cli.invoke(app, ["mygroup", "mycommand"])
        assert result.exit_code == 0
        mock_get.assert_called_once_with("/api/v1/mygroup/mycommand")
```

---

## Submitting Changes

### Pull Request Process

1. **Ensure all checks pass** before submitting:
   ```bash
   black --check dawos_cli/ tests/
   pylint dawos_cli/
   ruff check dawos_cli/ tests/
   pytest --cov=dawos_cli
   ```

2. **Push** your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request** against the `main` branch.

4. **Fill out the PR template** with:
   - A clear description of the changes
   - Any related issue numbers
   - Testing steps for reviewers

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage remains at or above 90%
- [ ] Black formatting applied
- [ ] Pylint score is 10.0/10
- [ ] Ruff reports no violations
- [ ] New features include tests
- [ ] Documentation is updated (if applicable)

---

## Reporting Issues

### Bug Reports

When reporting a bug, please include:

1. **dawos-cli version** (`dawos --version`)
2. **Python version** (`python --version`)
3. **Operating system** and version
4. **Steps to reproduce** the issue
5. **Expected behavior** vs. **actual behavior**
6. **Error output** (with `--verbose` flag if applicable)

### Feature Requests

Feature requests are welcome! Please include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: What other approaches did you consider?

---

## Adding New Commands

To add a new command group:

### 1. Create the Command Module

Create `dawos_cli/commands/mycommand.py`:

```python
"""My command group — brief description."""

from __future__ import annotations

import typer

from .. import client, output

app = typer.Typer(help="My command group description.")


@app.command("list")
def list_items() -> None:
    """List all items."""
    data = client.get("/api/v1/mycommand")
    items = data.get("items", data) if isinstance(data, dict) else data
    if isinstance(items, list):
        output.table(items, ["name", "status"], title="Items")
    else:
        output.response(data)


@app.command("show")
def show(
    name: str = typer.Argument(..., help="Item name"),
) -> None:
    """Show details of an item."""
    data = client.get(f"/api/v1/mycommand/{name}")
    output.response(data, title=f"Item: {name}")
```

### 2. Register in `app.py`

Add the import and mount the command group:

```python
from .commands import mycommand  # Add to the import block

app.add_typer(mycommand.app, name="mycommand", help="My command group.")
```

### 3. Write Tests

Add tests in `tests/test_commands.py`:

```python
class TestMyCommands:
    def test_list(self, cli, mock_get):
        mock_get.return_value = {"items": [{"name": "a", "status": "ok"}]}
        result = cli.invoke(app, ["mycommand", "list"])
        assert result.exit_code == 0
        mock_get.assert_called_once_with("/api/v1/mycommand")

    def test_show(self, cli, mock_get):
        mock_get.return_value = {"name": "a", "status": "ok"}
        result = cli.invoke(app, ["mycommand", "show", "a"])
        assert result.exit_code == 0
        mock_get.assert_called_once_with("/api/v1/mycommand/a")
```

### 4. Run Checks

```bash
black dawos_cli/ tests/
pylint dawos_cli/
pytest --cov=dawos_cli --cov-report=term-missing
```

---

## Questions?

If you have questions about contributing, please open a [GitHub Discussion](https://github.com/Cepat-Kilat-Teknologi/dawos-cli/discussions) or reach out to the maintainers.

Thank you for contributing!

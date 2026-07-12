# Contributing

See [CONTRIBUTING.md](https://github.com/Cepat-Kilat-Teknologi/dawos-cli/blob/main/CONTRIBUTING.md) for the full guide.

## Quick Setup

```bash
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli
make dev
source .venv/bin/activate
```

## Development Commands

```bash
make test       # Run 682 tests with coverage
make lint       # Black + Pylint + Ruff
make format     # Auto-format with Black
make check      # All checks (lint + test)
```

## Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks run Black, Ruff, and Pylint automatically on `git commit`.

## Quality Standards

- **Black**: line-length 88, target py39
- **Pylint**: must be 10.00/10
- **Ruff**: zero violations
- **Coverage**: minimum 90% (currently 100%)

# Architecture

## Overview

```
┌──────────────┐     HTTP/REST      ┌──────────────┐     CLI      ┌──────────────┐
│  accel-ppp   │ ◄──────────────── │  dawos-agent  │ ◄────────── │  dawos-cli   │
│  (BNG core)  │                    │  (FastAPI)    │             │  (Typer+Rich) │
└──────────────┘                    └──────────────┘             └──────────────┘
```

## Module Structure

```
dawos_cli/
├── __init__.py          # Version string
├── __main__.py          # python -m dawos_cli
├── app.py               # Typer app, global options, command registration
├── client.py            # httpx HTTP client (singleton, X-API-Key auth)
├── config.py            # Multi-profile config (cross-platform paths)
├── output.py            # Rich output helpers (table, json, csv, yaml)
├── state.py             # Runtime state dataclass (singleton)
├── dashboard.py         # Rich Live dashboard (dawos top)
├── doctor.py            # System diagnostics (dawos doctor)
├── shell.py             # Interactive REPL (dawos shell)
├── updater.py           # Version update checker
├── telemetry.py         # Opt-in anonymous usage stats
└── commands/
    ├── sessions.py      # PPPoE session management
    ├── system.py        # System info and health
    ├── service.py       # BNG service control
    ├── profile.py       # Profile management
    ├── config_cmd.py    # BNG configuration
    ├── network.py       # Network interfaces
    ├── firewall.py      # Firewall rules
    ├── nat.py           # NAT/masquerade
    ├── ... (26 modules)
    └── zone.py          # Zone-based firewall
```

## Design Principles

1. **Thin client** — dawos-cli is a pure HTTP client. All logic lives in dawos-agent.
2. **Consistent output** — Every command uses `output.py` helpers for uniform formatting.
3. **Global state** — `state.py` singleton avoids threading context through every command.
4. **Multi-profile** — Operators manage multiple BNG nodes without re-typing credentials.
5. **Automation-first** — `--json` and `--format csv` for scripting from day one.

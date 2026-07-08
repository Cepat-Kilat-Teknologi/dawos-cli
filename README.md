<p align="center">
  <strong>dawos-cli</strong><br>
  <em>Remote CLI client for dawos-agent — manage PPPoE/BNG routers from the command line.</em><br>
  <a href="https://pypi.org/project/dawos-cli/">PyPI</a> |
  <a href="https://cepat-kilat-teknologi.github.io/dawos-cli/">Documentation</a> |
  <a href="https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases">Releases</a>
</p>

---

## Overview

**dawos-cli** is a feature-rich command-line interface for managing [accel-ppp](https://accel-ppp.org/) PPPoE/BNG routers through the [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) REST API. It provides comprehensive management capabilities including session control, firewall management, traffic shaping, routing, and real-time monitoring — all from your terminal.

### Key Features

- **26 command groups** covering sessions, firewall, NAT, routing, traffic, pools, DHCP, DNS, VRRP, and more
- **Multi-profile support** for managing multiple BNG nodes from a single installation
- **Live dashboard** (`dawos top`) with real-time session statistics and system metrics
- **Interactive shell** (`dawos shell`) with tab completion and command history
- **Multiple output formats** — `--format table|json|csv|yaml` for any workflow
- **Self-diagnostics** (`dawos doctor`) — environment, connectivity, and config checks
- **SSE streaming** for live traffic monitoring and log tailing
- **Rich terminal output** with tables, panels, and color — or `--json` for scripting
- **Command aliases** — `s`, `sys`, `cfg`, `net`, `fw`, `rt`, `mon`, `diag` for power users
- **Self-updating** — built-in update notifications and `dawos update`
- **Shell completion** for Bash, Zsh, Fish, and PowerShell
- **Guarded configuration** with automatic rollback on failure
- **Config export/import** — back up and share profiles across machines
- **Opt-in telemetry** — anonymous usage statistics (disabled by default)

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Global Options](#global-options)
- [Command Reference](#command-reference)
- [Usage Examples](#usage-examples)
- [Shell Completion](#shell-completion)
- [Architecture](#architecture)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [Security](#security)
- [Changelog](#changelog)
- [License](#license)

---

## Installation

### Prerequisites

- **Python 3.9** or later — [Download Python](https://www.python.org/downloads/)
- A running [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) instance

### Quick Install (Recommended)

```bash
pip install dawos-cli
```

Or with [pipx](https://pipx.pypa.io) (isolated environment):

```bash
pipx install dawos-cli
```

**Homebrew (macOS / Linux):**

```bash
brew install Cepat-Kilat-Teknologi/tap/dawos-cli
```

**One-line installer (macOS / Linux):**

```bash
curl -fsSL https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.sh | bash
```

**Windows (PowerShell as Administrator):**

```powershell
irm https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.ps1 | iex
```

> The installer checks Python, installs [pipx](https://pipx.pypa.io) if needed, and registers the `dawos` command globally.
> Open a **new terminal** after installation, then run `dawos --version` to verify.

### Manual Install

#### Option A — pipx (Isolated)

```bash
# macOS
brew install pipx && pipx ensurepath

# Linux (Debian/Ubuntu)
sudo apt install pipx && pipx ensurepath

# Windows
pip install --user pipx && python -m pipx ensurepath

# Then install dawos-cli
pipx install dawos-cli
```

#### Option B — pip

```bash
pip install dawos-cli
```

#### Option C — From Source (Development)

```bash
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Or use the Makefile (macOS / Linux):

```bash
make dev            # Create venv + install deps
source .venv/bin/activate
```

### Upgrade

```bash
# Built-in (recommended)
dawos update

# pipx
pipx upgrade dawos-cli

# pip
pip install --upgrade dawos-cli
```

### Uninstall

```bash
# pipx
pipx uninstall dawos-cli

# pip
pip uninstall dawos-cli
```

---

## Quick Start

### 1. Add Your First BNG Node

```bash
dawos profile add production --url http://192.168.1.100:8470 --key YOUR_API_KEY
```

> **Where to get the API key?** The API key is the `DAWOS_API_KEY` value on your [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) server. Run this on the server to check:
> ```bash
> sudo cat /etc/dawos-agent/agent.env | grep DAWOS_API_KEY
> ```
>
> - **Key already set?** Copy the value and use it in the command above.
> - **Key not set yet?** Generate one and configure the server (see [Authentication docs](https://github.com/Cepat-Kilat-Teknologi/dawos-agent/blob/main/docs/CONFIGURATION.md#authentication)):
>   ```bash
>   # 1. Generate a secure key
>   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
>
>   # 2. Set it on the server
>   sudo nano /etc/dawos-agent/agent.env    # add: DAWOS_API_KEY=<generated-key>
>   sudo systemctl restart dawos-agent
>
>   # 3. Use the same key in dawos-cli
>   dawos profile add production --url http://<server-ip>:8470 --key <generated-key>
>   ```

This creates a profile named `production` pointing to your dawos-agent instance. The first profile is automatically set as active.

> **Tip:** Use `--no-check` to skip connectivity verification when adding a profile (useful for offline setup):
> ```bash
> dawos profile add production --url http://192.168.1.100:8470 --key YOUR_KEY --no-check
> ```

### 2. Verify Connection

```bash
dawos status
```

### 3. Start Managing

```bash
# System overview
dawos system info

# List active PPPoE sessions
dawos session list

# Launch the live dashboard
dawos top

# Stream real-time traffic
dawos traffic watch
```

---

## Configuration

### Config File Location

| Platform | Path |
|----------|------|
| **macOS / Linux** | `~/.config/dawos/config.json` |
| **Linux (XDG)** | `$XDG_CONFIG_HOME/dawos/config.json` |
| **Windows** | `%APPDATA%\dawos\config.json` |

Override on any platform:

```bash
# Linux / macOS
export DAWOS_CONFIG_DIR=/etc/dawos

# Windows PowerShell
$env:DAWOS_CONFIG_DIR = "C:\dawos"
```

### Profile Management

Manage multiple BNG nodes from a single installation:

```bash
# Add profiles
dawos profile add bng1 --url http://10.0.0.1:8470 --key API_KEY_1
dawos profile add bng2 --url http://10.0.0.2:8470 --key API_KEY_2

# List all profiles
dawos profile list

# Switch active profile
dawos profile use bng2

# Test connectivity
dawos profile test bng1

# Remove a profile
dawos profile remove bng2
```

### Per-Command Profile Override

```bash
# Override with --profile flag
dawos --profile bng1 session list

# Override with environment variable
DAWOS_PROFILE=bng1 dawos session list
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DAWOS_PROFILE` | Override the active profile | Active profile from config |
| `DAWOS_CONFIG_DIR` | Override configuration directory | Platform default (see above) |
| `DAWOS_NO_UPDATE_CHECK` | Disable update notifications (`1` to disable) | Not set |
| `DAWOS_TELEMETRY` | Enable anonymous usage stats (`1` to enable) | Not set |

---

## Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--profile NAME` | `-p` | Use a specific profile (overrides active) |
| `--json` | `-j` | Output raw JSON (for scripting and piping) |
| `--format FMT` | `-F` | Output format: `table`, `json`, `csv`, `yaml` |
| `--verbose` | `-v` | Show request URLs and timing |
| `--timeout SECS` | `-t` | Request timeout in seconds (default: 30) |
| `--version` | `-V` | Show version and exit |
| `--help` | `-h` | Show help message |

> **Note:** Global options must appear **before** the subcommand: `dawos -j system info`

---

## Command Reference

### Top-Level Commands

| Command | Description |
|---------|-------------|
| `dawos status` | Quick connection and service health check |
| `dawos top` | Launch the live full-screen monitoring dashboard |
| `dawos version` | Show version information |
| `dawos update` | Check for updates and upgrade |
| `dawos doctor` | Run system diagnostics (environment, connectivity, config) |
| `dawos shell` | Launch interactive REPL with tab completion |

### Command Groups

| Group | Alias | Description | Subcommands |
|-------|-------|-------------|-------------|
| **profile** | — | Connection profile management | `add`, `list`, `use`, `remove`, `test`, `show`, `export`, `import` |
| **system** | `sys` | System information and health | `info`, `health`, `metrics` |
| **service** | — | BNG service control | `status`, `start`, `stop`, `restart`, `cmd` |
| **session** | `s` | PPPoE session management | `list`, `stats`, `find`, `terminate`, `restart`, `by-sid`, `by-ip`, `snapshot`, `drop-by-mac` |
| **config** | `cfg` | BNG configuration | `show`, `update`, `backups`, `revisions`, `diff`, `rollback`, `apply`, `confirm`, `apply-status` |
| **network** | `net` | Network interfaces and routing | `interfaces`, `interface`, `interface-config`, `routes`, `add-route`, `del-route`, `dns`, `dns-set`, `vlans`, `vlan-add`, `vlan-del`, `vlan-state` |
| **firewall** | `fw` | Firewall, sysctl, and conntrack | `status`, `rules`, `save`, `validate`, `sysctl`, `sysctl-set`, `conntrack`, `conntrack-set`, `snmp`, `groups`, `group-add`, `group-del`, `group-members` |
| **nat** | — | NAT and masquerade management | `status`, `masquerade-on`, `masquerade-off`, `egress`, `egress-set`, `egress-del`, `public-ip-add`, `public-ip-del`, `box-egress`, `box-egress-set` |
| **pppoe** | — | PPPoE interface management | `interfaces`, `add`, `remove`, `mac-filter`, `mac-add`, `mac-del`, `pado`, `pado-set` |
| **traffic** | — | Live traffic monitoring | `watch`, `watch-user`, `queue`, `ratelimit`, `ratelimit-restore` |
| **routing** | `rt` | Dynamic routing protocols | `bgp`, `bgp-routes`, `ospf`, `ospf-neighbors`, `ospf-routes`, `rip`, `rip-routes`, `bfd`, `bfd-peers` |
| **pool** | — | IP address pool management | `list`, `usage`, `add`, `remove` |
| **conntrack** | — | Connection tracking | `config`, `table-size`, `timeouts`, `timeout-set`, `helpers`, `profiles`, `profile-apply` |
| **events** | — | Event hooks and webhooks | `hooks`, `hook-add`, `hook-del`, `fire`, `history`, `history-clear` |
| **scheduler** | — | Scheduled job management | `list`, `add`, `remove`, `run` |
| **dns** | — | DNS forwarding | `status`, `config`, `config-set`, `flush` |
| **dhcp** | — | DHCP server and relay | `status`, `leases`, `relay`, `restart`, `relay-restart` |
| **ntp** | — | NTP time synchronization | `status`, `sources` |
| **lldp** | — | LLDP link-layer discovery | `status`, `neighbors`, `neighbor` |
| **vrrp** | — | VRRP high-availability | `status`, `group`, `failover`, `restart` |
| **flow** | — | Flow accounting (NetFlow/sFlow) | `status`, `collectors`, `stats`, `restart` |
| **monitoring** | `mon` | Monitoring and metrics | `status`, `metrics`, `metrics-service`, `configure`, `restart` |
| **limits** | — | Connection limits | `show`, `set`, `interface` |
| **zone** | — | Zone-based firewall | `list`, `show`, `add`, `remove` |
| **diagnostics** | `diag` | System diagnostics | `doctor` |
| **logs** | — | Log viewing and streaming | `tail`, `stream` |

---

## Usage Examples

### Session Management

```bash
# List all active sessions
dawos session list

# Session statistics
dawos session stats

# Find a specific user's session
dawos session find john

# Terminate a session (with confirmation prompt)
dawos session terminate john

# Terminate without confirmation
dawos session terminate john --force

# Restart a session (drop + reconnect)
dawos session restart john --force

# Look up session by SID or IP
dawos session by-sid abc123
dawos session by-ip 10.0.0.5

# Full session snapshot
dawos session snapshot john

# Drop by MAC address
dawos session drop-by-mac AA:BB:CC:DD:EE:FF --force
```

### Configuration Management

```bash
# Show current config
dawos config show

# Update config from a file
dawos config update @/path/to/config.ini --force

# List backups and revisions
dawos config backups
dawos config revisions

# Diff against a backup
dawos config diff backup_20240101

# Rollback to a checkpoint
dawos config rollback backup_20240101 --force

# Apply config with guarded rollback (auto-reverts on failure)
dawos config apply @new_config.ini --force

# Confirm the apply (prevents auto-rollback)
dawos config confirm
```

### Traffic Monitoring

```bash
# Live traffic stream (Ctrl+C to stop)
dawos traffic watch

# Watch a specific user
dawos traffic watch-user john

# View TC queue for a user
dawos traffic queue john

# Apply rate limit
dawos traffic ratelimit john --rate 50M/25M

# Restore original rate
dawos traffic ratelimit-restore john
```

### Firewall Management

```bash
# View firewall status and rules
dawos firewall status
dawos firewall rules

# Validate an nftables configuration
dawos firewall validate "table inet filter { ... }"

# Save the current ruleset
dawos firewall save

# Manage firewall groups
dawos firewall groups
dawos firewall group-add blocked_ips --type address --elements "10.0.0.1,10.0.0.2"
dawos firewall group-members blocked_ips "10.0.0.3,10.0.0.4"
dawos firewall group-del blocked_ips
```

### Network and Routing

```bash
# List interfaces and routes
dawos network interfaces
dawos network routes

# Add a static route
dawos network add-route 10.0.0.0/24 --gw 192.168.1.1

# Configure an interface
dawos network interface-config eth0 --mtu 9000

# Manage VLANs
dawos network vlans
dawos network vlan-add eth0 --id 100 --address 10.100.0.1/24

# View and configure DNS
dawos network dns
dawos network dns-set "8.8.8.8,1.1.1.1"
```

### Monitoring and Logs

```bash
# Live dashboard (full-screen)
dawos top
dawos top --interval 5

# View recent logs
dawos logs tail
dawos logs tail --lines 200 --service accel-ppp

# Stream logs in real time (Ctrl+C to stop)
dawos logs stream
dawos logs stream --service accel-ppp

# System diagnostics
dawos diagnostics doctor

# Built-in doctor command
dawos doctor
```

### Interactive Shell

```bash
# Launch interactive REPL with tab completion
dawos shell

# Inside the shell, type commands without 'dawos' prefix:
#   session list
#   system info
#   s list          (alias for session list)
#   exit
```

### Output Formats

> **Note:** `--json`, `-j`, `--format`, and `-F` are global options — place them **before** the command group.

```bash
# Default Rich table
dawos session list

# JSON output for scripting
dawos --json session list
dawos -j session list

# CSV for spreadsheets
dawos -F csv session list > sessions.csv

# YAML output
dawos -F yaml session list
```

### JSON Output for Scripting

```bash
# Pipe session data to jq
dawos -j session list | jq '.[].username'

# Extract system uptime
dawos -j system info | jq '.uptime'

# Count active sessions
dawos -j session stats | jq '.active_sessions'

# Export session list to CSV
dawos -j session list | jq -r '.[] | [.username, .ip, .uptime] | @csv'
```

---

## Shell Completion

Install shell completion for your preferred shell:

```bash
# Automatic installation
dawos --install-completion

# Manual generation
dawos --show-completion bash >> ~/.bashrc
dawos --show-completion zsh  >> ~/.zshrc
dawos --show-completion fish >  ~/.config/fish/completions/dawos.fish
```

---

## Architecture

```
dawos-cli/
├── dawos_cli/
│   ├── __init__.py          # Package metadata and version
│   ├── __main__.py          # python -m dawos_cli support
│   ├── app.py               # Root Typer app, global callback, command mounting
│   ├── state.py             # Shared state singleton (profile, flags)
│   ├── config.py            # Profile management (~/.config/dawos/config.json)
│   ├── client.py            # httpx HTTP client (GET/POST/PUT/DELETE/SSE)
│   ├── output.py            # Rich output helpers (table, json, csv, yaml)
│   ├── dashboard.py         # Live full-screen dashboard (Rich Live)
│   ├── doctor.py            # System diagnostics (dawos doctor)
│   ├── shell.py             # Interactive REPL with tab completion (dawos shell)
│   ├── updater.py           # Version update checker (GitHub Releases)
│   ├── telemetry.py         # Opt-in anonymous usage statistics
│   └── commands/            # 26 command group modules
│       ├── config_cmd.py    # Configuration management
│       ├── conntrack.py     # Connection tracking
│       ├── dhcp.py          # DHCP server and relay
│       ├── diagnostics.py   # System diagnostics
│       ├── dns.py           # DNS forwarding
│       ├── events.py        # Event hooks and webhooks
│       ├── firewall.py      # Firewall rules, sysctl, SNMP
│       ├── flow.py          # Flow accounting
│       ├── limits.py        # Connection limits
│       ├── lldp.py          # LLDP discovery
│       ├── logs.py          # Log viewing and streaming
│       ├── monitoring.py    # Monitoring and metrics
│       ├── nat.py           # NAT / masquerade
│       ├── network.py       # Network interfaces, routes, VLANs
│       ├── ntp.py           # NTP synchronization
│       ├── pool.py          # IP address pools
│       ├── pppoe.py         # PPPoE interfaces and MAC filters
│       ├── profile.py       # Connection profile management
│       ├── routing.py       # Dynamic routing (BGP/OSPF/RIP/BFD)
│       ├── scheduler.py     # Scheduled jobs
│       ├── service.py       # Service control
│       ├── sessions.py      # Session management
│       ├── system.py        # System info and health
│       ├── traffic.py       # Traffic monitoring and shaping
│       ├── vrrp.py          # VRRP high-availability
│       └── zone.py          # Zone-based firewall
├── tests/                   # 426 tests, 97% coverage
│   ├── conftest.py          # Shared fixtures
│   ├── test_app.py          # App-level and CLI integration tests
│   ├── test_client.py       # HTTP client tests
│   ├── test_commands.py     # All command group tests
│   ├── test_config.py       # Configuration and profile export/import tests
│   ├── test_dashboard.py    # Dashboard tests
│   ├── test_doctor.py       # Doctor diagnostics tests
│   ├── test_output.py       # Output format tests (table, json, csv, yaml)
│   ├── test_shell.py        # Interactive shell tests
│   ├── test_state.py        # State management tests
│   └── test_telemetry.py    # Telemetry module tests
├── .github/
│   └── workflows/
│       ├── ci.yml           # GitHub Actions CI (lint + test on push/PR)
│       └── release.yml      # PyPI publish + GitHub Releases on tag
├── .pre-commit-config.yaml  # Pre-commit hooks (black, ruff, pylint)
├── docs/                    # MkDocs Material documentation site
├── mkdocs.yml               # MkDocs configuration
├── dawos-cli.spec           # PyInstaller standalone binary spec
├── homebrew/
│   └── dawos-cli.rb         # Homebrew tap formula
├── pyproject.toml           # Project metadata, build config, tool settings
├── Makefile                 # Development shortcuts
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md              # Security policy
├── CODE_OF_CONDUCT.md       # Community guidelines
└── LICENSE                  # MIT License
```

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Shared state** | Profile name, base URL, API key, and flags are set once by the global callback and read by all commands via `state.current`. |
| **Lazy HTTP client** | A single `httpx.Client` is created on first use and reused for all requests within a session. |
| **Consistent errors** | HTTP errors are caught, formatted with Rich, and exit with code 1. |
| **Multi-format output** | `--json` flag or `--format csv/yaml` switches output for scripting. |
| **Confirmation prompts** | Destructive operations require `y/n` confirmation (skip with `--force`). |
| **Modular commands** | Each command file exposes a `typer.Typer()` as `app`, mounted in `app.py`. |

---

## Development

### Environment Setup

```bash
# Clone and set up
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Code Quality Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **[Black](https://black.readthedocs.io/)** | Code formatting | `pyproject.toml` `[tool.black]` |
| **[Pylint](https://pylint.readthedocs.io/)** | Static analysis | `pyproject.toml` `[tool.pylint]` |
| **[Ruff](https://docs.astral.sh/ruff/)** | Fast linting (complementary) | `pyproject.toml` `[tool.ruff]` |
| **[pytest](https://docs.pytest.org/)** | Test framework | `pyproject.toml` `[tool.pytest]` |
| **[pytest-cov](https://pytest-cov.readthedocs.io/)** | Coverage reporting | `pyproject.toml` `[tool.coverage]` |
| **[pre-commit](https://pre-commit.com/)** | Git hooks (black + ruff + pylint) | `.pre-commit-config.yaml` |

### Running Code Quality Checks

```bash
# Format code
black dawos_cli/ tests/

# Run linting
pylint dawos_cli/
ruff check dawos_cli/ tests/

# Run all tests
pytest

# Run tests with coverage
pytest --cov=dawos_cli --cov-report=term-missing

# Run a specific test file
pytest tests/test_commands.py -v

# Run a specific test class
pytest tests/test_commands.py::TestSessionCommands -v

# All checks at once (via Makefile)
make check
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit` to enforce code quality:

```bash
# Install hooks (one-time setup)
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Project Conventions

- **Commands** reside in `dawos_cli/commands/<name>.py`, each exposing `app = typer.Typer()`
- **HTTP calls** use `client.get/post/put/delete` — never raw `httpx`
- **Output** uses `output.table/detail/response/success/error` — never raw `print`
- **Tests** mock at the `dawos_cli.client.get/post/put/delete` level, not `httpx`
- **Formatting** follows [Black](https://black.readthedocs.io/) with 88-character line length
- **Linting** targets Pylint 10.0/10

---

## Testing

The project maintains **426 tests** with **97% coverage** across all source files:

```bash
# Quick test run
pytest

# Full coverage report
pytest --cov=dawos_cli --cov-report=term-missing
```

### Coverage by Module

| Module | Statements | Coverage |
|--------|-----------|----------|
| `dawos_cli/commands/*.py` | 1,024 | 99% |
| `dawos_cli/app.py` | 139 | 79% |
| `dawos_cli/dashboard.py` | 135 | 100% |
| `dawos_cli/output.py` | 107 | 97% |
| `dawos_cli/client.py` | 101 | 96% |
| `dawos_cli/doctor.py` | 83 | 100% |
| `dawos_cli/config.py` | 81 | 98% |
| `dawos_cli/updater.py` | 76 | 49% |
| `dawos_cli/shell.py` | 73 | 66% |
| `dawos_cli/telemetry.py` | 49 | 88% |
| `dawos_cli/state.py` | 12 | 100% |
| **Total** | **1,881** | **97%** |

### Test Categories

- **Core modules** — state, config, client, output, dashboard
- **All 26 command groups** — every subcommand tested
- **New features** — doctor diagnostics, interactive shell, telemetry, output formats
- **Confirmation prompts** — all destructive operations
- **Error handling** — HTTP 401, 404, 422, 500, connection errors
- **SSE streaming** — traffic watch, log stream
- **Edge cases** — empty lists, non-dict responses, KeyboardInterrupt

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up your development environment
- Code style and formatting standards
- Submitting pull requests
- Reporting issues

---

## Security

For information about reporting security vulnerabilities, please see [SECURITY.md](SECURITY.md).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed version history.

---

## API Compatibility

dawos-cli targets **dawos-agent v0.1.x** REST API running on port 8470. All endpoints use `X-API-Key` header authentication.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

---

<p align="center">
  <sub>Built with <a href="https://typer.tiangolo.com/">Typer</a>, <a href="https://rich.readthedocs.io/">Rich</a>, and <a href="https://www.python-httpx.org/">httpx</a>.</sub>
</p>

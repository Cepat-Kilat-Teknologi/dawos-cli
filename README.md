<p align="center">
  <strong>dawos-cli</strong><br>
  <em>Remote CLI client for dawos-agent — manage PPPoE/BNG routers from the command line.</em>
</p>

---

## Overview

**dawos-cli** is a feature-rich command-line interface for managing [accel-ppp](https://accel-ppp.org/) PPPoE/BNG routers through the [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) REST API. It provides comprehensive management capabilities including session control, firewall management, traffic shaping, routing, and real-time monitoring — all from your terminal.

### Key Features

- **26 command groups** covering sessions, firewall, NAT, routing, traffic, pools, DHCP, DNS, VRRP, and more
- **Multi-profile support** for managing multiple BNG nodes from a single installation
- **Live dashboard** (`dawos top`) with real-time session statistics and system metrics
- **SSE streaming** for live traffic monitoring and log tailing
- **Rich terminal output** with tables, panels, and color — or `--json` for scripting
- **Shell completion** for Bash, Zsh, Fish, and PowerShell
- **Guarded configuration** with automatic rollback on failure

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

One command to install dawos-cli system-wide. The installer checks Python, installs [pipx](https://pipx.pypa.io) if needed, and registers the `dawos` command globally.

**macOS / Linux:**

```bash
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli
./installer.sh
```

**Windows (PowerShell — Run as Administrator):**

```powershell
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli
.\installer.ps1
```

> After install, open a **new terminal** and run `dawos --version` to verify.

### Manual Install

#### Option A — pipx (Isolated, Recommended)

```bash
# macOS
brew install pipx && pipx ensurepath

# Linux (Debian/Ubuntu)
sudo apt install pipx && pipx ensurepath

# Windows
pip install --user pipx && python -m pipx ensurepath

# Then install dawos-cli
pipx install git+https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
```

#### Option B — pip (Into Active Environment)

```bash
pip install git+https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
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

### Verify Installation

```bash
dawos --version
# dawos-cli 0.1.0

dawos --help
```

### Configuration Directory

dawos-cli stores profiles in a platform-appropriate location:

| Platform | Default Path |
|----------|-------------|
| **macOS / Linux** | `~/.config/dawos/config.json` |
| **Windows** | `%APPDATA%\dawos\config.json` |

Override with the `DAWOS_CONFIG_DIR` environment variable on any platform.

### Upgrade

```bash
# pipx
pipx upgrade dawos-cli

# pip
pip install --upgrade dawos-cli

# From source
cd dawos-cli && git pull && pip install -e .
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

### 1. Install

**macOS / Linux:**

```bash
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli
./installer.sh
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
cd dawos-cli
.\installer.ps1
```

### 2. Add a Connection Profile

```bash
dawos profile add production http://192.168.1.100:8470 YOUR_API_KEY
```

The first profile added is automatically set as the active profile.

### 3. Test the Connection

```bash
dawos status
```

### 4. Start Managing

```bash
# View system information
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

### Profile Storage

Profiles are stored in `~/.config/dawos/config.json` (XDG-compliant on Linux/macOS).

Override the configuration directory:

```bash
export DAWOS_CONFIG_DIR=/etc/dawos
```

### Profile Management

```bash
# Add a profile with automatic health check
dawos profile add bng1 --url http://10.0.0.1:8470 --key SECRET_KEY

# Add without health check
dawos profile add bng2 --url http://10.0.0.2:8470 --key SECRET_KEY --no-check

# List all profiles
dawos profile list

# Switch the active profile
dawos profile use bng2

# Test connectivity for a specific profile
dawos profile test bng1

# View profile details
dawos profile show bng1

# Remove a profile
dawos profile remove bng2
```

### Per-Command Profile Override

```bash
# Override the active profile for a single command
dawos --profile bng1 session list

# Or use an environment variable
DAWOS_PROFILE=bng1 dawos session list
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DAWOS_PROFILE` | Override the active profile | Active profile from config |
| `DAWOS_CONFIG_DIR` | Override configuration directory | `~/.config/dawos` |

---

## Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--profile NAME` | `-p` | Use a specific profile (overrides active) |
| `--json` | `-j` | Output raw JSON (for scripting and piping) |
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

### Command Groups

| Group | Description | Subcommands |
|-------|-------------|-------------|
| **profile** | Connection profile management | `add`, `list`, `use`, `remove`, `test`, `show` |
| **system** | System information and health | `info`, `health`, `metrics` |
| **service** | BNG service control | `status`, `start`, `stop`, `restart`, `cmd` |
| **session** | PPPoE session management | `list`, `stats`, `find`, `terminate`, `restart`, `by-sid`, `by-ip`, `snapshot`, `drop-by-mac` |
| **config** | BNG configuration | `show`, `update`, `backups`, `revisions`, `diff`, `rollback`, `apply`, `confirm`, `apply-status` |
| **network** | Network interfaces and routing | `interfaces`, `interface`, `interface-config`, `routes`, `add-route`, `del-route`, `dns`, `dns-set`, `vlans`, `vlan-add`, `vlan-del`, `vlan-state` |
| **firewall** | Firewall, sysctl, and conntrack | `status`, `rules`, `save`, `validate`, `sysctl`, `sysctl-set`, `conntrack`, `conntrack-set`, `snmp`, `groups`, `group-add`, `group-del`, `group-members` |
| **nat** | NAT and masquerade management | `status`, `masquerade-on`, `masquerade-off`, `egress`, `egress-set`, `egress-del`, `public-ip-add`, `public-ip-del`, `box-egress`, `box-egress-set` |
| **pppoe** | PPPoE interface management | `interfaces`, `add`, `remove`, `mac-filter`, `mac-add`, `mac-del`, `pado`, `pado-set` |
| **traffic** | Live traffic monitoring | `watch`, `watch-user`, `queue`, `ratelimit`, `ratelimit-restore` |
| **routing** | Dynamic routing protocols | `bgp`, `bgp-routes`, `ospf`, `ospf-neighbors`, `ospf-routes`, `rip`, `rip-routes`, `bfd`, `bfd-peers` |
| **pool** | IP address pool management | `list`, `usage`, `add`, `remove` |
| **conntrack** | Connection tracking | `config`, `table-size`, `table-size-set`, `timeouts`, `timeout-set`, `helpers`, `profiles`, `profile-apply` |
| **events** | Event hooks and webhooks | `hooks`, `hook-add`, `hook-del`, `fire`, `history`, `history-clear` |
| **scheduler** | Scheduled job management | `list`, `add`, `remove`, `run` |
| **dns** | DNS forwarding | `status`, `config`, `config-set`, `flush` |
| **dhcp** | DHCP server and relay | `status`, `leases`, `relay`, `restart`, `relay-restart` |
| **ntp** | NTP time synchronization | `status`, `sources` |
| **lldp** | LLDP link-layer discovery | `status`, `neighbors`, `neighbor` |
| **vrrp** | VRRP high-availability | `status`, `group`, `failover`, `restart` |
| **flow** | Flow accounting (NetFlow/sFlow) | `status`, `collectors`, `stats`, `restart` |
| **monitoring** | Monitoring and metrics | `status`, `metrics`, `metrics-service`, `configure`, `restart` |
| **limits** | Connection limits | `show`, `set`, `interface` |
| **zone** | Zone-based firewall | `list`, `show`, `add`, `remove` |
| **diagnostics** | System diagnostics | `doctor` |
| **logs** | Log viewing and streaming | `tail`, `stream` |

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
│   ├── output.py            # Rich output helpers (table, detail, kvtable, JSON)
│   ├── dashboard.py         # Live full-screen dashboard (Rich Live)
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
├── tests/                   # 344 tests, 99% coverage
│   ├── conftest.py          # Shared fixtures
│   ├── test_app.py          # App-level tests
│   ├── test_client.py       # HTTP client tests
│   ├── test_commands.py     # All command group tests
│   ├── test_config.py       # Configuration tests
│   ├── test_dashboard.py    # Dashboard tests
│   ├── test_output.py       # Output helper tests
│   └── test_state.py        # State management tests
├── pyproject.toml           # Project metadata, build config, tool settings
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
| **JSON mode** | `--json` flag switches all output to raw JSON for piping and scripting. |
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

The project maintains **344 tests** with **99% coverage** across all source files:

```bash
# Quick test run
pytest

# Full coverage report
pytest --cov=dawos_cli --cov-report=term-missing
```

### Coverage by Module

| Module | Statements | Coverage |
|--------|-----------|----------|
| `dawos_cli/*.py` | 429 | 100% |
| `dawos_cli/commands/*.py` | 995 | 100% |
| **Total** | **1,424** | **99.58%** |

### Test Categories

- **Core modules** — state, config, client, output, dashboard
- **All 26 command groups** — every subcommand tested
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

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.2.0] - 2026-07-07

### Added

- **GitHub Actions CI** — Automated lint + test pipeline on push and pull requests (`.github/workflows/ci.yml`)
- **GitHub Actions Release** — PyPI publish + [GitHub Releases](https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases) on version tag (`.github/workflows/release.yml`)
- **Output format options** — `--format csv|yaml` and `-F` shorthand flag alongside existing `--json`
- **Pre-commit hooks** — Black, Ruff, and Pylint run automatically on `git commit` (`.pre-commit-config.yaml`)
- **MkDocs Material documentation** — Full documentation site at [cepat-kilat-teknologi.github.io/dawos-cli](https://cepat-kilat-teknologi.github.io/dawos-cli/) (`docs/`, `mkdocs.yml`)
- **ASCII branding** — Branded logo in `dawos version` and `dawos --version` output
- **`dawos doctor` command** — System diagnostics checking Python version, CLI version, update status, profile, connectivity, shell, config file, and pipx
- **Config export/import** — `dawos profile export` and `dawos profile import` for backup and cross-machine sharing
- **Homebrew tap formula** — `homebrew/dawos-cli.rb` for macOS/Linux installation via `brew install`
- **Interactive shell** — `dawos shell` REPL with tab completion, command history, and readline fallback
- **Command aliases** — Short aliases for power users: `s` (session), `sys` (system), `cfg` (config), `net` (network), `fw` (firewall), `rt` (routing), `mon` (monitoring), `diag` (diagnostics)
- **Standalone binary** — PyInstaller spec for building single-file executables (`dawos-cli.spec`)
- **Opt-in telemetry** — Anonymous usage statistics disabled by default, enabled with `DAWOS_TELEMETRY=1`
- **`dawos update` / `dawos self-update`** — Built-in update commands with confirmation prompt
- **Automatic update check** — Non-blocking daily check on CLI startup with cache

### Changed

- Output module now uses Rich console for JSON output instead of raw `print()` for consistent capture
- Dashboard panel titles cleaned up (removed decorative emoji icons, kept functional symbols)

---

## [0.1.0] - 2026-07-07

### Added

- **26 command groups** with full CLI coverage for dawos-agent v0.1.x API:
  - `system` — System information, health checks, and metrics
  - `service` — BNG service control (start, stop, restart, raw command)
  - `session` — PPPoE session management (list, find, terminate, restart, snapshot, by-sid, by-ip, drop-by-mac)
  - `config` — Configuration management (show, update, backups, revisions, diff, rollback, guarded apply with confirm)
  - `profile` — Multi-profile connection management (add, list, use, remove, test, show)
  - `network` — Network interfaces, routes, VLANs, DNS
  - `firewall` — nftables rules, sysctl, conntrack, SNMP, firewall groups
  - `nat` — NAT masquerade, egress, public IP management, box egress
  - `pppoe` — PPPoE interfaces, MAC filters, PADO delay
  - `traffic` — Live traffic monitoring (SSE streaming), rate limiting, TC queues
  - `routing` — Dynamic routing protocols (BGP, OSPF, RIP, BFD)
  - `pool` — IP address pool management
  - `conntrack` — Connection tracking (config, table size, timeouts, helpers, profiles)
  - `events` — Event hooks and webhooks (CRUD, fire, history)
  - `scheduler` — Scheduled job management
  - `dns` — DNS forwarding (status, config, flush)
  - `dhcp` — DHCP server and relay
  - `ntp` — NTP time synchronization
  - `lldp` — LLDP link-layer discovery
  - `vrrp` — VRRP high-availability
  - `flow` — Flow accounting (NetFlow/sFlow)
  - `monitoring` — Monitoring exporters and metrics
  - `limits` — Connection limits
  - `zone` — Zone-based firewall
  - `diagnostics` — System diagnostics (doctor)
  - `logs` — Log viewing (tail) and real-time streaming (SSE)
- **3 top-level commands**: `status`, `top`, `version`
- **Live dashboard** (`dawos top`) — Full-screen Rich Live dashboard with real-time session stats, system resources, and active session table
- **Multi-profile support** — Manage multiple BNG nodes with named profiles stored in `~/.config/dawos/config.json`
- **Rich terminal output** — Tables, panels, key-value displays, and colored status messages
- **JSON output mode** (`--json` / `-j`) — Raw JSON output for scripting and piping to `jq`
- **SSE streaming** — Real-time traffic monitoring and log streaming with `Ctrl+C` graceful shutdown
- **Confirmation prompts** — All destructive operations require confirmation (skip with `--force`)
- **Shell completion** — Auto-completion for Bash, Zsh, Fish, and PowerShell
- **File-based config input** — `@filename` syntax for config update and apply commands
- **Environment variable support** — `DAWOS_PROFILE` and `DAWOS_CONFIG_DIR` overrides
- **Comprehensive test suite** — 425 tests with 93% code coverage
- **Code quality** — Black formatting, Pylint 10.0/10, Ruff clean, pre-commit hooks
- **Project documentation** — README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, LICENSE, CHANGELOG

### Fixed

- `session terminate` — Corrected payload from `{"sid": sid}` to `{"username": username}` to match API contract
- `config diff` — Added required `backup_name` query parameter
- `config apply` — Added required `content` body parameter with `@filename` support
- `firewall validate` — Changed `ruleset` argument from optional to required to match API contract

### Changed

- Adopted [Black](https://black.readthedocs.io/) as the code formatter (88-char line length)
- Adopted [Pylint](https://pylint.readthedocs.io/) as the primary static analyzer
- Removed 46 unused variable assignments across command modules (identified by Ruff)

---

[0.1.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.1.0
[0.2.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.2.0
[Unreleased]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/compare/v0.2.0...HEAD

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.4.2] - 2026-07-17

### Fixed

- **Version display** — `dawos version` and `dawos doctor` now report the
  correct installed version. Previously `__version__` was hardcoded and could
  drift from the package metadata after a release. Now reads from
  `importlib.metadata.version()` like dawos-agent does.

## [0.4.1] - 2026-07-17

### Security

- **Profile key masking (Phase 3.7)** — `dawos profile list` and
  `dawos profile show` now display API keys as `****...XXXX` (last 4 chars
  only). Full keys are never printed to the terminal, preventing shoulder
  surfing and accidental exposure in screen recordings or shared terminals.

### Changed

- **745 tests** — up from 728 (17 new tests covering profile key masking).
  100% test coverage maintained.

## [0.4.0] - 2026-07-14

### Added

- **Session search commands** — `dawos session search-mac`, `search-ip`, `search-sid` find sessions by MAC address, IP address, or session ID
- **Extended system stats** — `dawos system stats-extended` shows detailed system statistics (CPU, memory, sessions breakdown)
- **IP pool detail** — `dawos pool detail` shows per-pool allocation details with individual assignments
- **Config validation** — `dawos config validate` validates accel-ppp configuration content with line-level error/warning reporting; supports `@filename` syntax to read from file
- **PPPoE runtime config** — `dawos pppoe runtime` shows current PPPoE runtime settings; `dawos pppoe runtime-set` updates service_name, ac_name, verbose with live reload
- **Session history module** — 4 new commands under `dawos history`:
  - `list` — query historical session snapshots with filters (username, IP, date range, pagination)
  - `snapshot` — capture current active sessions into history database
  - `purge` — delete history records older than a timestamp (GDPR/disk management)
  - `stats` — show history database statistics (record count, unique users, DB size)
- **CSV export module** — 2 new commands under `dawos export`:
  - `sessions` — export active sessions as RFC 4180 CSV (stdout or `--output` file)
  - `history` — export history records as CSV with filters (username, IP, date range, limit)
- **RADIUS diagnostics module** — 3 new commands under `dawos radius`:
  - `config` — show RADIUS server configuration (secrets never exposed)
  - `status` — show RADIUS server connection states
  - `check` — health check with reachability test per server
- **`client.get_text()` method** — new HTTP client method for raw text responses (used by CSV export endpoints that return `text/csv`)

### Changed

- **34 command modules** — up from 31 (added `history`, `export`, `radius_cmd`)
- **728 tests** — up from 682 (46 new tests covering all v0.4.0 commands + client error paths)
- **100% test coverage** maintained

## [0.3.3] - 2026-07-12

### Added

- **Network throughput command** — `dawos network throughput` shows per-interface RX/TX byte counters with human-readable formatting (B/KB/MB/GB/TB/PB), matching dawos-agent v0.3.3 `GET /api/v1/network/throughput` endpoint
- **Conntrack flush command** — `dawos conntrack flush` clears the kernel connection tracking table with confirmation prompt (bypass with `--force`), matching dawos-agent v0.3.3 `POST /api/v1/conntrack/flush` endpoint; displays pre-flush entry count

### Security

- **Timeout and transport error handling** — `client.py` now catches `httpx.TimeoutException` and `httpx.RequestError` in all 5 HTTP methods (`get`, `post`, `put`, `delete`, `stream_sse`), preventing unhandled exceptions from leaking internal state
- **Sanitized error output in shell REPL** — `shell.py` catch-all handler now only shows raw messages for safe exception types (`ValueError`, `TypeError`, `KeyError`); all others show a generic message with `--verbose` hint
- **Sanitized error output in wizard engine** — `wizards.py` step runner applies the same type-aware sanitization to prevent internal path/stack leaks in wizard failure messages
- **Plaintext API key warning on export** — `profile export` now warns that the output contains plaintext API keys and sets `0600` permissions on export files
- **Profile import validation** — `import_profiles()` validates each profile dict for required `url` and `api_key` keys; malformed entries are skipped with log warnings
- **Config file permission check** — `_load()` warns when the config file has group- or world-readable permissions (Unix only)
- **Atomic config writes** — `_save()` writes to a temp file with `0600` from creation, then atomically replaces via `os.replace()` to eliminate partial-write and world-readable window risks
- **Rich markup escaping** — `table()`, `detail()`, and `kvtable()` escape untrusted API response data to prevent Rich markup injection
- **Insecure URL warning** — `profile add` warns when using plain HTTP on non-loopback hosts
- **Corrupt config handling** — `_load()` catches `JSONDecodeError` on corrupt config files and exits with an actionable error message

### Added

- **Confirmation prompts on destructive operations** — `bulk ratelimit`, `firewall sysctl-set`, `firewall group-delete`, `nat masquerade-disable`, `nat egress-remove`, `nat public-ip-unbind` now require `--force` or interactive confirmation
- **`output.unwrap()` helper** — DRY response unwrapping replaces inline patterns across 18 command modules

### Fixed

- **Update check suppressed in non-TTY** — pipes, scripts, and CI no longer see update notifications
- **Updater version comparison** — `fetch_latest_tag()` compares all tags by parsed version instead of trusting API list order
- **Updater installs pinned PyPI release** — `run_self_update()` installs `dawos-cli==X.Y.Z` from PyPI instead of `git+URL`
- **Exit code propagation** — `dawos status` propagates failure exit code when agent is unreachable

### Changed

- **682 tests** — up from 675, with 7 new tests covering network throughput and conntrack flush commands (success, confirmation accept/abort, edge cases)

## [0.3.2] - 2026-07-09

### Changed

- **100% test coverage** — up from 97% (587 tests, 2421 statements, 0 uncovered lines)
- **587 tests** — up from 508, with 79 new tests covering all edge cases across 12 modules: updater, shell, wizard, telemetry, firewall, config, output, playbook, app, client, audit, config_cmd

## [0.3.1] - 2026-07-09

### Added

- **Graceful shutdown commands** — `dawos service shutdown` (soft/hard mode with confirmation) and `dawos service shutdown-cancel` to match dawos-agent v0.3.2 shutdown endpoints
- **Readiness probe** — `dawos system ready` for load-balancer health checks (`GET /health/ready`)
- **Config revision content** — `dawos config revision-content <name>` to view full content of a specific config checkpoint revision
- **Config compare** — `dawos config compare --from <a> --to <b>` for unified diff between two config revisions
- **Audit log viewer** — `dawos audit list` with filters (`--method`, `--path`, `--role`, `--status`, `--limit`) for reviewing API mutation history
- **Bulk operations** — `dawos bulk terminate` (batch session termination), `dawos bulk ratelimit` (batch rate changes), `dawos bulk shaper-restore` (batch shaper restoration)
- **Operational playbooks** — `dawos playbook list` and `dawos playbook run <name>` for pre-defined automation sequences (health-check, backup-config, safe-restart)
- **29 command modules** — up from 26, with 3 new modules: `audit`, `bulk`, `playbook`
- **508 tests** — up from 426, with 82 new tests covering all 10 new commands and edge cases

## [0.3.0] - 2026-07-08

### Changed

- **DELETE operations now expect 204 No Content** — All DELETE API calls updated to match dawos-agent 204 standardization. The HTTP client already handled 204 responses correctly; no functional changes required.

### Added

- **Live PPPoE session test report** — 25 commands tested with real PPPoE session (terminate, restart, ratelimit, queue, drop-by-mac)
- **Live integration test report** — 133 total commands tested against real BNG node (`docs/testing/test-report.md`)

### Fixed

- **Traffic ratelimit URL path** — `dawos traffic ratelimit` sent `POST /api/v1/traffic/ratelimit` with username in body, but API expects `POST /api/v1/traffic/ratelimit/{username}` with only rate in body, causing 404 errors
- **Session table hyphen/underscore mismatch** — `rate-limit`, `rx-bytes`, `tx-bytes` fields from accel-ppp were not displayed because `output.table()` and `_print_csv()` only looked up underscored keys; added fallback lookup for hyphenated variants
- **PPPoE add field name** — `dawos pppoe add` sent `{"name": ...}` instead of `{"interface": ...}`, causing 422 errors
- **DNS set field name** — `dawos network dns-set` sent `{"servers": [...]}` instead of `{"nameservers": [...]}`, causing 422 errors
- **NAT egress set field name** — `dawos nat egress-set` sent `{"customer_ip": ...}` instead of `{"target": ...}`, causing 422 errors
- **Conntrack set field name** — `dawos firewall conntrack-set` sent `{"max": N}` instead of `{"max_value": N}`, causing 422 validation errors on `PUT /api/v1/firewall/conntrack`
- **Monitoring configure redesign** — `dawos monitoring configure` sent `{"target": ..., "value": ...}` but API expects `ConfigureExporterRequest` with `{"service": ..., "enable": bool}`; redesigned CLI to use `--service`/`-s` and `--enable/--disable` flags

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
  - `profile` — Multi-profile connection management (add, list, use, remove, test, export, import)
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

[0.4.1]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/compare/v0.3.3...v0.4.0
[0.3.3]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.3.3
[0.3.2]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.3.2
[0.3.1]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.3.1
[0.3.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.3.0
[0.1.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.1.0
[0.2.0]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/releases/tag/v0.2.0
[0.4.2]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/compare/v0.4.1...v0.4.2
[Unreleased]: https://github.com/Cepat-Kilat-Teknologi/dawos-cli/compare/v0.4.2...HEAD

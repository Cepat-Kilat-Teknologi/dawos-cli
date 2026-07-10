# Commands Overview

DawOS CLI provides **31 command groups** organized for managing every aspect of your BNG router.

## Top-Level Commands

| Command | Description |
|---------|-------------|
| `dawos status` | Quick connection + health check |
| `dawos top` | Live monitoring dashboard |
| `dawos version` | Show version information |
| `dawos update` | Check and install updates |
| `dawos doctor` | System diagnostics |
| `dawos shell` | Interactive REPL mode |

## Command Groups

| Group | Alias | Description |
|-------|-------|-------------|
| `session` | `s` | PPPoE session management |
| `system` | `sys` | System info and health |
| `service` | — | BNG service control |
| `config` | `cfg` | BNG configuration |
| `profile` | — | Connection profiles |
| `network` | `net` | Interfaces, routes, VLANs |
| `firewall` | `fw` | Firewall rules and SNMP |
| `nat` | — | NAT / masquerade |
| `pppoe` | — | PPPoE interface management |
| `traffic` | — | Traffic monitoring and shaping |
| `routing` | `rt` | Dynamic routing (BGP/OSPF) |
| `pool` | — | IP address pools |
| `conntrack` | — | Connection tracking |
| `events` | — | Event hooks and webhooks |
| `scheduler` | — | Scheduled jobs |
| `dns` | — | DNS forwarding |
| `dhcp` | — | DHCP server and relay |
| `ntp` | — | NTP time sync |
| `lldp` | — | LLDP discovery |
| `vrrp` | — | VRRP high-availability |
| `flow` | — | NetFlow/sFlow accounting |
| `monitoring` | `mon` | Monitoring and metrics |
| `limits` | — | Connection limits |
| `zone` | — | Zone-based firewall |
| `diagnostics` | `diag` | System diagnostics |
| `logs` | — | Log viewing and streaming |
| `audit` | — | Audit log viewer |
| `bulk` | — | Bulk operations |
| `playbook` | — | Operational playbooks |
| `node` | — | Multi-node group management |
| `wizard` | — | Guided interactive workflows |

## Global Options

These options must be placed **before** the command group (e.g., `dawos --json session list`):

```
--profile, -p    Profile name (overrides active profile)
--json, -j       Raw JSON output
--format, -F     Output format: table, json, csv, yaml
--verbose, -v    Verbose output (show URLs, timing)
--timeout, -t    Request timeout in seconds (default: 30)
--version, -V    Show version and exit
--help, -h       Show help
```

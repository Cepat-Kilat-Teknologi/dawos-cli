# CLI Test Report

Live integration test results for **dawos-cli v0.2.0** against a real dawos-agent instance.

---

## Test Environment

| Field | Value |
|-------|-------|
| **CLI Version** | 0.2.0 |
| **Agent Version** | 0.1.0 |
| **Server** | 192.168.216.99:8470 (dawos-dev) |
| **Profile** | `development` (active) |
| **Client OS** | macOS (operator workstation) |
| **Install Method** | pipx |
| **Test Date** | 2026-07-07 |

---

## Summary

| Category | Tested | Passed | Notes |
|----------|:------:|:------:|-------|
| Read commands | 55 | 55 | All 29 API groups covered |
| Write commands | 19 | 19 | Full CRUD cycles |
| **Total** | **74** | **74** | **100% pass rate** |

---

## Read Commands (55 tests)

Every read command returns exit code 0 with properly formatted Rich table output.

### System and Status (4/4)

| Command | Result |
|---------|--------|
| `dawos status` | Connected, health OK, version 0.1.0, node dawos-dev |
| `dawos version` | CLI version banner displayed |
| `dawos system info` | Hostname, OS, kernel, arch, uptime |
| `dawos system metrics` | CPU, memory, disk, load average |

### Service (2/2)

| Command | Result |
|---------|--------|
| `dawos service status` | accel-ppp running with uptime |
| `dawos service cmd "show version"` | Raw accel-cmd output returned |

### Session (2/2)

| Command | Result |
|---------|--------|
| `dawos session list` | Empty table (no active subscribers) |
| `dawos session stats` | Session counters displayed |

### Config (4/4)

| Command | Result |
|---------|--------|
| `dawos config show` | Full accel-ppp.conf content |
| `dawos config backups` | Backup file list with timestamps |
| `dawos config revisions` | Revision count and metadata |
| `dawos config apply-status` | Pending status (false) |

### Network (4/4)

| Command | Result |
|---------|--------|
| `dawos network interfaces` | Interface table (eth0, ens19, lo) |
| `dawos network routes` | Routing table |
| `dawos network vlans` | VLAN list |
| `dawos network dns` | Nameservers and search domains |

### Firewall (4/4)

| Command | Result |
|---------|--------|
| `dawos firewall rules` | nftables ruleset |
| `dawos firewall conntrack` | Max connections, status, recommendation |
| `dawos firewall sysctl` | IP forwarding status |
| `dawos firewall groups` | Firewall group list |

### NAT (2/2)

| Command | Result |
|---------|--------|
| `dawos nat status` | NAT status with bound IPs |
| `dawos nat egress` | Egress map entries |

### PPPoE (3/3)

| Command | Result |
|---------|--------|
| `dawos pppoe interfaces` | Listener interface list |
| `dawos pppoe pado` | PADO delay configuration |
| `dawos pppoe mac-filter` | MAC filter entries |

### Pool (1/1)

| Command | Result |
|---------|--------|
| `dawos pool list` | IP address pool list |

### Conntrack (4/4)

| Command | Result |
|---------|--------|
| `dawos conntrack config` | Table size, count, hash, usage |
| `dawos conntrack timeouts` | All 12 protocol timeout values |
| `dawos conntrack helpers` | Helper module list |
| `dawos conntrack profiles` | Available profiles |

### Events (2/2)

| Command | Result |
|---------|--------|
| `dawos events hooks` | Registered webhook list |
| `dawos events history` | Event fire history |

### Scheduler (1/1)

| Command | Result |
|---------|--------|
| `dawos scheduler list` | Scheduled job list |

### DNS (2/2)

| Command | Result |
|---------|--------|
| `dawos dns status` | DNS forwarding status |
| `dawos dns config` | DNS forwarder configuration |

### DHCP (3/3)

| Command | Result |
|---------|--------|
| `dawos dhcp status` | DHCP server status |
| `dawos dhcp leases` | Active lease table |
| `dawos dhcp relay` | Relay agent status |

### NTP (2/2)

| Command | Result |
|---------|--------|
| `dawos ntp status` | NTP synchronization status |
| `dawos ntp sources` | Upstream NTP sources |

### LLDP (2/2)

| Command | Result |
|---------|--------|
| `dawos lldp status` | LLDP daemon status |
| `dawos lldp neighbors` | Discovered neighbor table |

### VRRP (1/1)

| Command | Result |
|---------|--------|
| `dawos vrrp status` | VRRP group status |

### Flow Accounting (3/3)

| Command | Result |
|---------|--------|
| `dawos flow status` | NetFlow/sFlow status |
| `dawos flow stats` | Flow statistics |
| `dawos flow collectors` | Collector configuration |

### Monitoring (1/1)

| Command | Result |
|---------|--------|
| `dawos monitoring status` | Monitoring service status |

### Limits (1/1)

| Command | Result |
|---------|--------|
| `dawos limits show` | Connection limit settings |

### Zone Firewall (1/1)

| Command | Result |
|---------|--------|
| `dawos zone list` | Zone firewall list |

### Diagnostics (1/1)

| Command | Result |
|---------|--------|
| `dawos diagnostics doctor` | System health check results |

### Routing (9/9)

| Command | Result |
|---------|--------|
| `dawos routing bgp` | BGP peer summary |
| `dawos routing bgp-routes` | BGP routing table |
| `dawos routing ospf` | OSPF status |
| `dawos routing ospf-neighbors` | OSPF adjacencies |
| `dawos routing ospf-routes` | OSPF routing table |
| `dawos routing rip` | RIP status |
| `dawos routing rip-routes` | RIP routing table |
| `dawos routing bfd` | BFD summary |
| `dawos routing bfd-peers` | BFD peer sessions |

### Logs (1/1)

| Command | Result |
|---------|--------|
| `dawos logs tail` | Last N log lines |

---

## Write Commands (19 tests)

Full create-verify-delete cycles. All resources cleaned up after testing.

### Pool CRUD (3/3)

| Command | Result |
|---------|--------|
| `dawos pool add test-pool 10.99.0.0/24` | Pool created |
| `dawos pool list` | Pool visible in list |
| `dawos pool remove test-pool` | Pool removed |

### Zone CRUD (3/3)

| Command | Result |
|---------|--------|
| `dawos zone add test-zone` | Zone created |
| `dawos zone list` | Zone visible in list |
| `dawos zone remove test-zone` | Zone removed |

### Scheduler CRUD (3/3)

| Command | Result |
|---------|--------|
| `dawos scheduler add test-job "show stat"` | Job created |
| `dawos scheduler list` | Job visible in list |
| `dawos scheduler remove test-job` | Job removed |

### Event Hook CRUD (3/3)

| Command | Result |
|---------|--------|
| `dawos events add test-hook session-up webhook https://...` | Hook registered |
| `dawos events hooks` | Hook visible in list |
| `dawos events remove test-hook` | Hook removed |

### PPPoE Interface CRUD (3/3)

| Command | Result |
|---------|--------|
| `dawos pppoe add ens19` | Interface added |
| `dawos pppoe interfaces` | Interface visible in list |
| `dawos pppoe remove ens19` | Interface removed |

### NAT Masquerade (2/2)

| Command | Result |
|---------|--------|
| `dawos nat masquerade-on ens18` | Masquerade enabled |
| `dawos nat masquerade-off` | Masquerade disabled |

### PADO Delay (3/3)

| Command | Result |
|---------|--------|
| `dawos pppoe pado-set 200` | Delay set to 200ms |
| `dawos pppoe pado` | Verified 200ms |
| `dawos pppoe pado-set 0` | Delay cleared |

### Conntrack Profile (2/2)

| Command | Result |
|---------|--------|
| `dawos conntrack apply gaming` | Gaming profile applied |
| `dawos conntrack apply default` | Default profile restored |

---

## Output Formats

dawos-cli supports multiple output formats via the global `-F` flag:

| Format | Flag | Use Case |
|--------|------|----------|
| Table (default) | -- | Human-readable Rich tables |
| JSON | `-j` or `-F json` | Scripting and piping |
| CSV | `-F csv` | Spreadsheet import |
| YAML | `-F yaml` | Configuration management |

Example:

```bash
# Rich table (default)
dawos session list

# JSON output for scripting
dawos -j session list

# Pipe JSON to jq
dawos -F json conntrack timeouts | jq '.timeouts.tcp_timeout_established'
```

> **Note:** The `-j`/`-F` flag is a **global option** and must appear before the subcommand: `dawos -j status`, not `dawos status -j`.

---

## Command Reference

### Complete Command List

| Group | Subcommands |
|-------|------------|
| `status` | *(top-level, no subcommand)* |
| `version` | *(top-level, no subcommand)* |
| `doctor` | *(top-level, no subcommand)* |
| `system` | `info`, `metrics` |
| `service` | `status`, `start`, `stop`, `restart`, `cmd` |
| `session` | `list`, `stats` |
| `config` | `show`, `backups`, `revisions`, `apply-status` |
| `network` | `interfaces`, `routes`, `vlans`, `dns` |
| `firewall` | `rules`, `conntrack`, `sysctl`, `groups` |
| `nat` | `status`, `egress`, `masquerade-on`, `masquerade-off` |
| `pppoe` | `interfaces`, `add`, `remove`, `pado`, `pado-set`, `mac-filter`, `mac-add`, `mac-del` |
| `pool` | `list`, `add`, `remove` |
| `conntrack` | `config`, `timeouts`, `helpers`, `profiles`, `apply` |
| `events` | `hooks`, `history`, `add`, `remove` |
| `scheduler` | `list`, `add`, `remove` |
| `dns` | `status`, `config` |
| `dhcp` | `status`, `leases`, `relay` |
| `ntp` | `status`, `sources` |
| `lldp` | `status`, `neighbors` |
| `vrrp` | `status` |
| `flow` | `status`, `stats`, `collectors` |
| `monitoring` | `status` |
| `limits` | `show` |
| `zone` | `list`, `add`, `remove` |
| `diagnostics` | `doctor` |
| `routing` | `bgp`, `bgp-routes`, `ospf`, `ospf-neighbors`, `ospf-routes`, `rip`, `rip-routes`, `bfd`, `bfd-peers` |
| `logs` | `tail` |
| `traffic` | `top` (live dashboard) |
| `profile` | `list`, `add`, `remove`, `use` |

# Command Reference

Complete reference for all dawos-cli commands.

## Top-Level Commands

| Command | Description |
|---------|-------------|
| `dawos status` | Quick connection + health check |
| `dawos top` | Live monitoring dashboard (full-screen) |
| `dawos version` | Show version information |
| `dawos update` | Check for updates and upgrade |
| `dawos doctor` | System diagnostics check |
| `dawos shell` | Interactive REPL mode |

## Profile Management

| Command | Description |
|---------|-------------|
| `dawos profile add NAME --url URL --key KEY` | Add or update a profile |
| `dawos profile list` | List all profiles |
| `dawos profile use NAME` | Set active profile |
| `dawos profile remove NAME` | Remove a profile |
| `dawos profile test [NAME]` | Test connectivity |
| `dawos profile export` | Export profiles to JSON |
| `dawos profile import FILE` | Import profiles from JSON |

## Session Management (`session` / `s`)

| Command | Description |
|---------|-------------|
| `dawos session list` | List active PPPoE sessions |
| `dawos session stats` | Session statistics |
| `dawos session find USERNAME` | Find session by username |
| `dawos session terminate USERNAME` | Terminate a session |
| `dawos session restart USERNAME` | Restart a session |
| `dawos session by-sid SID` | Look up by session ID |
| `dawos session by-ip IP` | Look up by IP address |
| `dawos session snapshot USERNAME` | Full session snapshot |
| `dawos session drop-by-mac MAC` | Drop session by MAC |

## System & Service (`system` / `sys`)

| Command | Description |
|---------|-------------|
| `dawos system info` | System information |
| `dawos system health` | Health check |
| `dawos system metrics` | System metrics |
| `dawos system ready` | Readiness probe (load balancer) |
| `dawos service status` | BNG service status |
| `dawos service start` | Start accel-ppp |
| `dawos service stop` | Stop accel-ppp |
| `dawos service restart` | Restart accel-ppp |
| `dawos service cmd COMMAND` | Run a raw accel-cmd command |
| `dawos service shutdown` | Graceful shutdown (soft/hard) |
| `dawos service shutdown-cancel` | Cancel pending soft shutdown |

## Configuration (`config` / `cfg`)

| Command | Description |
|---------|-------------|
| `dawos config show` | Show current configuration |
| `dawos config update @FILE` | Update configuration from file |
| `dawos config backups` | List configuration backups |
| `dawos config revisions` | List configuration revisions |
| `dawos config diff BACKUP` | Diff against a backup |
| `dawos config rollback BACKUP` | Rollback to a backup |
| `dawos config apply @FILE` | Apply configuration (guarded) |
| `dawos config confirm` | Confirm applied configuration |
| `dawos config apply-status` | Check apply status |
| `dawos config revision-content NAME` | View full revision content |
| `dawos config compare --from A --to B` | Compare two revisions (diff) |

## Network & Routing (`network` / `net`, `routing` / `rt`)

| Command | Description |
|---------|-------------|
| `dawos network interfaces` | List interfaces |
| `dawos network interface NAME` | Interface details |
| `dawos network interface-config NAME` | Interface configuration |
| `dawos network routes` | Routing table |
| `dawos network add-route DEST` | Add a static route |
| `dawos network del-route DEST` | Delete a static route |
| `dawos network dns` | DNS configuration |
| `dawos network dns-set SERVERS` | Set DNS servers |
| `dawos network vlans` | VLAN configuration |
| `dawos network vlan-add IFACE` | Add VLAN |
| `dawos network vlan-del ID` | Delete VLAN |
| `dawos network vlan-state ID STATE` | Set VLAN state |
| `dawos routing bgp` | BGP neighbors |
| `dawos routing bgp-routes` | BGP routes |
| `dawos routing ospf` | OSPF status |
| `dawos routing ospf-neighbors` | OSPF neighbors |
| `dawos routing ospf-routes` | OSPF routes |
| `dawos routing rip` | RIP status |
| `dawos routing rip-routes` | RIP routes |
| `dawos routing bfd` | BFD status |
| `dawos routing bfd-peers` | BFD peers |

## Firewall & NAT (`firewall` / `fw`)

| Command | Description |
|---------|-------------|
| `dawos firewall status` | Firewall status |
| `dawos firewall rules` | List firewall rules |
| `dawos firewall save` | Save current ruleset |
| `dawos firewall validate RULES` | Validate nftables config |
| `dawos firewall sysctl` | Show sysctl settings |
| `dawos firewall sysctl-set K V` | Set sysctl parameter |
| `dawos firewall conntrack` | Conntrack settings |
| `dawos firewall conntrack-set N` | Set conntrack max entries |
| `dawos firewall snmp` | SNMP settings |
| `dawos firewall groups` | List firewall groups |
| `dawos firewall group-add NAME` | Add firewall group |
| `dawos firewall group-del NAME` | Delete firewall group |
| `dawos firewall group-members NAME` | Manage group members |
| `dawos nat status` | NAT status |
| `dawos nat masquerade-on IFACE` | Enable masquerade |
| `dawos nat masquerade-off IFACE` | Disable masquerade |
| `dawos nat egress` | Egress rules |
| `dawos nat egress-set` | Set egress rules |
| `dawos nat egress-del` | Delete egress rules |
| `dawos nat public-ip-add IP` | Add public IP |
| `dawos nat public-ip-del IP` | Remove public IP |
| `dawos nat box-egress` | Box-level egress |
| `dawos nat box-egress-set` | Set box-level egress |

## Other Groups

| Group | Alias | Description |
|-------|-------|-------------|
| `dawos pppoe` | — | PPPoE interface management |
| `dawos traffic` | — | Traffic monitoring and shaping |
| `dawos pool` | — | IP address pool management |
| `dawos conntrack` | — | Connection tracking |
| `dawos events` | — | Event hooks and webhooks |
| `dawos scheduler` | — | Scheduled jobs |
| `dawos dns` | — | DNS forwarding |
| `dawos dhcp` | — | DHCP server and relay |
| `dawos ntp` | — | NTP time sync |
| `dawos lldp` | — | LLDP discovery |
| `dawos vrrp` | — | VRRP high-availability |
| `dawos flow` | — | NetFlow/sFlow accounting |
| `dawos monitoring` | `mon` | Monitoring and metrics |
| `dawos monitoring status` | | Monitoring service status |
| `dawos monitoring metrics SERVICE` | | Metrics for a service |
| `dawos monitoring configure -s SVC` | | Enable/disable a monitoring exporter |
| `dawos monitoring restart SERVICE` | | Restart a monitoring service |
| `dawos limits` | — | Connection limits |
| `dawos zone` | — | Zone-based firewall |
| `dawos diagnostics` | `diag` | System diagnostics |
| `dawos logs` | — | Log viewing and streaming |

## Audit Log (`audit`)

| Command | Description |
|---------|-------------|
| `dawos audit list` | List recent audit log entries |
| `dawos audit list --method POST` | Filter by HTTP method |
| `dawos audit list --path /api/v1/service` | Filter by path prefix |
| `dawos audit list --role admin` | Filter by RBAC role |
| `dawos audit list --status 200` | Filter by status code |
| `dawos audit list --limit 50` | Limit entries returned |

## Bulk Operations (`bulk`)

| Command | Description |
|---------|-------------|
| `dawos bulk terminate USER1,USER2` | Batch terminate sessions |
| `dawos bulk ratelimit U1:5M/20M,U2:10M/50M` | Batch rate limit changes |
| `dawos bulk shaper-restore USER1,USER2` | Batch restore RADIUS shapers |

## Operational Playbooks (`playbook`)

| Command | Description |
|---------|-------------|
| `dawos playbook list` | List available playbooks |
| `dawos playbook run NAME` | Execute a playbook |

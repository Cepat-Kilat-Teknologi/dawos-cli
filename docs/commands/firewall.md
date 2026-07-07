# Firewall & NAT

## Firewall

```bash
dawos firewall status           # Firewall status overview
dawos firewall rules            # List firewall rules
dawos firewall save             # Save current ruleset
dawos firewall validate RULES   # Validate nftables configuration
dawos firewall sysctl           # Show sysctl settings
dawos firewall sysctl-set K V   # Set a sysctl parameter
dawos firewall conntrack        # Show conntrack settings
dawos firewall conntrack-set K V # Set conntrack parameter
dawos firewall snmp             # SNMP firewall settings
dawos firewall groups           # List firewall groups
dawos firewall group-add NAME   # Add a firewall group
dawos firewall group-del NAME   # Delete a firewall group
dawos firewall group-members NAME ELEMENTS  # Manage group members
```

Alias: `dawos fw rules`, `dawos fw status`, etc.

## NAT

```bash
dawos nat status               # NAT / masquerade status
dawos nat masquerade-on IFACE  # Enable masquerade on interface
dawos nat masquerade-off IFACE # Disable masquerade on interface
dawos nat egress               # Show egress rules
dawos nat egress-set           # Set egress rules
dawos nat egress-del           # Delete egress rules
dawos nat public-ip-add IP     # Add a public IP
dawos nat public-ip-del IP     # Remove a public IP
dawos nat box-egress           # Show box-level egress
dawos nat box-egress-set       # Set box-level egress
```

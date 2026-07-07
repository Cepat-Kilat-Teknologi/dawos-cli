# Network & Routing

## Network

```bash
dawos network interfaces        # List network interfaces
dawos network interface NAME    # Show interface details
dawos network interface-config NAME  # Get interface configuration
dawos network routes            # Show routing table
dawos network add-route DEST    # Add a static route
dawos network del-route DEST    # Delete a static route
dawos network dns               # Show DNS configuration
dawos network dns-set SERVERS   # Set DNS servers
dawos network vlans             # List VLANs
dawos network vlan-add IFACE    # Add a VLAN
dawos network vlan-del ID       # Delete a VLAN
dawos network vlan-state ID STATE  # Set VLAN state
```

Alias: `dawos net interfaces`, `dawos net routes`, etc.

## Routing

```bash
dawos routing bgp              # BGP neighbor summary
dawos routing bgp-routes       # BGP routing table
dawos routing ospf             # OSPF status
dawos routing ospf-neighbors   # OSPF neighbor table
dawos routing ospf-routes      # OSPF routes
dawos routing rip              # RIP status
dawos routing rip-routes       # RIP routing table
dawos routing bfd              # BFD status
dawos routing bfd-peers        # BFD peer table
```

Alias: `dawos rt bgp`, `dawos rt ospf`, etc.

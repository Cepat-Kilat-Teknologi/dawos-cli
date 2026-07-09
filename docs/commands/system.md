# System & Service

## System Commands

```bash
dawos system info          # System information
dawos system health        # Health check
dawos system metrics       # System metrics
dawos system ready         # Readiness probe (load balancer)
```

Aliases: `dawos sys info`, `dawos sys health`, `dawos sys metrics`, `dawos sys ready`

## Service Commands

```bash
dawos service status           # BNG service status
dawos service start            # Start accel-ppp
dawos service stop             # Stop accel-ppp
dawos service restart          # Restart accel-ppp
dawos service cmd COMMAND      # Run a raw accel-cmd command
dawos service shutdown         # Graceful shutdown (soft/hard)
dawos service shutdown-cancel  # Cancel pending soft shutdown
```

### Graceful Shutdown

Initiate a graceful shutdown of accel-ppp:

```bash
# Soft shutdown — drain existing sessions, reject new ones
dawos service shutdown --mode soft

# Hard shutdown — terminate all sessions immediately
dawos service shutdown --mode hard --force

# Cancel a pending soft shutdown
dawos service shutdown-cancel
```

!!! warning
    Service start/stop/restart and shutdown commands require confirmation. Use `--force` to skip.

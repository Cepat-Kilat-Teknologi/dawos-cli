# System & Service

## System Commands

```bash
dawos system info          # System information
dawos system health        # Health check
dawos system metrics       # System metrics
```

Aliases: `dawos sys info`, `dawos sys health`, `dawos sys metrics`

## Service Commands

```bash
dawos service status       # BNG service status
dawos service start        # Start accel-ppp
dawos service stop         # Stop accel-ppp
dawos service restart      # Restart accel-ppp
dawos service cmd COMMAND  # Run a raw accel-cmd command
```

!!! warning
    Service start/stop/restart commands require confirmation. Use `--force` to skip.

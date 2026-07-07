# Multi-Node Management

Manage multiple BNG nodes from a single CLI installation using profiles.

## Setting Up Multiple Profiles

```bash
# Production BNG
dawos profile add prod --url http://192.168.1.1:8470 --key PROD_KEY

# Staging BNG
dawos profile add staging --url http://10.0.0.1:8470 --key STAGING_KEY

# Development BNG
dawos profile add dev --url http://172.16.0.1:8470 --key DEV_KEY
```

## Switching Between Nodes

```bash
# Set active profile
dawos profile use prod

# Or use --profile flag for one-off commands
dawos --profile staging session list
dawos -p dev system info
```

## Environment Variable Override

```bash
# Useful in scripts
export DAWOS_PROFILE=prod
dawos session list  # uses prod profile
```

## Backup & Restore

```bash
# Export all profiles
dawos profile export > ~/dawos-profiles-backup.json

# Import on another machine
dawos profile import dawos-profiles-backup.json
```

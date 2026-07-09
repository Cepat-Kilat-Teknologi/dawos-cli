# Scripting & Automation

DawOS CLI is designed for automation with `--json` and `--format` output modes.

> **Note:** `--json`, `-j`, `--format`, and `-F` are global options — they must be placed **before** the command group (e.g., `dawos --json session list`, not `dawos session list --json`).

## JSON Output

```bash
# Get raw JSON for piping
dawos --json session list

# Parse with jq
dawos -j session list | jq '.[].username'

# Count active sessions
dawos -j session list | jq 'length'
```

## CSV Output

```bash
# Export to CSV for spreadsheets
dawos -F csv session list > sessions.csv

# Use with standard Unix tools
dawos -F csv session list | cut -d',' -f1,2
```

## YAML Output

```bash
dawos -F yaml session list
```

## Shell Scripts

```bash
#!/bin/bash
# Monitor session count and alert if below threshold

COUNT=$(dawos -j session list | jq 'length')
if [ "$COUNT" -lt 10 ]; then
    echo "ALERT: Only $COUNT sessions active!"
fi
```

## Cron Jobs

```bash
# Export session stats every hour
0 * * * * dawos --profile prod -j session stats >> /var/log/dawos-stats.jsonl

# Daily session report
0 8 * * * dawos -F csv session list > /reports/sessions-$(date +%F).csv
```

## CI/CD Integration

```bash
# Disable update checks in CI
export DAWOS_NO_UPDATE_CHECK=1

# Use environment variable for profile
export DAWOS_PROFILE=prod
dawos -j system health
```

## Error Handling

DawOS CLI uses standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (connection failed, not found, etc.) |
| `2` | Usage error (wrong arguments) |

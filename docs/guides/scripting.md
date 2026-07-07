# Scripting & Automation

dawos-cli is designed for automation with `--json` and `--format` output modes.

## JSON Output

```bash
# Get raw JSON for piping
dawos session list --json

# Parse with jq
dawos session list --json | jq '.[].username'

# Count active sessions
dawos session list --json | jq 'length'
```

## CSV Output

```bash
# Export to CSV for spreadsheets
dawos session list --format csv > sessions.csv

# Use with standard Unix tools
dawos session list --format csv | cut -d',' -f1,2
```

## YAML Output

```bash
dawos session list --format yaml
```

## Shell Scripts

```bash
#!/bin/bash
# Monitor session count and alert if below threshold

COUNT=$(dawos session list --json | jq 'length')
if [ "$COUNT" -lt 10 ]; then
    echo "ALERT: Only $COUNT sessions active!"
fi
```

## Cron Jobs

```bash
# Export session stats every hour
0 * * * * dawos --profile prod session stats --json >> /var/log/dawos-stats.jsonl

# Daily session report
0 8 * * * dawos session list --format csv > /reports/sessions-$(date +%F).csv
```

## CI/CD Integration

```bash
# Disable update checks in CI
export DAWOS_NO_UPDATE_CHECK=1

# Use environment variable for profile
export DAWOS_PROFILE=prod
dawos system health --json
```

## Error Handling

dawos-cli uses standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (connection failed, not found, etc.) |
| `2` | Usage error (wrong arguments) |

# Configuration

## Profiles

DawOS CLI uses **profiles** to manage connections to multiple BNG nodes. Each profile stores a URL and API key.

### Config Location

| Platform | Path |
|----------|------|
| Linux/macOS | `~/.config/dawos/config.json` |
| macOS (XDG) | `$XDG_CONFIG_HOME/dawos/config.json` |
| Windows | `%APPDATA%\dawos\config.json` |
| Custom | `$DAWOS_CONFIG_DIR/config.json` |

### Managing Profiles

```bash
# Add a profile
dawos profile add prod --url http://192.168.1.1:8470 --key YOUR_KEY

# Add without connectivity check
dawos profile add staging --url http://10.0.0.1:8470 --key KEY --no-check

# List all profiles
dawos profile list

# Switch active profile
dawos profile use staging

# Test connectivity
dawos profile test prod

# Remove a profile
dawos profile remove staging
```

### Export / Import

Back up and share profiles across machines:

```bash
# Export all profiles to a file
dawos profile export > profiles.json

# Import profiles from a file
dawos profile import profiles.json

# Export a single profile
dawos profile export --name prod > prod-profile.json
```

!!! warning "Security"
    Exported files contain API keys. Handle them securely and do not commit to version control.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DAWOS_PROFILE` | Override active profile |
| `DAWOS_CONFIG_DIR` | Custom config directory |
| `DAWOS_NO_UPDATE_CHECK` | Disable update notifications (`1` to disable) |
| `DAWOS_TELEMETRY` | Enable anonymous usage stats (`1` to enable) |

## Output Formats

All commands support multiple output formats:

```bash
dawos session list                    # Rich table (default)
dawos --json session list             # JSON output
dawos -F csv session list             # CSV for spreadsheets
dawos -F yaml session list            # YAML output
```

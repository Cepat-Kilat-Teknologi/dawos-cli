# Quick Start

Get connected to your BNG node in under 2 minutes.

## 1. Install

```bash
pip install dawos-cli
```

## 2. Get Your API Key

The API key is the `DAWOS_API_KEY` value on your dawos-agent server:

```bash
sudo cat /etc/dawos-agent/agent.env | grep DAWOS_API_KEY
```

!!! info "Key not set yet?"
    Generate one on the server:
    ```bash
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    ```
    Then add it to `/etc/dawos-agent/agent.env`:
    ```
    DAWOS_API_KEY=your_generated_key_here
    ```
    Restart the agent: `sudo systemctl restart dawos-agent`

## 3. Add Your BNG Node

```bash
dawos profile add prod --url http://YOUR_SERVER_IP:8470 --key YOUR_API_KEY
```

The CLI will verify connectivity automatically:

```
ℹ Checking connectivity to http://192.168.1.1:8470 ...
✓ Connected — node=bng-prod-01 version=0.1.0
✓ Profile prod saved.
```

## 4. Check Connection

```bash
dawos status
```

## 5. Explore

```bash
# List active PPPoE sessions
dawos session list

# View session stats
dawos session stats

# Live monitoring dashboard
dawos top

# System health
dawos system info

# See all commands
dawos --help
```

## Next Steps

- [Configuration](configuration.md) — Multi-profile management
- [Command Reference](../commands/reference.md) — Full command list
- [Scripting Guide](../guides/scripting.md) — Automation with `--json`

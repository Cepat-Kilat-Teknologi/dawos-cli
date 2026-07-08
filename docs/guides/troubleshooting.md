# Troubleshooting

## `dawos doctor`

Run the built-in diagnostic tool first:

```bash
dawos doctor
```

This checks Python version, connectivity, profile status, and more.

## Common Issues

### Connection Refused

```
ERROR: Cannot reach http://192.168.1.1:8470/health
```

**Causes:**
- dawos-agent is not running on the server
- Wrong IP address or port
- Firewall blocking port 8470

**Fix:**
```bash
# On the server:
sudo systemctl status dawos-agent
sudo systemctl start dawos-agent

# Check if port is open:
curl http://SERVER_IP:8470/health
```

### Authentication Failed (401)

```
ERROR: 401 Unauthorized
```

**Fix:** Verify your API key matches the server:
```bash
# On the server:
sudo cat /etc/dawos-agent/agent.env | grep DAWOS_API_KEY

# Update your profile:
dawos profile add prod --url http://SERVER:8470 --key CORRECT_KEY
```

### No Active Profile

```
ERROR: No profile configured
```

**Fix:**
```bash
dawos profile add prod --url http://SERVER:8470 --key YOUR_KEY
```

### Command Not Found

```
bash: dawos: command not found
```

**Fix:**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
pip install dawos-cli
```

### Update Check Slow

The update check runs at most once per 24 hours. To disable:
```bash
export DAWOS_NO_UPDATE_CHECK=1
```

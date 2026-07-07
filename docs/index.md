# dawos-cli

**Remote CLI client for dawos-agent — manage PPPoE/BNG routers from the command line.**

<div class="grid cards" markdown>

- :material-rocket-launch: **Quick Start**

    Get up and running in under 2 minutes.

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

- :material-download: **Installation**

    Install on Linux, macOS, or Windows.

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

- :material-console: **Commands**

    Full reference for all 26 command groups + 6 top-level commands.

    [:octicons-arrow-right-24: Command Reference](commands/reference.md)

- :material-cog: **Configuration**

    Multi-profile setup for managing multiple BNG nodes.

    [:octicons-arrow-right-24: Configuration](getting-started/configuration.md)

</div>

## What is dawos-cli?

`dawos-cli` is a command-line tool for managing PPPoE/BNG routers powered by [accel-ppp](https://accel-ppp.org/) through the [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) REST API.

### Features

- :material-server-network: **Full BNG Control** — Sessions, firewall, routing, NAT, traffic shaping, and more
- :material-monitor-dashboard: **Live Dashboard** — Real-time monitoring with `dawos top`
- :material-account-multiple: **Multi-Profile** — Manage multiple BNG nodes from one CLI
- :material-code-json: **Automation Ready** — `--json` and `--format csv|yaml` output for scripting
- :material-console: **Interactive Shell** — `dawos shell` REPL with tab completion
- :material-stethoscope: **Self-Diagnostics** — `dawos doctor` checks environment, connectivity, config
- :material-update: **Self-Updating** — Built-in update notifications and `dawos update`
- :material-shield-check: **Secure** — API key authentication with profile export/import

### Quick Example

```bash
# Add your BNG node
dawos profile add prod --url http://192.168.1.1:8470 --key YOUR_API_KEY

# Check status
dawos status

# View active sessions
dawos session list

# Live dashboard
dawos top
```

## Requirements

- Python 3.9+
- A running [dawos-agent](https://github.com/Cepat-Kilat-Teknologi/dawos-agent) instance

## Install

```bash
pip install dawos-cli
```

See [Installation](getting-started/installation.md) for more options (pipx, Homebrew, installer script).

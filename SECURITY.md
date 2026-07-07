# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

The dawos-cli team takes security issues seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by emailing the project maintainers directly. You should receive a response within **48 hours** acknowledging your report.

### What to Include

When reporting a vulnerability, please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)
5. **Your contact information** for follow-up questions

### Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix development | Depends on severity |
| Public disclosure | After fix is released |

### Severity Classification

| Severity | Description | Response |
|----------|-------------|----------|
| **Critical** | Remote code execution, credential exposure | Immediate patch release |
| **High** | Authentication bypass, data leakage | Patch within 7 days |
| **Medium** | Denial of service, information disclosure | Patch in next release |
| **Low** | Minor issues with limited impact | Addressed in future release |

## Security Best Practices

When using dawos-cli in production:

### API Key Management

- **Never** commit API keys to version control.
- Store API keys in environment variables or secure vaults when possible.
- Use unique API keys per BNG node.
- Rotate API keys periodically.

### Profile Security

- The profile configuration file (`~/.config/dawos/config.json`) contains API keys in plain text. Ensure appropriate file permissions:
  ```bash
  chmod 600 ~/.config/dawos/config.json
  ```
- On shared systems, set `DAWOS_CONFIG_DIR` to a user-specific directory with restricted permissions.

### Network Security

- Always use dawos-cli over trusted networks or VPN connections.
- Consider placing dawos-agent behind a reverse proxy with TLS termination.
- Restrict dawos-agent access to authorized IP addresses.

### Operational Security

- Use `--verbose` mode sparingly in production — it may expose sensitive information in logs.
- Avoid using `--json` output with sensitive data in shared terminal sessions.
- Review the `dawos diagnostics doctor` output regularly to ensure proper security configuration.

## Known Security Considerations

1. **Plain-text API keys**: Profile configuration stores API keys without encryption. This is by design for CLI simplicity but requires proper file permissions.

2. **HTTP transport**: dawos-cli communicates with dawos-agent over HTTP by default. For production deployments, use HTTPS via a reverse proxy.

3. **No certificate pinning**: The client does not implement certificate pinning. Use network-level controls for secure communication.

## Acknowledgments

We thank all security researchers who help improve the security of dawos-cli. Contributors will be acknowledged (with permission) in release notes.

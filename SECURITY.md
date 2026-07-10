# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes |
| 0.2.x   | Security fixes only |

## Reporting a Vulnerability

The DawOS CLI team takes security issues seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by emailing **security@cepat-kilat.id**. You should receive a response within **48 hours** acknowledging your report.

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

When using DawOS CLI in production:

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

- Always use DawOS CLI over trusted networks or VPN connections.
- Consider placing DawOS Agent behind a reverse proxy with TLS termination.
- Restrict DawOS Agent access to authorized IP addresses.

### Operational Security

- Use `--verbose` mode sparingly in production — it may expose sensitive information in logs.
- Avoid using `--json` output with sensitive data in shared terminal sessions.
- Review the `dawos doctor` output regularly to ensure proper security configuration.

## Known Security Considerations

1. **Plain-text API keys**: Profile configuration stores API keys without encryption. This is by design for CLI simplicity but requires proper file permissions. The CLI now warns on `profile export` that the output contains plaintext keys and sets `0600` permissions on export files automatically.

2. **HTTP transport**: DawOS CLI communicates with DawOS Agent over HTTP by default. For production deployments, use HTTPS via a reverse proxy.

3. **No certificate pinning**: The client does not implement certificate pinning. Use network-level controls for secure communication.

4. **Config file permissions**: The CLI checks config file permissions on load and warns if the file is group- or world-readable. The `_save()` function sets `0600` permissions automatically on write.

5. **Error sanitization**: Shell REPL and wizard engine sanitize catch-all exception output to prevent leaking internal paths or stack traces. Only safe exception types (`ValueError`, `TypeError`, `KeyError`) show their raw messages; all others display a generic failure message.

6. **Import validation**: Profile import validates each profile dict for required `url` and `api_key` keys before persisting. Malformed entries are skipped with log warnings.

## Acknowledgments

We thank all security researchers who help improve the security of DawOS CLI. Contributors will be acknowledged (with permission) in release notes.

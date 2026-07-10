# Security

See [SECURITY.md](https://github.com/Cepat-Kilat-Teknologi/dawos-cli/blob/main/SECURITY.md) for the full security policy.

## Quick Reference

- **Vulnerability reports**: Email security@cepat-kilat.id (not public issues)
- **Response time**: Acknowledgment within 48 hours
- **Supported versions**: 0.3.x (full support), 0.2.x (security fixes only)

## Security Features

| Feature | Implementation |
|---------|---------------|
| API key storage | Config file with `0600` permissions, permission warning on load |
| Profile export | Plaintext warning, `chmod 0600` on exported files |
| Profile import | Structure validation (rejects malformed profiles) |
| Error output | Sanitized — runtime errors hide internal paths and stack traces |
| Self-update | Pinned PyPI install (version-locked, no arbitrary git HEAD) |
| Node exec | Requires `--force` flag or interactive confirmation |
| HTTP transport | Warning on insecure (non-HTTPS) URLs |
| Config integrity | Atomic writes, corrupt JSON recovery |

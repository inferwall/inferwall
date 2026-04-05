# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

InferenceWall is a security tool — we take vulnerabilities in our own codebase seriously.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report vulnerabilities through one of these channels:

1. **GitHub Security Advisory**: [Report a vulnerability](https://github.com/inferwall/inferwall/security/advisories/new) (preferred)
2. **Email**: security@inferwall.dev

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to expect

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 7 days
- **Fix timeline**: within 30 days for critical issues, 90 days for others
- **Credit**: we will credit you in the release notes (unless you prefer anonymity)

### Scope

The following are in scope:

- Signature bypass (crafted input that evades detection)
- Authentication bypass in the API
- Scoring manipulation (forcing allow on known-malicious input)
- Denial of service via crafted payloads
- Dependencies with known CVEs

The following are out of scope:

- Detection gaps for novel attack techniques (file a feature request instead)
- Issues in third-party ML models (report to the model author)
- Social engineering attacks against project maintainers

## Security Best Practices for Deployments

- Always set `IW_API_KEY` and `IW_ADMIN_KEY` in production
- Run behind a reverse proxy with TLS
- Use the `strict` policy profile for high-security environments
- Keep InferenceWall updated (`pip install --upgrade inferwall`)
- Monitor flagged requests for emerging attack patterns

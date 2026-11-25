# Security Policy

## Supported Versions

Security fixes are released for the latest version only. Update to the newest release to receive them.

| Version | Supported          |
| ------- | ------------------ |
| Latest release | :white_check_mark: |
| Older releases | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project:

1. **Do not** create a public GitHub issue
2. Report via one of the following:
   - **Preferred:** [GitHub Security Advisories](https://github.com/itential/admin-skills/security/advisories/new) (report privately)
   - **Alternative:** security@itential.com
3. Include in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Affected versions
   - Impact assessment
   - Suggested fix (if any)

We will acknowledge your report within 48 hours and provide regular updates on our progress toward a fix. We follow coordinated disclosure practices.

## Security Best Practices

<!-- MAINTAINER: Update the sections below for your project's technology stack. Remove items that don't apply and add stack-specific guidance (e.g., SQL injection prevention for database projects, CSRF protection for web apps). -->

- **Credentials:** Never hardcode secrets, API keys, or passwords. Use environment variables or a secrets manager. Keep platform credentials in the `.env` of the folder you work in: the skills' auth helper reads it and caches a short-lived token in `.auth.json` and `.auth.curl`, so the agent never reads `.env` or sees your secret. A new service account's secret is written straight to a `.env` file by `save_service_account.py`, never shown. Never commit `.env`, `.auth.json` or `.auth.curl`. A model can still choose to print the short-lived token from `.auth.json` or `.auth.curl` (smaller models occasionally do, despite the skills telling them not to); if that matters in your environment, block reads of `.env` and `.auth.*` in your AI tool's permission settings.
- **Dependencies:** Keep dependencies up to date. Run security scans regularly and monitor advisories.
- **Input validation:** Validate and sanitize all external input at system boundaries.
- **Error handling:** Sanitize error messages before exposing them. Avoid logging sensitive data.
- **TLS:** Always use HTTPS in production environments.
- **Access control:** Follow the principle of least privilege for all credentials and permissions.

<!-- MAINTAINER: Add any project-specific security considerations below. Examples:
- Authentication/authorization requirements
- Data encryption standards
- Compliance requirements (SOC 2, GDPR, etc.)
- Security testing tools used in CI/CD
-->

## Automated Checks

Every pull request is checked for things the skill instructions and scripts must not do (a token in a URL, instructions to read `.env`, secrets in commands or on the command line, and others), unsafe GitHub Actions workflows (zizmor) and code vulnerabilities (CodeQL). GitHub secret scanning blocks committed keys, and OpenSSF Scorecard grades the repository weekly. Details: [CONTRIBUTING.md → Security checks](CONTRIBUTING.md#security-checks).

# Security Policy

## Supported Versions

The following versions of this project are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

---

## Reporting a Vulnerability

We take the security of this project seriously. If you identify a security vulnerability, please do not disclose it publicly in issues or pull requests.

### Disclosure Process

1. Report vulnerabilities by opening a private security advisory on GitHub or by contacting the repository maintainer directly.
2. Please include:
   - A detailed description of the vulnerability.
   - Steps to reproduce the issue or proof-of-concept payload.
   - Potential impact of the vulnerability.
3. The maintainers will acknowledge receipt within 48 hours and provide a timeline for remediation.

---

## Security Best Practices in this Repository

- **No Hardcoded Secrets**: Secrets and environment configurations are loaded via environment variables (`Config` class in `backend/config.py`).
- **Input Validation**: All 9 cytological parameters are validated against boundary conditions ($1.0 \le x \le 10.0$) before reaching model inference to prevent injection or numerical overflow.
- **Batch Rate Limiting**: Batch requests are capped at 500 records per call to prevent resource exhaustion and denial of service.

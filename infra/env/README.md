# Environment Management & Secrets Architecture

## Overview

The LEXIS platform enforces strict environment separation across three operational tiers:
1. **Local Development (`local`)**: Containerized or standalone developer instances running on developer workstations.
2. **Staging Environment (`staging`)**: Pre-release cloud deployment integrated with sandbox database clusters and test credentials.
3. **Production Environment (`production`)**: Hardened, TLS-enforced cloud deployment with automated secret injection.

---

## Directory Structure

```
infra/env/
├── README.md               # Environment architecture and security guidelines
├── local.env.example       # Template for local development
├── staging.env.example     # Template for staging deployment pipelines
└── production.env.example  # Template for production deployment pipelines
```

---

## Security Policies & Best Practices

1. **Zero Secret Commitment Policy**:
   - Never check actual secret values into git history under any circumstances.
   - All `.env` files except `.env.example` templates are strictly gitignored.

2. **Secret Lifecycle & Injection**:
   - **Local**: Developers copy `infra/env/local.env.example` to `.env` in the root folder.
   - **Staging / Production**: Environment variables are injected dynamically via secret management platforms (GitHub Encrypted Secrets, AWS Secrets Manager, or HashiCorp Vault) into container environments at runtime.

3. **Key Entropy & Length Requirements**:
   - `JWT_SECRET` and `JWT_REFRESH_SECRET` must be generated using cryptographically secure random sources (e.g. `openssl rand -hex 32`). Minimum requirement is 32 bytes (256-bits).
   - `ENCRYPTION_KEY` must be a 64-character hex string representing a 256-bit AES encryption key.

4. **Automated Validation**:
   - Application services run automated runtime startup checks via `backend/config/env.js`. If any required key is missing or fails security checks (such as insufficient JWT secret length in production), the application process terminates immediately with an error log.

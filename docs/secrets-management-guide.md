# LEXIS Secrets Management & Security Architecture Guide

## Executive Summary

The **Environment & Secrets Foundation** module establishes the core security boundary for the LEXIS Legal Intelligence Platform. It guarantees that credentials, API keys, private keys, and database connection strings never touch git history or public code repositories.

---

## Architecture Principles

1. **Defense in Depth**: Automated security validation happens at three layers:
   - **Local Workstation**: Pre-commit git hook blocks secret commits before reaching git history.
   - **Application Startup**: Fast-fail runtime environment validator (`backend/config/env.js`) aborts startup if keys are missing or cryptographically weak.
   - **CI/CD Pipeline**: GitHub Actions runs automated secret detection scans on every PR and push.
2. **Environment Separation**: Environment parameters are categorized by tier (`local`, `staging`, `production`) in `/infra/env/`.
3. **Least Privilege Secret Distribution**: Production secrets are injected dynamically into container runtime processes from secure secret vaults (GitHub Secrets / Vault).

---

## Local Development Quickstart

1. **Initialize Local Environment File**:
   Copy `.env.example` to `.env` in the root workspace directory:
   ```bash
   cp .env.example .env
   ```

2. **Activate Pre-Commit Security Hook**:
   Run the cross-platform setup script to configure local git hooks:
   ```bash
   node scripts/install-hooks.js
   ```

3. **Verify Environment Configuration**:
   Test the environment validator to ensure your `.env` settings meet all security requirements:
   ```bash
   node backend/config/env.js
   ```

---

## Pre-Commit Secret Scanner

The pre-commit scanner (`.githooks/pre-commit`) inspects staged git commits for high-risk pattern signatures:

| Signature Category | Pattern Detected | Risk Mitigated |
|---|---|---|
| **OpenAI API Key** | `sk-[a-zA-Z0-9]{20,}` | Exposing high-cost AI LLM quota keys |
| **AWS Access Key ID** | `AKIA[0-9A-Z]{16}` | Cloud infrastructure compromise |
| **GitHub Access Token** | `ghp_...` / `github_pat_...` | Unauthorized repo write access |
| **Google Cloud Key** | `AIzaSy[a-zA-Z0-9_-]{33}` | API bill abuse |
| **Private Keys** | `-----BEGIN * PRIVATE KEY-----` | TLS/SSL & RSA private key leak |

---

## Key Generation Standard

When setting up `staging` or `production` environments:

- **JWT Secrets (`JWT_SECRET`, `JWT_REFRESH_SECRET`)**:
  Generate 32+ byte random hex string:
  ```bash
  openssl rand -hex 32
  ```

- **Encryption Keys (`ENCRYPTION_KEY`)**:
  Generate 256-bit AES encryption key:
  ```bash
  openssl rand -hex 32
  ```

---

## Incident Response Plan: Credentials Leaked

If an API key or secret is accidentally exposed:
1. **Revoke Immediately**: Deactivate the key in the provider console (OpenAI, AWS, Sarvam, SMS Provider).
2. **Rotate Credentials**: Generate a new key and update the secret store (GitHub Secrets / Vault).
3. **Purge Git History**: Use `git-filter-repo` or BFG Repo-Cleaner if a secret was committed to remote git history.
4. **Audit Logs**: Review cloud audit trails for unauthorized access during the exposure window.

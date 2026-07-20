# LEXIS — Week 1 Development Plan (Track A: Platform, Auth & Security)

**Sprint goal:** Every route any track builds from Week 2 onward should automatically inherit hashing/auth, rate limiting, security headers, and a clean secrets setup — so the team never has to retrofit security later.

**Runs in parallel with:** Module 0 (Project Foundation & DevOps) and Module 1 (Authentication & User Management), owned jointly with the rest of Track A.

**Owner:** Track A (dedicated security member) + Track A DevOps half for Module 0 items.

---

## Pre-requisites before Day 1

- [ ] Repo scaffolded (`/frontend`, `/backend`, `/agents`, `/infra`, `/docs`) — confirm with whoever owns Module 0
- [ ] Access to GitHub repo with admin rights (needed for branch protection + CI secrets)
- [ ] Node.js + Python environments confirmed working locally
- [ ] Docker + Docker Compose installed locally

---

## Day 1 (Mon) — Environment & Secrets Foundation

**Objective:** No secret ever touches git history; every environment is cleanly separated from day one.

| Task | Detail | Output |
|---|---|---|
| `.env.example` file | List every env var the stack will need: `JWT_SECRET`, `JWT_REFRESH_SECRET`, `MONGO_URI`, `REDIS_URL`, `QDRANT_URL`, `OPENAI_API_KEY`, `SARVAM_API_KEY`, `SMS_PROVIDER_KEY`, `NODE_ENV` | `.env.example` committed, real `.env` gitignored |
| Environment separation | Create `local`, `staging`, `production` env configs (even if staging/prod are placeholders for now) | `/infra/env/` folder with 3 template files |
| `.gitignore` audit | Confirm `.env`, `node_modules`, `__pycache__`, `*.pem`, `/uploads` (future) all excluded | Updated `.gitignore` |
| Pre-commit secret scan | Install `git-secrets` or a simple regex pre-commit hook that blocks commits containing key-like strings (`sk-`, `AKIA`, etc.) | Working pre-commit hook, tested with a dummy fake key |
| CI secrets setup | Add placeholder secrets to GitHub Actions repo secrets (don't need real values yet, just the pipeline wiring) | CI can reference `${{ secrets.X }}` without failing |

**End of day check:** clone the repo fresh, confirm no real secret exists anywhere in git history (`git log -p | grep -i api_key` should return nothing).

---

## Day 2 (Tue) — Password Auth Core

**Objective:** Signup/login works end-to-end with properly hashed credentials.

| Task | Detail | Output |
|---|---|---|
| User schema | Fields: `id, name, phone, email, passwordHash, language_pref, created_at, is_anonymous, last_login, mfa_enabled` | Mongoose/Joi schema committed |
| Signup endpoint | `POST /auth/signup` — bcrypt hash (cost factor ≥12), validate email/phone format, reject weak passwords (min length + complexity check) | Working endpoint, tested via Postman |
| Login endpoint | `POST /auth/login` — verify hash, never log password even on failure | Working endpoint |
| Password policy | Document minimum requirements (length, no common-password list check via a small local dictionary) | Short policy doc in `/docs` |

**End of day check:** signup a test user, confirm `passwordHash` in DB is a bcrypt string, confirm plaintext password never appears in any log line.

---

## Day 3 (Wed) — OTP Login & Rate Limiting

**Objective:** Phone-based OTP login works and is protected against brute force from day one — not retrofitted later.

| Task | Detail | Output |
|---|---|---|
| OTP request endpoint | `POST /auth/otp/request` — integrate SMS provider trial tier (MSG91/Twilio), generate 6-digit OTP, 5-minute expiry, no reuse after verification | Working endpoint |
| OTP verify endpoint | `POST /auth/otp/verify` — match against stored (hashed) OTP, single-use enforcement | Working endpoint |
| Rate limiting middleware | Apply to **all** auth endpoints: 5 attempts / 15 min per IP+account combo (use `express-rate-limit` + Redis store so it survives restarts) | Middleware applied to `/auth/*` |
| Brute-force test | Script that hits `/auth/login` and `/auth/otp/request` repeatedly, confirm 429 responses trigger correctly | Test script + passing result logged |

**End of day check:** run the brute-force test script against staging/local — 6th attempt within 15 minutes must return 429, not 200/401.

---

## Day 4 (Thu) — Tokens, Sessions & RBAC Scaffold

**Objective:** JWT issuance, refresh rotation, and role scaffolding are in place before any protected route is built by other tracks.

| Task | Detail | Output |
|---|---|---|
| JWT access token | 15-minute expiry, signed with `JWT_SECRET`, includes `userId`, `role` | Token issuance on login/OTP success |
| Refresh token | httpOnly, Secure, SameSite=Strict cookie, 7-day expiry, rotated on every use (old token invalidated) | `POST /auth/refresh` endpoint |
| Logout & invalidation | `POST /auth/logout` clears refresh cookie + invalidates server-side session record; force logout on password change | Working endpoint |
| RBAC scaffold | `citizen` role active now; `lawyer` / `admin` roles defined in schema but explicitly deny-by-default (no routes should trust them yet) | Role check middleware, unit tested |
| Auth middleware | Reusable Express middleware (`requireAuth`, `requireRole`) other tracks will import for protected routes | Middleware exported from `/backend/middleware/auth.js` |

**End of day check:** confirm a tampered/expired JWT is rejected with 401, and that refresh-token replay (reusing an already-rotated token) is detected and blocked.

---

## Day 5 (Fri) — Security Headers, CORS & API Hardening Baseline

**Objective:** Every API response — regardless of which track built the route — carries baseline security protections.

| Task | Detail | Output |
|---|---|---|
| helmet.js | Apply globally in Express app entrypoint (before any route registration) | Security headers visible in response (check via curl -I) |
| CORS policy | Lock to known frontend origins only (`localhost:3000` for now, staging/prod domains as placeholders) | CORS config committed |
| Global rate limiter | Baseline per-IP limiter on *all* routes (separate, looser than the auth-specific one from Day 3) | Applied in app entrypoint |
| Request validation baseline | Add Zod/Joi validation wrapper utility that other tracks can use for their own endpoints going forward | `/backend/utils/validate.js` + example usage doc |
| Password reset flow | `POST /auth/password/reset-request` + `POST /auth/password/reset-confirm` — expiring token via email link | Working endpoints |

**End of day check:** hit any API route without proper headers/origin from a disallowed domain — confirm CORS blocks it; confirm helmet headers (`X-Content-Type-Options`, `X-Frame-Options`, etc.) appear on every response.

---

## Weekend Buffer / Day 6 (optional, if needed) — Integration & Handoff

**Objective:** Package Week 1's work so Tracks B, C, and D can build on it Monday without friction.

| Task | Detail | Output |
|---|---|---|
| Postman collection | Full collection covering signup, login, OTP, refresh, logout, password reset | Shared in repo `/docs/postman/` |
| Auth integration guide | One-page doc: "how to protect a new route" — import `requireAuth`, check `req.user.role`, example snippet | `/docs/auth-integration.md` |
| Demo to team | 15-min walkthrough with Tracks B/C/D — signup → login → protected route → logout cycle live | Team sign-off that they can build against it |
| Update issue tracker | Mark Module 1 security-related sub-tasks as done, log any deferred items (e.g., MFA toggle, full RBAC beyond scaffold) | Updated GitHub Projects / Jira board |

---

## Week 1 Definition of Done

- [ ] Any team member can `git clone` → `docker compose up` and get a working environment in under 10 minutes, with zero real secrets in the repo
- [ ] Signup → Login → Protected route → Logout cycle works end-to-end, testable via the shared Postman collection
- [ ] Brute-force script confirms rate limiting trips correctly on auth endpoints
- [ ] helmet.js + CORS confirmed active on every API response
- [ ] Auth middleware (`requireAuth`, `requireRole`) is documented and ready for Tracks B/C/D to import starting Week 2
- [ ] No secret exists in git history; pre-commit hook blocks future leaks
- [ ] RBAC scaffold in place (citizen active, lawyer/admin stubbed deny-by-default)

## Explicitly Out of Scope for Week 1 (deferred to later weeks)

- Prompt-injection filtering (Week 2, depends on Track B's Input Layer)
- File upload validation / malware scanning (Week 2)
- Vault encryption (Week 4, joint with Track C)
- MFA beyond the `mfa_enabled` schema field (post-MVP / stretch goal)
- Full lawyer/admin permission logic (future scope per original synopsis)

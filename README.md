# Sentinel Claims

A planned PhilHealth claim review workspace for hospital reviewers: compare prepared claims with supporting records, coordinate corrections, and document review before submission through the hospital's existing system.

**Current status:** Implementation is underway. Named accounts, local MFA, assigned case access and offline inference guards are implemented. The full review interface and correction workflow remain unfinished. Hosted deployment and operational hospital use require additional verification.

Start with the [product summary](PRODUCT.md), [experience guide](DESIGN.md), and [build checklist](BUILD-CHECKLIST.md). Contributors should read the [session handoff](HANDOFF.md) before making changes.

## Planned workflow

Import a versioned bundle ? inspect coverage and source-linked findings ? request a source correction ? import the revised bundle ? recheck ? export the named reviewer's record.

Initial scope is adult general medical inpatient claims before initial submission. Submission automation, clinical/coding decisions and reimbursement guarantees are excluded.

## Local development

Install the locked environment and provision named accounts from a private terminal:

```powershell
uv sync --project apps/api --locked
uv run --project apps/api --locked python -m sentinel account-create reviewer --roles reviewer
uv run --project apps/api --locked python -m sentinel account-create supervisor --roles supervisor
uv run --project apps/api --locked python -m sentinel serve
```

Open `http://127.0.0.1:8000/login`. Password prompts do not echo. Supervisor/admin provisioning displays a fresh secret for a local TOTP authenticator and requires its code before saving. No shared or default password exists. Supervisor assignment can claim historical unassigned cases; administrator status alone cannot view records.

`account-disable USER`, `account-enable USER`, `account-revoke USER` and `account-reset USER` run through the same CLI. Resetting a privileged account reenrolls MFA; all these commands revoke existing sessions. Treat terminal access as operator authority. Restrict the data directory to the operator using local filesystem permissions, including Windows ACLs. Keep `data/account.key` private and backed up separately from database exports: it encrypts the stored MFA secrets. A missing or wrong key fails authentication closed.

Sessions expire after eight hours or twenty idle minutes. HTTP on loopback uses HttpOnly/SameSite cookies; HTTPS requires `SECURE_COOKIES=true`. Production requires HTTPS/secure cookies and PostgreSQL. Remote inference remains disabled unless `NETWORK_MODE=online` is explicitly selected. SQLite is a development path; container/PostgreSQL verification is pending.

The old shared token works only with explicit `AUTH_MODE=legacy` in development and a configured token of at least 24 characters. This migration mode has no named accountability; use named mode for the new workflow. The full evidence workbench is still under construction.

Versioned imports are available through the authenticated API: create a case with facility, encounter, claim and patient anchors at `POST /api/cases`, then upload files plus a typed SHA-256 manifest and expected revision at `/api/claims/{id}/bundles` with an `Idempotency-Key`. Get immutable membership and current extraction coverage at `/api/claims/{id}/bundles/{version}`; authorized original downloads use `/api/documents/{id}/content`. Original objects are encrypted beneath `SOURCE_STORAGE_ROOT` and require the local key. These import APIs do not yet establish complete review or finalization.

## Repository layout

| Path | Owns |
|---|---|
| `apps/api/` | FastAPI app (`src/sentinel`, including the current static UI), Alembic `migrations/`, Python manifests and `uv.lock`, backend `tests/`, API-only `scripts/`, `Dockerfile` |
| `apps/web/` | Reserved for the Next.js frontend; created with it |
| `tests/e2e/` | Real-browser acceptance across the running app |
| `tests/fixtures/` | The single copy of shared synthetic evidence and locked manifests |
| `scripts/` | Cross-app commands: `verify.ps1`, `local.ps1` |
| `compose.yaml` | Local multi-service entry point |
| `docs/`, `prompts/` | Canonical documents and change records; reusable prompts |
| `data/` | Ignored private runtime state; start from the repository root or `apps/api/` and the same directory is used |

Run lint, the API tests and the browser acceptance suite with `./scripts/verify.ps1`. The placement policy is [.cursor/rules/repository-structure.mdc](.cursor/rules/repository-structure.mdc).

## Project context

This repository also holds the Best Apps & Agents track research for the Nebius x NVIDIA Global AI Hackathon. Hospital workflow readiness takes priority over prize-specific features.

| Document | Purpose |
|---|---|
| [Product decisions](PILOT-DECISIONS.md) | Accepted decisions and their rationale |
| [Workflow research](PILOT-WORKFLOW-RESEARCH.md) | Hospital process evidence and its limits |
| [Event reference](HACKATHON.md) | Recorded rules and dates; recheck official rules before submission |
| [Sponsor context](ORG.md) | Original sponsor background |
| [Research prompt](PROMPT.md) | Original research request |
| [Opportunity research](Hackathon-AI-Agent-Research.md) | Historical proposals, not the current product specification |

The earlier nightly headless auditor, market estimates and revenue positioning are historical hypotheses. They do not establish capability, customer demand or measured outcomes.

Local offline setup, account provisioning, encrypted checkpoints and isolated restore: [LOCAL-SETUP.md](LOCAL-SETUP.md). Container/PostgreSQL acceptance remains pending on a host with a working engine; SQLite verification is developmental.

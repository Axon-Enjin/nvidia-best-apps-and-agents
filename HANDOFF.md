# Sentinel Claims: session handoff

Last updated: **2026-10-22**.

## Current instruction and branch

Implementation remains authorized. The owner requested Tasks 4 through 10. Work stays inline on **feat/offline-prototype** in the existing linked worktree. The earlier owner pause is superseded. Commit only in this project; never commit or push to the external FMD repository. No push, public deployment, cloud purchase or real-patient-data processing is authorized.

## Read next

1. Root AGENTS.md and docs/state.md.
2. docs/changes/offline-prototype/tasks.md and verify.md, which own progress and evidence.
3. The active delta spec/design, PRD P01-P10 and SDD; DSD/QAD for UI and evaluation.
4. LOCAL-SETUP.md for launch, provisioning, backup and isolated restore; OCR-NOTICES.md for pinned local OCR.
5. docs/changes/repository-organization/ and .cursor/rules/repository-structure.mdc for where files live.
6. docs/changes/frontend-redesign/ for the Next.js review workspace: design, tasks, verification and the visual review.

## Repository layout

The API is `apps/api/` (package `src/sentinel`, `migrations/`, `tests/`, `pyproject.toml`, `uv.lock`, `Dockerfile`). Browser acceptance is `tests/e2e/`; shared synthetic evidence is `tests/fixtures/`. `apps/web/` is the Next.js review workspace (pnpm, `pnpm-lock.yaml`); it reaches FastAPI through its same-origin `/api` proxy. Run `./scripts/verify.ps1` from the repository root for lint, API tests and browser acceptance. Relative `data/` settings resolve against the repository root, so the private `data/` directory is the same from any working directory. Older change records keep the paths that were true when they were written.

## Implemented and verified locally

Tasks 1-8: offline provider guards; named local accounts and privileged TOTP; immutable encrypted bundle originals; content-derived P01-P10 checks; real queue/import/source workspace; append-only correction/manual events and revision fencing; guarded immutable reports and safe CSV/print; actual printed PNG/PDF OCR with separate source confirmations.

Task 9 adds encrypted checkpoints, isolated SQLite restore, source hash/history/authorization checks, revoked restored sessions, interrupted-job reconciliation, bounded worker retries and authenticated retirement tombstones. Docker/Compose/CI artifacts are prepared. Physical retention deletion and scheduled backups are not implemented.

Task 10 adds 40 independent labelled evaluation cases (20 discrepancies, 10 clean, 10 incomplete/adversarial), 20 corrected pairs and printed equivalents. The real browser completes import, discrepancy evidence, correction handoff/acknowledgement, corrected import, recheck, manual P07/P08, a different supervisor acknowledgement, finalization, CSV/print and a real process restart/reopen. A second reviewer is denied case/source/report access. Browser external origins and Python server non-loopback sockets are independently blocked during this test.

The active verification record holds exact test counts, measured environment, screenshots and rulings. A small SQLite metadata exercise uses 10,000 rows and five concurrent named readers; it does not establish production capacity or hospital benefit.

## Frontend redesign (2026-10-22)

The review workspace is now the Next.js app in `apps/web`: sign-in, a URL-driven claims queue, one intake for new claims, and three case phases (Import, Review, Complete) that open where action is needed. Review shows each issue beside its exact source values with lettered evidence marks, one primary next action, correction progress as separate events, manual reviews and a different supervisor's acknowledgement. Drafts survive expired sessions and stale revisions. FastAPI gained `TRUSTED_ORIGINS` and an additive `differences` field on checks; no rule, status or schema changed. The static UI still runs at port 8000 until the owner accepts the new frontend, then task 5.4 retires it. Start both servers as described in LOCAL-SETUP.md (web app on port 3000).

## Open first-prototype gates

There is no available Docker engine, WSL, Podman or PostgreSQL runtime on this host. Official Compose 5.6.1 standalone configuration validation passes, but image build/start, actual PostgreSQL correction/restore, Linux container OCR and container/OS egress acceptance remain unrun. The PostgreSQL integration test explicitly skips without TEST_DATABASE_URL. CI is defined but has not executed; no L1 claim is made. Tasks 9.4 and 10.3/10.4 remain unchecked; overall change verification stays FAIL. Do not archive or claim full prototype sign-off.

Next: obtain a working container runtime, run the standard setup and PostgreSQL restore drill, execute CI when publishing is authorized, then repeat acceptance with OS/container network isolation. No product-scope reapproval is needed.

## Boundaries

Synthetic patients only. Adult general medical inpatient ACR after discharge and before initial submission; the existing hospital system keeps submission authority. No official eClaims compatibility, autonomous clinical/coding decision, signature authenticity, hospital endorsement or payment guarantee is claimed.

P07 may resolve through named source-backed manual comparison and a different supervisor acknowledgement; AI remains not run offline. P08 requires actual marks, printed names and dates, not explicit absence. P09 permits only reasoned supervisor withdrawal of a mistakenly expected extra attachment. No core-artifact waiver exists. Source/rule changes reopen manual review; missing original objects block closeout; later revisions mark reports stale.

## External documentation engine and local material

Read-only engine: C:/Users/Yushin/tools/fmd-v3.0.1, source https://github.com/delatorrecj/fmd.git, tag v3.0.1, commit 4979fda6435dc007a331c40a5e9e28db813eebb2. Read its AGENTS.md and trigger matrix before docs work, use PYTHONDONTWRITEBYTECODE=1, and run its scripts against project docs. Never copy engine files here or commit/push to the engine repository.

Preserve unrelated untracked output/, docs/sentinel-node-claims-interoperability-research.md, docs/sentinel-node-walkthrough.html and docs/superpowers/. Full-workspace FMD checks still see the unchanged research voice/old-plan manifest findings; strict checks of the tracked artifact snapshot are separate. The plan ledger is ignored scratch under .superpowers/sdd/tasks/ while runtime gates remain open.

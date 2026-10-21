# Offline Prototype Implementation Plan

> **For agentic workers:** Execute task by task with the executing-plans skill and test-driven-development. Work inline by default. This plan is stored in the existing FMD change folder so one task list owns progress.

**Goal:** A fully working local review-and-correction prototype that operates with internet access disabled after installation.

**Architecture:** Retain FastAPI, SQLAlchemy and a durable worker; serve all assets locally. Use PostgreSQL for standard local/container operation and private local source storage. Keep SQLite as the existing lightweight development path. Remote inference is optional and explicitly disabled offline; manual narrative review retains named human accountability.

**Tech Stack:** Python, FastAPI, SQLAlchemy/Alembic, PostgreSQL, plain browser JavaScript/CSS, pytest and Playwright. Exact resolved versions live in `uv.lock`; the current build guide records tested versions.

**Spec:** [Offline requirements](specs/offline-review/spec.md), [PRD](../../prd-sentinel-node.md), [SDD](../../sdd-sentinel-node.md) and [QAD](../../qad-sentinel-node.md).

## Global Constraints

- Synthetic patient records only; one environment notice and export provenance.
- Adult general medical inpatient ACR, after discharge and before initial submission.
- Preserve P01-P10; only the documented supervisor withdrawal of a mistakenly expected extra attachment is permitted.
- Limits: 25 MB/file, 100 MB/bundle version, 150 pages/version, 30 files/version; never silently truncate.
- Use locally served assets; no CDN, cloud account, inference credential or email service required for the core workflow.
- Named reviewer/supervisor/admin roles; privileged MFA; admin alone cannot review clinical records.
- No automatic source changes, payer submission, clinical/coding decisions or reimbursement promises.
- No engine changes or commits/pushes to FMD. All work stays in the current project repository.

## Review Focus

1. A provider key left in an environment must not activate networking; Task 1 tests API, worker and adapter boundaries.
2. A copied name must not associate the wrong encounter; Task 3/4 test conflicting identifiers and unmatched documents.
3. Revising a completed case while another tab saves must not preserve a stale ready state; Task 6/7 test concurrent stale writes and finalization.
4. Turning off AI or failing OCR must not silently waive required review; Task 4/6/8 test manual acknowledgement, abstention and core-document blockers.
5. Restoring a backup must not sever evidence or resurrect expired access; Task 9/10 verify source hashes, account state and the deletion ledger.

## File responsibilities

Extend `sentinel/config.py`, `api.py`, `db.py`, `documents.py`, `audit.py`, `worker.py` and `samples.py` where their existing responsibility fits. Add focused `accounts.py`, `storage.py`, `bundles.py`, `review.py`, `reports.py` modules only for the new responsibilities described below. Create additive Alembic migrations; preserve original source/result history. Finish `sentinel/static/app.css` and `app.js` against the existing HTML shell and accepted design. Add fixtures under `tests/fixtures/` and keep held-out evaluation data separate from development examples.

## Task 1: Reproducible runtime and enforced offline inference

**Files:** `pyproject.toml`, `.env.example`, `sentinel/config.py`, `api.py`, `worker.py`, `inference.py`; test `tests/test_offline.py`.
**Interfaces:** Consumes existing `Settings` and `create_app(settings, database)`; produces `Settings.network_mode: str`, default `offline`, accepted values `offline|online`; `/api/config` returns the mode and usable model availability.

- [x] 1.1 Reproduce the unsatisfiable `httpx2>=0.22,<1` dependency and retain the valid lockfile-compatible dependency set. Run `uv sync --locked`; successful without rewriting the lock.
- [x] 1.2 Write and run `tests/test_offline.py`: default offline, invalid-mode rejection, explicit online opt-in, credentials cannot enable offline uploads, direct adapter makes zero requests, queued AI job preserves local results and reports `not_run_offline`. Six failures observed before implementation.
- [x] 1.3 Implement mode guards in configuration, API, worker and provider adapter. Local results remain honest; manual closeout is not implemented yet.
- [x] 1.4 Run `uv run --locked pytest -q`, then `uv run --offline --locked pytest -q`. Baseline 31 passed; final suite 37 passed, one deprecation warning.
- [x] 1.5 Commit `08b0c09`, `fix: restore reproducible setup and enforce offline inference`. Verification is in `verify.md`.

## Task 2: Local named accounts, roles and assignment

**Files:** create `sentinel/accounts.py`, additive account/session migration, `tests/test_accounts.py`; modify `api.py`, `db.py`, CLI and login UI.
**Interfaces:** Produce `require_actor(request) -> Actor`, `require_case_access(actor, case) -> None` and `create_local_account(username, password, roles) -> account_id`. `Actor` has immutable ID, role set and enabled state. Every child-resource route resolves its case before authorization.

- [x] 2.1 Verified OWASP, argon2-cffi, Fernet, RFC 6238 and FastAPI primary guidance. Observed missing account tests and old-token bypass failing before implementation; added credential-reflection regression RED to GREEN.
- [x] 2.2 Implemented CLI provisioning/recovery, salted Argon2id passwords, encrypted TOTP secrets, replay protection and revocable sessions. Shared-token mode requires explicit development migration configuration.
- [x] 2.3 Actor/assignment checks cover queue, aggregates, case history, rerun, findings, job, source and report routes. CSRF and safe local/HTTPS cookies are enforced. Admin alone cannot review.
- [x] 2.4 Account tests and full suite pass; Chromium desktop/mobile sign-in verified. Commit `feat: add local accounts and assigned case access`; evidence in `verify.md`.

## Task 3: Versioned bundles and private local originals

**Files:** create `sentinel/bundles.py`, `storage.py`, bundle/document migration and `tests/test_bundles.py`; extend `db.py`, `api.py`, `documents.py`.
**Interfaces:** Produce `import_bundle(actor, case_id, files, manifest, expected_revision, idempotency_key) -> BundleReceipt` and `read_source(actor, document_id) -> source bytes`. Receipt includes case ID, immutable version, import-job ID and coverage. Manifest carries document types, explicit facility/encounter/claim anchors and source hashes.

- [x] 3.1 Nine bundle scenarios failed before implementation. Added damaged-source and assignment-revision coverage; stale coverage and assignment behavior were observed failing before correction.
- [x] 3.2 Added bundle/document migration, write-once encrypted private objects, immutable manifests, staging receipts and durable quarantined import jobs. Legacy source/result records remain intact.
- [x] 3.3 Enforced byte/file/page bounds and content detection. Child parsers have time/memory caps; XML forbids DTDs/entities/external references. Per-file unsupported/unmatched/ambiguous/unreadable states stay visible.
- [x] 3.4 Eleven bundle scenarios pass; full suite and affected Ruff checks recorded in `verify.md`. Commit `feat: import immutable local claim bundles`.

## Task 4: Synthetic profile and deterministic coverage

**Files:** extend `samples.py`, `audit.py`, `documents.py`; add `tests/fixtures/development/`, `tests/test_profile.py`.
**Interfaces:** Produce `evaluate_profile(bundle, confirmed_extractions, rule_version) -> CheckRun`, with P01-P10 IDs, per-check status, blocking reasons and current-version evidence anchors. Financial calculations use Decimal.

- [x] 4.1 Write failing parameterized tests for every P01-P10 completion rule, PHP 0.01 tolerance, ambiguous extraction, missing core forms and the sole P09 supervisor exception.
- [x] 4.2 Add complete/discrepant/incomplete/corrected development bundles containing the seven required artifact types. Label internal eSOA schema as a sample contract, never official compatibility.
- [x] 4.3 Implement content-derived checks and source anchors. P07/P08 remain explicit manual obligations offline; unavailable automation does not pass them.
- [x] 4.4 Run `uv run --locked pytest tests/test_profile.py -q` and the full suite. Expected seeded issues and coverage statuses match fixture labels. Commit `feat: evaluate the bounded claim review profile`.

## Task 5: Working queue, import and evidence workbench

**Files:** finish `sentinel/static/index.html`, `app.css`, `app.js`; extend authorized API contracts; add `tests/browser/test_review_workspace.py`.
**Interfaces:** Consume authenticated queue/bundle/run/source contracts. Browser state retains explicit current version and revision; server remains authoritative. No remote scripts, fonts or viewers.

- [x] 5.1 Write browser scenarios for login, assigned queue/filtering, import/matching, coverage, finding selection and source anchors. Assert requested assets return 200 locally and no external origin is requested.
- [x] 5.2 Implement Sentinel Claims styling and keyboard-operable screens with empty/loading/error/success states. Show source beside finding and one sample-record environment notice.
- [x] 5.3 Exercise 1366x768, 375px, keyboard-only and 200% zoom. Run `uv run --locked pytest tests/browser/test_review_workspace.py -q`; expected source version matches selection and denied deep links stay denied. Commit `feat: complete the local evidence review workbench`.

## Task 6: Decisions, manual review, corrections and revisions

**Files:** create `sentinel/review.py`, event/task migration, `tests/test_corrections.py`; extend API/UI and worker recheck integration.
**Interfaces:** Produce `record_review(actor, case_id, expected_revision, action) -> ReviewState`. Actions include reasoned disposition, manual P07/P08 completion, supervisor acknowledgement and correction lifecycle events. Every action appends history and advances revision.

- [ ] 6.1 Write failing scenarios for true discrepancy, evidence-backed dismissal, responsible department/person, handoff/acknowledgement, corrected-source recheck, retained original history and stale concurrent edits.
- [ ] 6.2 Implement append-only events and optimistic concurrency. Source/rule changes invalidate affected decisions; conservatively reopen all when dependency is unknown.
- [ ] 6.3 Implement offline P07 manual comparison with named reviewer evidence plus separate supervisor acknowledgement. Do not change `not_run_offline` to an automated success.
- [ ] 6.4 Run `uv run --locked pytest tests/test_corrections.py -q` and the full suite. Expected old evidence/history survives restart and stale saves return conflict. Commit `feat: track corrections and revision-safe manual review`.

## Task 7: Guarded closeout, reports and event metrics

**Files:** create `sentinel/reports.py`, finalization migration, `tests/test_closeout.py`; extend API/UI.
**Interfaces:** Produce `finalize_review(actor, case_id, bundle_version, rule_version, expected_revision) -> ReportSnapshot` and `export_report(actor, report_id, format) -> bytes`. Allowed formats: CSV and printable HTML. All guards run in the same transaction as snapshot creation.

- [ ] 7.1 Write failing tests for each unresolved blocker, open correction, wrong role, stale version, concurrent replacement, CSV formula/XSS payload and wrong-version evidence.
- [ ] 7.2 Implement current-version P10 guards and snapshots with actor, source/rule versions, coverage and sample provenance. Revisions mark previous reports stale; no payer approval wording.
- [ ] 7.3 Derive queue/correction/completion metrics from stored events with explicit denominators. Verify counts against seeded histories.
- [ ] 7.4 Run `uv run --locked pytest tests/test_closeout.py -q` and the full suite. Commit `feat: finalize and export versioned review records`.

## Task 8: Local printed-scan OCR and confirmation

**Files:** extend `documents.py`, add `sentinel/ocr.py`, extraction-confirmation migration and `tests/test_local_ocr.py`; update UI.
**Interfaces:** Produce `extract_document(source, limits) -> ExtractionResult` and `confirm_extraction(actor, document_id, anchor, value, reason, expected_revision) -> confirmation_id`. Keep original, extracted and confirmed values separate.

- [ ] 8.1 Select/pin a locally available OCR engine and English data; verify license and installation instructions. Test actual printed scan fixtures, not an OCR mock presented as capability.
- [ ] 8.2 Implement bounded local OCR with page anchors and no network fallback. Critical IDs/dates/amounts require source confirmation before blocking checks use them.
- [ ] 8.3 Run `uv run --locked pytest tests/test_local_ocr.py -q`. Expected text/scan equivalents reach the same reviewed result, while handwriting, failed binaries and unreadable passages remain incomplete. Commit `feat: support locally verified printed scans`.

## Task 9: Local packaging, worker recovery and restore

**Files:** create `Dockerfile`, `compose.yaml`, startup/backup/restore scripts and `LOCAL-SETUP.md`; add `tests/test_recovery.py`; extend config/worker only as needed.
**Interfaces:** Consume published migrations, private storage root and durable jobs. Produce documented setup/start/stop/backup/restore commands that select no remote services by default. Packaging includes OCR assets and all browser resources.

- [ ] 9.1 Write failure tests for worker interruption, duplicate publication, stale lease, missing source, expired account and restored deletion ledger. Preserve conditional lease fencing.
- [ ] 9.2 Package web/worker plus local PostgreSQL and persistent private source volumes. Bind to loopback by default; LAN use requires deliberate configuration. Keep SQLite instructions explicitly developmental. Add `.github/workflows/ci.yml` for lint/tests and PostgreSQL integration; record its actual run before claiming L1 exists.
- [ ] 9.3 Provide coordinated database/source backups and isolated restore verification. Validate hashes, history, authorization and pending-job reconciliation, not only command exit codes.
- [ ] 9.4 Run `uv run --locked pytest tests/test_recovery.py -q` and `docker compose config`; then start the available container runtime and execute the full correction loop/restore drill. If Docker/PostgreSQL is unavailable, leave that verification unchecked. Commit `feat: package a recoverable offline workspace`.

## Task 10: Disconnected acceptance and first prototype sign-off

**Files:** add 40 held-out labelled bundles under `tests/fixtures/evaluation/`, `tests/browser/test_offline_acceptance.py`, and `tests/test_acceptance.py`; update this change's `verify.md` with actual results.
**Interfaces:** Consume the completed application with named local accounts and no provider credentials. Use a real local browser/server/database and block external requests while allowing loopback/local database traffic.

- [ ] 10.1 Lock 20 discrepancy, 10 clean and 10 incomplete/unsupported/adversarial evaluation bundles independent of development fixtures. Record hashes, expected findings and evidence locations.
- [ ] 10.2 Run import -> evidence -> correction handoff -> corrected import -> recheck -> manual review/supervisor acknowledgement -> final record -> CSV/print -> restart -> reopen. Include a second account and unauthorized access attempts.
- [ ] 10.3 Block external networking and inspect browser/server requests. Assert no hidden provider/CDN/identity/analytics traffic, no false finalization and no wrong-version evidence.
- [ ] 10.4 Run `uv run --offline --locked pytest -q` and the documented PostgreSQL/browser/restore commands. Expected all offline acceptance scenarios pass with real data persistence. Measure workload limits; do not label unrun hosted/AI/hospital studies complete.
- [ ] 10.5 Record known limits, actual test environment, screenshots and repeatable launch/restore instructions. Commit `test: verify the complete disconnected review workflow` only after evidence exists.

## First prototype completion bar

Tasks 1-10 are complete; every visible control has real behavior; a clean local setup can run the full disconnected correction loop; scans, roles, completion guards, history, reports and restore are verified. No mock AI result or automatically waived manual review is permitted. Hosted deployment, live-model quality targets and hospital validation remain separate later gates.

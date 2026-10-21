# Verify: Offline first working prototype

**Date:** 2026-10-21
**Overall:** FAIL

FAIL means the complete prototype is not finished. Tasks 1-2 are verified; Tasks 3-10 remain pending. Do not archive or report the entire change complete.

## Completeness

- PASS: existing scaffold preserved as `e8c0ace`; branch `feat/offline-prototype` created.
- PASS: invalid dependency reproduced, then corrected; `uv sync --locked` succeeds using the unchanged lockfile.
- PASS: six offline behavior tests observed failing before implementation, then passing after mode guards were added.
- PASS: Task 1 committed as `08b0c09`, `fix: restore reproducible setup and enforce offline inference`; new test file passes Ruff.
- PASS: `uv run --offline --locked pytest -q`: 37 passed, one Starlette/HTTPX deprecation warning.
- PASS: Task 2 named accounts, local privileged MFA, revocable sessions and assigned case authorization implemented and tested.
- FAIL: new bundle/profile workflow, evidence workbench, manual acknowledgement, correction tasks, closeout/reporting, local OCR and packaging/recovery remain unimplemented.

## Correctness

- PASS: default/explicit mode validation, offline import rejection despite credentials, direct adapter zero-request behavior, offline worker handling of already-queued remote work and explicit online transport behavior tested.
- PASS: queued remote work processed offline retains deterministic results and marks remote coverage `not_run_offline` with incomplete outcome.
- LIMIT: `uv --offline` is a package-manager setting; this test run is not a whole-machine network isolation test. Provider transport tests are controlled test doubles, not live AI calls.
- FAIL: the full disconnected browser correction loop and 40-bundle acceptance set have not been executed.

## Coherence

- PASS: offline is an intermediate local milestone; the approved hosted-evaluation and operational-hospital goals remain.
- PASS: no remote credentials, cloud purchase, real-record authorization or completed hospital integration is invented.
- OPEN: Docker was not found on the current command path. PostgreSQL/container verification must use an actual available runtime before Task 9 can complete.

## Review quality

- Security: named mode now denies anonymous/shared-token access. Legacy shared-token access requires explicit development-only configuration; it does not establish named accountability.
- Coverage: existing tests and new offline guard tests pass, but they do not exercise the pending Must-Have workflow.
- Context hygiene: document content remains untrusted; offline mode never substitutes canned model output.

## Findings

- WARNING: Starlette warns that HTTPX TestClient support is deprecated. The existing locked environment works; select a supported replacement deliberately rather than restoring an impossible package range.
- WARNING: missing browser CSS/JavaScript and single-XML/chart assumptions still prevent a fully working prototype.
- SUGGESTION: keep task commits small and update this record with actual test and runtime evidence.

## Decisions during execution

- Retain the valid existing lockfile and remove only the impossible development constraint. Cost if wrong: revisit the testing transport migration, without changing production behavior.
- Keep optional SQLite for direct development while leaving standard PostgreSQL packaging/testing pending. No database support or concurrency claim is inferred from SQLite tests.

## Task 2 evidence

- Primary guidance checked 2026-10-21: [OWASP passwords](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [sessions](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/howto.html), [Fernet](https://cryptography.io/en/latest/fernet/), [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238), [FastAPI cookies](https://fastapi.tiangolo.com/advanced/response-cookies/) and [Alembic SQLite](https://alembic.sqlalchemy.org/en/latest/batch.html).
- Runtime dependency choices: argon2-cffi 25.1.0 default Argon2id parameters; cryptography 50.0.2 Fernet. Exact transitive versions are in updated `uv.lock`. TOTP uses stdlib HMAC SHA-1, 30-second steps, six digits, one-step tolerance and atomic replay fencing; RFC vector verified.
- RED: old bearer token bypass observed; missing account module exposed 13 missing contracts. Later CLI/login checks failed before implementation. Native migration test exposed Alembic's unsupported SQLite constraint ALTER. Credential-reflection test failed before safe validation handling.
- GREEN: 20 account scenarios plus one real Chromium login test at 1366x768 and 375px passed. Coverage includes password salts/normalization, MFA expiry/replay/concurrent use, session expiry/idle/revocation/restart, disable/reset/enable CLI, migration preservation, assignment/IDOR, aggregate isolation, admin denial, CSRF without Origin, throttling, HTTPS cookies and local assets/no external browser request.
- Final Task 2 checks: `uv sync --locked` succeeded; `uv run --offline --locked pytest -q` returned **58 passed**, one Starlette/HTTPX warning; affected source/tests passed Ruff. FMD change validation returned zero failures/warnings; `git diff --check` passed.
- Session decisions: eight-hour absolute/twenty-minute idle limits, opaque random cookie with only its digest stored, per-session CSRF token, DB-backed five-attempt account and thirty-attempt client windows per five minutes. Provisioning and sensitive recovery remain local CLI operations.
- Ruling: default named mode never falls back to an anonymous or shared identity, including a fresh database. Historical cases remain unassigned until a supervisor assigns them. Explicit legacy mode requires development and a configured token of at least 24 characters. Cost if wrong: adjust the migration instructions, not the named authorization boundary.
- Migration deviation: SQLite's native nullable `ADD COLUMN ... REFERENCES` avoids table rebuilds and preserves historical records; PostgreSQL uses Alembic's normal column/constraint operations. Only SQLite execution is established here.
- Limit: login browser verification covers authentication only. The evidence workbench and complete offline browser correction loop remain pending. The Starlette/HTTPX deprecation warning remains visible.

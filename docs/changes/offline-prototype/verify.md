# Verify: Offline first working prototype

**Date:** 2026-10-21
**Overall:** FAIL

FAIL means the complete prototype is not finished. Tasks 1-7 are verified; Tasks 8-10 remain pending. Do not archive or report the entire change complete.

## Completeness

- PASS: existing scaffold preserved as `e8c0ace`; branch `feat/offline-prototype` created.
- PASS: invalid dependency reproduced, then corrected; `uv sync --locked` succeeds using the unchanged lockfile.
- PASS: six offline behavior tests observed failing before implementation, then passing after mode guards were added.
- PASS: Task 1 committed as `08b0c09`, `fix: restore reproducible setup and enforce offline inference`; new test file passes Ruff.
- PASS: `uv run --offline --locked pytest -q`: 37 passed, one Starlette/HTTPX deprecation warning.
- PASS: Task 2 named accounts, local privileged MFA, revocable sessions and assigned case authorization implemented and tested.
- PASS: Task 3 encrypted immutable local originals, versioned membership, idempotent/revision-fenced imports, bounded child parsing and protected source downloads implemented.
- FAIL: accepted profile checks, evidence workbench, manual acknowledgement, correction tasks, closeout/reporting, local OCR and packaging/recovery remain unimplemented.

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

## Task 3 evidence

- Primary guidance checked 2026-10-21: [Python subprocess isolation/timeouts](https://docs.python.org/3.14/library/subprocess.html), [pypdf text extraction and memory concerns](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) and [defusedxml security controls](https://github.com/tiran/defusedxml).
- RED: nine API scenarios returned missing case/bundle routes before implementation. Later a coverage test caught a stale quarantine status after parsing, and an assignment test caught failure to advance case revision.
- GREEN: eleven scenarios cover all seven artifact types, original-byte/hash preservation across revisions, encrypted objects, duplicate idempotency keys, manifest/source identity mismatch, ambiguous duplicate fields, concurrent imports, filenames, child-route assignment, XML entities, unsupported binary, blank scans, file/page bounds and source damage.
- Final checks: `uv run --offline --locked pytest -q --tb=short --durations=10` returned **69 passed**, one existing Starlette/HTTPX warning, in 50.85 seconds. The preceding green run reported an anomalous 2:25:15 elapsed time; it was not reproduced and is not performance evidence. The slowest test on rerun took 6.40 seconds. Affected source/tests passed Ruff; `git diff --check` and change validation passed. Strict FMD validation of the tracked document snapshot returned zero failures/warnings; unrelated local research stayed excluded from that snapshot.
- The database stores source hashes and opaque keys; originals use Fernet with the external local key and exclusive writes. Staging receipts survive interrupted object writes for later reconciliation; no orphan cleanup or restore claim is made yet.
- Parsers execute in child processes with a twelve-second timeout, 512 MB process cap and bounded text/pages/nodes. Actual child execution on this Windows host parsed the fixtures. Linux resource-limit code and PostgreSQL execution remain unverified until packaging.
- Ruling: retain the legacy multipart `POST /api/claims` contract and add JSON case creation at `POST /api/cases`. Versioned imports use the specified `/api/claims/{id}/bundles` path. Cost if wrong: add a JSON alias during API migration; source/version semantics stay the same.
- Ruling: preserve oversized aggregate-page versions in quarantine with `limits_exceeded` and explicit page counts; never truncate. They cannot establish complete coverage. Cost if wrong: tighten admission before version publication, retaining the quarantined originals.
- Assignment now advances revision, and import CAS checks both revision and assignment. Legacy rerun cannot replace a versioned case. Lease-fenced publication writes all extraction outcomes together; unsupported content receives no invented fields.
- Limit: the import job evaluates content/membership only. Full P01-P10 evaluation is Task 4; every new version remains incomplete until the remaining review workflow is implemented. OCR, end-to-end browser review and PostgreSQL/container/restore acceptance are pending.

## Task 4 evidence

- RED: 22 profile scenarios failed for the absent profile and development-bundle contract. GREEN: all 22 pass. Full suite: 91 passed with the existing Starlette warning.
- Seven-artifact complete/discrepant/incomplete/corrected bundles are saved under tests/fixtures/development. SampleESOA v1 is an internal synthetic contract, not official compatibility.
- Content checks cover adult scope, required source fields, identity, chronology/disposition, Decimal PHP 0.01 tolerance, unsupported finance and core-artifact non-waiver. All findings carry immutable bundle/document/hash/page anchors.
- P07/P08 remain manual obligations; P10 remains transactional closeout work. Supervisor-only P09 withdrawal is evaluated in the profile and will be authorized through stored events in Task 6.
- Ruling: isolate the accepted profile in profile.py, re-exported through audit.py, preserving legacy audit records/contracts. Cost if wrong: relocate the implementation without changing its interface.
- Primary references checked: [SQLAlchemy DML](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html), [Python Decimal](https://docs.python.org/3/library/decimal.html) and [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/).

## Task 5 evidence

- RED: real Chromium could not activate the absent import workflow. An initial exact login-label mismatch was corrected before observing the missing-behavior failure.
- GREEN: real manifest/seven-original upload, assigned queue/search, saved profile selection and version-correct source text pass at 1366x768, 375px and 200% CSS zoom. Controls are activated with Enter; focus/overflow, local asset HTTP 200, JavaScript errors and external browser requests are checked. Screenshots are in test-results/workbench-*.png (local, ignored). Full suite: 92 passed, existing Starlette warning.
- The desktop/mobile captures were inspected together. The UI inherits the accepted forest/paper design and local system fonts. Source downloads retain server assignment checks.
- Fixture bytes are marked binary in .gitattributes so checkout line-ending conversion cannot invalidate manifest hashes. A Task 4 trailing-blank-line diff-check finding was removed.
- Ruling: import accepts an explicit JSON manifest and its originals, exposing declared types before upload. Cost if wrong: add a guided manifest editor without changing storage or membership semantics.

## Task 6 evidence

- RED: five service scenarios failed for absent routes/service; a real browser scenario failed for absent review controls. GREEN: six service scenarios plus the browser correction-handoff/reload flow pass. Full suite: 99 passed, one existing warning, in 98.85 seconds.
- Tests establish attributed append-only history, department/person responsibility, handoff/acknowledgement, corrected-version recheck, old-source preservation, concurrency conflicts, wrong-version evidence rejection and restart persistence.
- P07 requires current source-backed comparison and a different supervisor actor. Automated status remains not_run_offline. P08 verifies source marks/printed names/dates before accepting manual presence review. Source/rule changes and explicit reruns reopen manual review.
- Extra expectations persist; only a supervisor can withdraw one with a reason. No core-artifact waiver exists. Legacy mutable decision writes are denied for versioned bundles.
- Ruling: correction tasks and extra expectations are projections of append-only events rather than separate mutable task rows. Cost if wrong: add cached projections while retaining events as authority.

## Task 7 evidence

- RED: six scenarios failed for absent closeout/report contracts and an unguarded legacy report route. GREEN: seven closeout scenarios pass, including unresolved checks, open tasks, wrong role, stale revisions/versions, concurrent source replacement, immutable report staleness, CSV formula neutralization, HTML escaping and explicit metric denominators. Full suite: 106 passed, one existing warning, in 128.41 seconds.
- Finalization locks the current case through guard evaluation, snapshot creation and final event. Snapshots retain actors, source hashes, checks/findings/decisions, manual/AI coverage and sample provenance. Later revisions mark reports stale; old snapshots remain inspectable.
- Legacy versioned-job JSON export is denied so it cannot bypass finalization.
- Queue, completion and correction-duration metrics derive from assigned cases and stored events, with case/correction/duration denominators.

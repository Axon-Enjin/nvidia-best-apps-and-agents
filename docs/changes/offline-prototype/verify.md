# Verify: Offline first working prototype

**Date:** 2026-10-21
**Overall:** FAIL

FAIL means the complete prototype is not finished. Tasks 1-8 are verified. Tasks 9-10 have verified local implementation, with standard-runtime and isolation gates still open. Do not archive or report the entire change complete.

## Completeness

- PASS: existing scaffold preserved as `e8c0ace`; branch `feat/offline-prototype` created.
- PASS: invalid dependency reproduced, then corrected; `uv sync --locked` succeeds using the unchanged lockfile.
- PASS: six offline behavior tests observed failing before implementation, then passing after mode guards were added.
- PASS: Task 1 committed as `08b0c09`, `fix: restore reproducible setup and enforce offline inference`; new test file passes Ruff.
- PASS: `uv run --offline --locked pytest -q`: 37 passed, one Starlette/HTTPX deprecation warning.
- PASS: Task 2 named accounts, local privileged MFA, revocable sessions and assigned case authorization implemented and tested.
- PASS: Task 3 encrypted immutable local originals, versioned membership, idempotent/revision-fenced imports, bounded child parsing and protected source downloads implemented.
- PASS: accepted profile, evidence workbench, separate manual/supervisor review, corrections, current-version reports, real printed OCR and encrypted SQLite recovery are implemented and exercised.
- OPEN: actual container/PostgreSQL build, workflow, OCR, restore and OS/container egress acceptance remain unrun. CI is prepared without an executed result.

## Correctness

- PASS: default/explicit mode validation, offline import rejection despite credentials, direct adapter zero-request behavior, offline worker handling of already-queued remote work and explicit online transport behavior tested.
- PASS: queued remote work processed offline retains deterministic results and marks remote coverage `not_run_offline` with incomplete outcome.
- LIMIT: `uv --offline` is a package-manager setting; this test run is not a whole-machine network isolation test. Provider transport tests are controlled test doubles, not live AI calls.
- PASS: a real SQLite/browser correction/export/process-restart loop and the 40-case deterministic evaluation set execute locally, with browser-origin and Python socket guards.
- LIMIT: these guards do not establish whole-machine network isolation or the standard PostgreSQL/container path.

## Coherence

- PASS: offline is an intermediate local milestone; the approved hosted-evaluation and operational-hospital goals remain.
- PASS: no remote credentials, cloud purchase, real-record authorization or completed hospital integration is invented.
- OPEN: Docker engine, WSL, Podman and PostgreSQL are unavailable. Official standalone Compose configuration validation passes; actual runtime verification is required before Tasks 9-10 sign-off.

## Review quality

- Security: named mode now denies anonymous/shared-token access. Legacy shared-token access requires explicit development-only configuration; it does not establish named accountability.
- Coverage: deterministic profile, source evidence, correction/manual guards, finalization, real OCR and local restore have direct tests. PostgreSQL/container/OS isolation remain explicit gaps.
- Context hygiene: document content remains untrusted; offline mode never substitutes canned model output.

## Findings

- WARNING: Starlette warns that HTTPX TestClient support is deprecated. The existing locked environment works; select a supported replacement deliberately rather than restoring an impossible package range.
- RESOLVED: local CSS/JavaScript and the versioned seven-artifact workbench now replace the old single-XML/chart UI.
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

## Task 8 evidence

- RED: four scenarios failed for absent OCR/confirmation contracts and unsupported scan status. GREEN: real printed PNG and image-only PDF extraction, pinned engine/model, missing binary, blank print, separate source confirmation and handwriting rejection pass. Full suite: 110 passed, one existing warning, in 161.53 seconds.
- Windows engine: Tesseract 5.5.3.20260724 with leptonica 1.87.0. Official release SHA-256 bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4 verified against GitHub release metadata. English tessdata_fast 4.1.0 hash is pinned in code and OCR-NOTICES.md. Pillow 12.3.0 and pypdfium2 5.14.0 are locked.
- Windows canceled installer execution. Extracting verified official binaries using verified 7-Zip required no administrator/PATH changes. The repeatable install_ocr.py command subsequently ran successfully. One attempted rerun while OCR held the executable open was blocked by Windows; the stopped-process rerun passed.
- Local process isolation bounds text, pixels, pages, time and memory. OCR supports at most 20 pages/document and 40 million pixels/page; excess is explicit incomplete, never truncated. Original, OCR candidates and source-confirmed values remain separate. Every scan candidate requires source confirmation; later confirmations reopen manual review.
- Source previews and confirmation controls are local and authorized. No claim of handwriting recognition, authenticity or clinical validation is made. Linux/container OCR execution remains Task 9.
- Primary references: [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html), [pypdfium2 API and process guidance](https://pypdfium2.readthedocs.io/en/stable/python_api.html) and [Debian package](https://packages.debian.org/trixie/tesseract-ocr). Licenses and install commands are in OCR-NOTICES.md.
- Ruling: require confirmation of every OCR candidate, beyond only critical fields, until scan quality is measured. Cost if wrong: reviewer effort; relax only with quality evidence.

## Task 9 evidence

- RED: recovery/restore contracts were absent. Subsequent failures exposed an unclosed SQLite backup connection on Windows and unbounded worker retries; both were corrected. GREEN: five recovery scenarios pass, including expired/competing leases, duplicate publication fencing, encrypted checkpoint/isolated restore, source hashes, named history/authorization, revoked restored sessions, missing sources, orphan staging and newer retirement tombstones. Full suite: 115 passed, 1 PostgreSQL skip, one existing warning, in 179.53 seconds.
- Compose 5.6.1 official standalone binary SHA-256 91b1492f0a923427651e2b955739d732ac36b8191193bf4799e62f3e3525c4cd verified from release metadata. `compose.exe config --quiet` passes. No Docker engine/WSL/Podman/PostgreSQL executable exists on this host; container build/start, standard PostgreSQL workflow/restore and Linux OCR remain unchecked.
- Prepared a read-only-root non-root web/worker image, private volumes, internal network and loopback publication. Python 3.14.5 and PostgreSQL 17.11 image digests were verified from Docker Hub. Linux Tesseract package is pinned to Debian 5.5.0-1+b1 with the independently pinned English model.
- Added CI lint/tests and a real PostgreSQL migration/correction/report scenario. CI has not run; no L1 claim is made. LOCAL-SETUP.md and scripts/local.ps1 provide start/stop/checkpoint commands.
- Restore requires a new directory and empty PostgreSQL target, validates encrypted sources, resets interrupted jobs and revokes sessions. Authenticated retirement tombstones deny access after older-backup restoration. This is not physical retention deletion or a scheduled backup service. Checkpoints are bounded to 512 MB.
- Ruling: preserve orphan staging objects for explicit operator reconciliation rather than delete uncertain evidence. Cost if wrong: disk growth until a reviewed retention job exists.
- Ruling: continue Task 10 on the verified SQLite development path while leaving the standard container/PostgreSQL gate open, as the task explicitly requires when runtime is unavailable. Cost if wrong: platform-specific defects may remain until that gate is executed.
- Primary references: [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html), [version policy](https://www.postgresql.org/support/versioning/) and [Compose internal networks](https://docs.docker.com/compose/how-tos/networking/).

## Task 10 local acceptance evidence

- Locked 40 independently authored synthetic evaluation cases: 20 discrepancies, 10 clean, 10 incomplete/adversarial. Twenty corrected pairs retain separate original manifests. The lock records original/corrected manifest hashes, source hashes, expected checks and exact field/page/value evidence. Held-out printed PNG/PDF equivalents use separate fictional templates. No clinical/model accuracy or hospital-benefit claim follows from this set.
- Real Chromium and a real local server/database complete import, discrepancy/source inspection, correction ownership, handoff/acknowledgement, corrected import, recheck, manual P07/P08, different-supervisor acknowledgement, final snapshot, CSV/print, process termination/restart and reopen. A second named reviewer is denied case/source/report access. Old originals, review history, current report and AI not_run_offline survive restart.
- The acceptance server installs a Python socket audit guard independent of NETWORK_MODE and verifies that guard using a blocked startup probe. Browser routing separately blocks external origins. No external application request was recorded before or after restart. These controls do not establish a whole-machine firewall; container/OS isolation remains unrun.
- Environment: Windows 11 build 26200, Python 3.14.5, SQLite 3.50.4, FastAPI 0.156.4, Starlette 1.9.0, SQLAlchemy 2.0.55, Alembic 1.20.0, pytest 9.1.1, Ruff 0.17.1, Playwright 1.64.0 / Chromium 156.0.8078.4. OCR/package versions are recorded under Task 8. This run used no provider credentials.
- A bounded metadata exercise uses 10,000 rows, five concurrent named readers, 2,000 assigned rows each and 100-row response limits. It checks assignment isolation and rejects a requested page size of 101. The five-request latency sample is descriptive only, not a production capacity/SLA result or 100-import/day proof.
- Screenshots: test-results/workbench-1366-1.png, workbench-375-1.png, workbench-1366-2.png and offline-acceptance.png. The final 2x capture uses a 683x384 effective viewport with device scale 2, replacing an invalid CSS-zoom simulation. Native browser-chrome zoom gestures and screen-reader conformance are not established. Launch, checkpoint and isolated restore commands are in LOCAL-SETUP.md.
- Acceptance guard regressions reproduced and corrected: current P10 display, missing-original hash verification at closeout, reassignment reopening and explicit absent/unknown marks/signatories/dates. Prior combined run: 164 passed, 1 explicit PostgreSQL skip, 2 warnings. One is the existing Starlette warning; Pydantic produced an intermittent schema-field warning in an existing concurrent-account scenario. No warning suppression was added.

## Fresh review and fix pass

A fresh read-only whole-branch code/interface review found four Important issues and no established Critical issue. All four were reproduced through real API/browser failures before their fixes:

1. An unrelated confirmation promoted an unmatched extra attachment. Effective source status now requires all four identity anchors to match the case before readable/matched status; extra review stays blocked otherwise.
2. An explicitly supplied missing retirement ledger was silently empty. Restore now validates that directory before creating a restore target and fails closed if it disappears during reconciliation.
3. Queue filters used immutable raw job outcomes after closeout. Current versioned queue categories now derive from current rule/job/case state: checks unavailable before a successful current run, needs review until closeout, completed after current finalization. Raw coverage/AI results remain unchanged.
4. Manual/extra evidence controls hardcoded page 1. Reviewers now select one or more real page numbers, with client/server bounds and page-2 persistence checked in Chromium.

The targeted review-fix/viewport run passed five scenarios. Source-before-decision placement was additionally reproduced failing and fixed after the page controls lengthened the form. Desktop and effective-zoom recaptures show the source before the action form. There is no second reviewer certification; the fixes are covered by regression tests and the final combined suite.

Deferred minor: a completed import may retain its earlier processing notice. Stored job status, coverage, source version and final record are authoritative; the notice is cosmetic.

## Rulings and unresolved review scope

- Ruling: isolate the profile in profile.py and expose it through audit.py to preserve legacy records/contracts. Cost if wrong: relocate code without changing the interface.
- Ruling: import an explicit manifest and its originals, displaying declared types first. Cost if wrong: add a guided manifest editor without changing immutable membership.
- Ruling: derive correction tasks/extra expectations from append-only events. Cost if wrong: add cached projections while retaining the events.
- Ruling: require confirmation of every OCR candidate until quality is measured. Cost if wrong: reviewer effort; any relaxation needs evidence.
- Ruling: preserve uncertain orphan staging for operator reconciliation. Cost if wrong: disk growth until a reviewed retention job exists.
- Ruling: continue SQLite acceptance while retaining the standard PostgreSQL/container gate, as Task 9 explicitly permits when no runtime exists. Cost if wrong: platform-specific defects remain until that gate executes.
- Ruling: current queue categories reflect workflow state, with raw coverage/AI visible in the case. Cost if wrong: refine filtering labels without rewriting evidence.
- Ruling: use reduced effective viewport/device scale for a 200-percent equivalent, not CSS zoom. Cost if wrong: native-browser behavior still needs manual follow-up; no gesture/conformance claim is made.
- Ruling: treat source placement as material after page controls lengthened the form. Cost if wrong: refine navigation after observing reviewers.

The reviewer explicitly set aside the following; they remain bounded as follows:

- Actual container/PostgreSQL/Linux OCR/OS isolation/hosted CI: still unrun and gated, not implicitly approved. Cost if wrong: runtime-specific failures await execution.
- Clinical/model quality and hospital effectiveness: outside deterministic synthetic acceptance, with separate later evaluation. Cost if wrong: no reviewer-benefit or clinical claim is justified.
- Old supervisor acknowledgements after rerun: the current-event cutoff blocks P07 completion; the old event remains inspectable. Cost if wrong: revisit acknowledgement recording UX; no completion bypass was established.
- One attachment covering multiple expectations: named manual applicability can cover several requirements, with source evidence and reasons. Cost if wrong: require distinct attachment mappings after workflow evidence.
- Native zoom, screen-reader conformance and administrative UI completeness: not established here. Named account administration is the tested local CLI; screen-reader/native gesture assessment remains open. Cost if wrong: accessibility or operator-workflow defects may remain.
- Broader recovery crash windows and concurrent account revocation: not reproduced by the bounded review. Recovery commands require stopped services, source checks and an isolated target; auth is checked on every request and restore revokes sessions. Cost if wrong: further fault/concurrency tests may identify gaps; no broader assurance is claimed.

Overall remains FAIL until Tasks 9.4 and 10.3/10.4 pass on an actual standard runtime with independent OS/container network isolation. No change archival, hosted release, live-model study or hospital sign-off occurred.

## Final local verification result

- `uv run --offline --locked pytest -q --tb=short`: **168 passed, 1 skipped, 1 warning in 227.00s (0:03:46)**. The one skip is the explicitly unavailable PostgreSQL runtime; the one warning is Starlette/HTTPX deprecation. No warnings were suppressed.
- `uv run --offline --locked ruff check sentinel tests migrations scripts`: all checks passed. Official standalone Compose 5.6.1 `config --quiet`: passed.
- Final five-request metadata sample: median 0.1077 seconds, maximum 0.1172 seconds. This is SQLite metadata only, without an import throughput or production latency claim.
- Test fixture bytes are preserved, including Windows CRLF manifest formatting. Git permits CR at fixture line ends rather than altering locked originals/hashes.
- Full-workspace FMD validation reports two unchanged untracked research/old-plan findings. Strict validation of the tracked artifact snapshot returns zero failures/warnings. Unrelated local files remain untouched.

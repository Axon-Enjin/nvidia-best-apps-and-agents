# Sentinel Claims: build checklist independent of FMD

Date: 2026-10-21. Purpose: identify work that can be implemented from the accepted product baseline without the external FMD engine. This checklist was requested by the owner; no application implementation or deployment was performed while creating it. All boxes remain unchecked until their completion evidence exists.

FMD is documentation tooling, not an application runtime dependency. The accepted [product](PRODUCT.md), [experience](DESIGN.md), and [detailed decisions](PILOT-DECISIONS.md), including checklist P01–P10, provide sufficient direction for the software work below. FMD reconciliation is now complete, with PROCEED WITH FIXES in the [scrutiny assessment](docs/scrutiny-sentinel-node.md). The [canonical requirements](docs/prd-sentinel-node.md), [architecture](docs/sdd-sentinel-node.md) and [test plan](docs/qad-sentinel-node.md) now govern the work below. Engine access is no longer a documentation blocker. The existing application-development pause remains until the owner instructs execution.

## What exists now

Read-only inspection found these starting points. Presence of code is not proof that it is complete, passing, secure, or deployable.

| Area | Starting point | Gap against the accepted product |
|---|---|---|
| Browser | `sentinel/static/index.html`, favicon | Referenced `app.css` and `app.js` are absent; old name, single XML/chart upload, and shared-token login need replacement. |
| API and persistence | `sentinel/api.py`, `sentinel/db.py`, `sentinel/service.py`, migrations | Existing claim/job/review model needs multi-document versions, named actors, assignments, correction tasks, and append-only events. |
| Rules and extraction | `sentinel/audit.py`, `sentinel/documents.py` | Internal prototype XML and text-PDF handling exist; accepted sample-profile checks and printed-scan OCR remain work. |
| AI and jobs | `sentinel/inference.py`, `sentinel/worker.py` | Provider adapter and job processing exist; new evidence schema, coverage rules, recovery, and live verification remain work. |
| Fixtures and tests | `sentinel/samples.py`, `tests/test_audit.py`, `tests/test_workflow.py` | Fixtures/tests reflect the earlier proposal. Do not carry historical pass results forward. |
| Packaging | `pyproject.toml`, `uv.lock`, `.env.example`, `alembic.ini` | Dependency installation needs fresh verification; standard PostgreSQL local startup and deployment packaging are unfinished. |

## Can be built and locally verified without FMD or hospital access

Ordinary development tools and package installation are still needed. These tasks do not need an official hospital export, patient data, cloud purchase, or live AI credentials. IDs indicate the recommended implementation order, not estimated duration.

- [ ] **B01 — Restore a reproducible local application setup.** Inspect the dependency/lockfile mismatch, install from a reviewed lockfile, add standard PostgreSQL container startup, migrations, and separate web/worker commands. Preserve the provisional code. **Done when:** a clean checkout starts through documented commands, a sample case survives restart, and failures report a useful cause. **Depends on:** none.

- [ ] **B02 — Implement versioned claim bundles.** Add facility/encounter/claim references, document types, immutable source versions and hashes, and a record of the current bundle. Replace the one-XML/one-chart assumption. **Done when:** multiple documents belong to one confirmed encounter, identical uploads do not silently create duplicate work, and revised sources preserve the previous version. **Depends on:** B01.

- [ ] **B03 — Add named users, roles, and case assignments.** Implement reviewer, supervisor, and administrator permissions, secure sessions, privileged-role MFA, account disablement, and access checks on API/document/export routes. **Done when:** two reviewers can perform their permitted work, denied actions fail server-side, and review actions identify their actor. **Depends on:** B01–B02.

- [ ] **B04 — Create realistic synthetic sample bundles.** Encode the seven artifact types in SAMPLE-ADULT-MEDICAL-1, including the internal sample eSOA contract. Supply clean, discrepant, incomplete, and corrected versions. **Done when:** fixtures have documented expected findings/source locations and do not claim official schema compatibility. Keep prompt-development cases separate from the locked evaluation set. **Depends on:** B02; can be prepared alongside B03.

- [ ] **B05 — Build the import wizard and coverage report.** Accept the supported sample XML/text PDFs and document metadata; enforce 25 MB/file, 100 MB/version, 150 pages/version, and 30 files/version. Confirm document membership and flag missing, unreadable, encrypted, or unsupported inputs without truncation. **Done when:** incomplete imports remain inspectable and cannot be mistaken for completed checks. **Depends on:** B02–B04.

- [ ] **B06 — Implement the sample-profile rules and review checklist.** Apply P01–P10 from PILOT-DECISIONS.md: scope, required artifacts/fields, identity, dates, known arithmetic, narrative review, manual signature-presence review, expected attachments, and closeout. Narrative comparison can initially be completed manually. **Done when:** clean/defective fixtures produce the expected results, required gaps block completion, and the only noncritical exception is the documented supervisor withdrawal of an incorrectly expected extra attachment. **Depends on:** B04–B05. No official clinical/package/eligibility rule is invented.

- [ ] **B07 — Finish the review queue and evidence workbench.** Implement the missing browser styling/behavior using Sentinel Claims branding. Show queue filters, assignee, coverage, findings, and the exact supporting document/page/field beside each finding. **Done when:** users can complete the flow by keyboard, evidence opens the right version, and empty/loading/error states work. **Depends on:** B03, B05–B06.

- [ ] **B08 — Record reasoned decisions and correction handoffs.** Add request-correction, dismiss-with-reason, and escalation actions; responsible person/department; manual handoff/acknowledgement tracking; and an exportable correction sheet. **Done when:** users can track who owes a correction and hand it off through existing channels without automated messaging or HIS access. **Depends on:** B03, B06–B07.

- [ ] **B09 — Recheck revisions and preserve history.** Link corrected uploads to the original case, rerun affected checks, show old/new findings, and record actor/time/reason events. Invalidate affected decisions after source/rule changes and reject stale concurrent edits. **Done when:** the initial discrepancy and its correction remain traceable, and an earlier report is visibly stale after revision. **Depends on:** B02, B06, B08.

- [ ] **B10 — Implement review closeout and reports.** Enforce P10 before a named reviewer can mark a version Ready for final submission review. Produce CSV and printable reports containing coverage, source/rule versions, decisions, actors, and permitted exceptions. **Done when:** unresolved requirements prevent finalization and the report describes internal review completion without implying submission or payer approval. **Depends on:** B06, B08–B09.

- [ ] **B11 — Add printed-scan OCR and extraction confirmation.** Process clear scanned PDFs and PNG/JPEGs locally, retain page/field anchors, display extracted text beside originals, and record source-backed confirmation of critical identifiers/dates/amounts. **Done when:** representative printed scans enter the same workflow, while unreadable handwriting and ambiguous extraction stay incomplete or require manual review. **Depends on:** B05–B07. No cloud OCR service is required for this task.

- [ ] **B12 — Extend the AI adapter and test its boundaries.** Accept the new versioned evidence model; validate output structure and source anchors; record model/prompt versions; handle timeout, invalid output, injection attempts, and unavailable configuration. Use explicit test doubles only in automated tests. **Done when:** the app reports unavailable inference honestly and supports the documented manual-review fallback with supervisor acknowledgement. **Depends on:** B02, B06, B09. Live inference and its accuracy are separate external checks below.

- [ ] **B13 — Add event-derived operational metrics.** Calculate awaiting-documents/correction counts, review turnaround, and accepted/dismissed findings from stored actions. **Done when:** values reconcile with case histories and no recovery amounts or reimbursement probabilities are fabricated. **Depends on:** B08–B10.

- [ ] **B14 — Harden uploads, processing, and private storage.** Finish upload content validation and malware/quarantine handling, private document retrieval, durable queue leases/retries, safe restart recovery, and bounded work. Implement the local storage path and test the object-storage contract against a local compatible service/test harness. **Done when:** unauthorized access, repeated requests, oversized/malicious files, and worker interruption do not leak data or duplicate review actions. **Depends on:** B03, B05, B09, B11–B12. Hosted storage verification remains separate.

- [ ] **B15 — Package the app for deployment and recovery.** Create web/worker images, environment configuration, health checks, migrations, secret handling, backup/restore procedures, and implement the canonical [operator runbook](docs/ops-sentinel-node.md). **Done when:** a clean local container deployment can be upgraded, restarted, backed up, and restored without losing verified source/history relationships. **Depends on:** B01, B03, B09, B14. Cloud provisioning is not part of this task.

- [ ] **B16 — Run the local acceptance suite.** Exercise the 40 locked synthetic bundles, role checks, evidence/version correctness, stale edits, worker failures, restored data, and the end-to-end correction loop. Measure local UI/processing performance against the accepted targets and report the test environment. **Done when:** deterministic checks match expectations, required gaps never falsely finalize, and all results distinguish actual execution from test doubles. **Depends on:** B04–B15. Live AI quality, hosted performance, and hospital usability cannot be claimed from local tests.

## Recommended first working milestone

Complete B01–B10 as a **text-first local review-and-correction flow**, with source-appropriate manual review where automation is not yet available:

1. A named reviewer opens a complete fictional case with a documented discharge-date mismatch.
2. The app shows the two conflicting source locations.
3. The reviewer records a correction request and its responsible department.
4. A corrected bundle is imported and checked; the earlier version remains available.
5. Required manual/checklist items are completed before the final internal review report is produced.
6. Another permitted user can inspect the saved history after restart.

Use local private storage and the access controls already included above. This milestone verifies a useful workflow; it is not the complete first release. B11–B16 and the applicable external release checks still remain.

## Can be prepared now; completion needs something other than FMD

| Work | Build/prepare without the engine | Actual external dependency |
|---|---|---|
| Live Nemotron comparison | Adapter, prompts, evidence validation, failure handling, evaluation harness | Nebius credentials, available model endpoint, inference budget, and real calls on synthetic cases. |
| AI quality evaluation | Annotated held-out fixtures, scoring, repeated-run harness | Live model runs and adjudication of findings against the annotated evidence; meet the accepted precision/recall targets before claiming readiness. |
| Hosted application | Images, configuration, migrations, health checks, runbook | Hosting access, selected region/preset, cost decision, URL/TLS configuration, private storage, and a verified deployment. |
| Hosted recovery and performance | Backup jobs, restore procedure, local load tests | Restore/load testing in the actual hosting environment; no production claim from a local run. |
| Reviewer usability evaluation | Task scripts, matched sample cases, timing and error capture | Two practicing claims reviewers, their time, and observed outcomes. No hospital partnership is needed to write the software first. |
| Hospital export adapter | Adapter boundary and explicit sample contract | Authorized representative exports, current schema/version, readable pre-encryption access, and vendor/hospital mapping tests. |
| Actual hospital records | Access/retention/processing controls and data-flow description | Explicit authorization for real data and hospital-specific hosting, processor, retention, and operating arrangements. Synthetic-only remains the current boundary. |
| Official policy/clinical validation | Versioned rule registry with source/effective-date/applicability fields | Applicable authoritative rules, current schemas/code lists, domain review, and evidence that each implemented check is correct. |
| Unprepared/missing claims detection | Future input contract for an encounter manifest | A complete expected-encounters/claims feed. Imported folders alone cannot reveal cases never exported. This remains later scope. |

FMD is specifically needed for the requested canonical artifact generation/reconciliation and its engine checks. It is not the missing prerequisite for these integrations, credentials, or evaluations.

## Scope guardrails

- Keep the accepted adult medical inpatient scope and checklist; do not silently expand to other packages.
- Keep sample records identified at the environment/export level. Test stubs must not masquerade as live results.
- Do not add direct claim submission, autonomous coding, financial recovery claims, or hospital write-back.
- Maintain canonical artifacts through the pinned external FMD engine; never modify or commit to the engine repository.
- When implementation is authorized, use this checklist as the work order and verify each deliverable before checking its box. Update the canonical artifacts with actual implementation evidence; never retroactively label unverified behavior as passing.

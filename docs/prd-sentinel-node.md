# Product Requirements Document (PRD)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin, project owner
**Status:** Draft
**Last reconciled:** 2026-10-21
**IDEA:** [Idea brief](idea-sentinel-node.md)
**BRD:** N/A; no investment or pricing decision this cycle.

Approved scope is stable enough for design. Draft status preserves the distinction between accepted requirements and unverified implementation. [Dated decisions](../PILOT-DECISIONS.md) record approval provenance; this document now owns product behavior.

## 1. Product Purpose & Value Proposition

Help a hospital PhilHealth reviewer reconcile prepared claims with supporting records, route corrections, and record completion on the current bundle. The existing hospital system retains final checks and submission authority. The first deliverable is a deployed, persistent evaluation workspace using synthetic patient records.

## 2. Target Personas

**Primary:** Named PhilHealth reviewer, assigned to adult general medical inpatient ACR claims after discharge and before initial submission. Needs understandable findings, reliable coverage and retained revision history.

**Secondary:** Supervisor assigns/reassigns cases, resolves disputes and monitors work. Administrator manages accounts, published profiles/rules and operations; review actions require an additional reviewer/supervisor role. Correction recipients in billing, medical records and clinical departments need no new login: reviewers record manual handoff and acknowledgement.

Planning scale is one hospital/team, 3?5 reviewers and one supervisor. No sponsor or actual users are established.

## 3. Core Features & Priorities

| ID | Feature | Description | Priority |
|---|---|---|---|
| PRD-F1 | Accounts and queue | Named sign-in, privileged MFA, roles, assigned-case access, queue filters | Must-Have |
| PRD-F2 | Versioned imports | Document membership, supported PDF/image/XML, printed OCR, source viewer and provenance | Must-Have |
| PRD-F3 | Coverage and checks | Published sample profile, P01?P10, deterministic results and evidence-linked AI questions | Must-Have |
| PRD-F4 | Review and correction | Reasoned dispositions, ownership/handoff, revised sources, rerun and append-only history | Must-Have |
| PRD-F5 | Completion and exports | Guarded internal completion, versioned CSV/printable records and event-derived metrics | Must-Have |
| PRD-F6 | Deployed operation | HTTPS, persistence, durable jobs, recovery, private storage, monitoring and local setup | Must-Have |
| PRD-F7 | Qualified hospital adapter | Obtain and test a hospital export profile and applicable checks | Should-Have; mandatory before operational pilot |
| PRD-F8 | Submission and clinical automation | Direct submission, coding, HIS mutation, diagnosis or benefit decisions | Won't-Have (v1) |

## 4. User Stories & Acceptance Criteria

**US-01: Work within assigned responsibility (PRD-F1).**

- Given an authenticated reviewer, when opening queue or any case/file/export URL, then only assigned cases are accessible. Supervisor can assign and view all cases; administrator alone cannot review.
- Given a disabled account, expired session, or privileged account without MFA, when attempting the protected operation, then access fails without exposing document existence/content.
- Given stored cases, when filtering assignee/state or sorting age, then counts and rows derive from persisted records. Filing due dates require a supplied value or verified applicable rule.

**US-02: Establish the actual bundle (PRD-F2).**

- Given supported files, when imported, then preserve immutable originals and hashes, document types, facility/encounter/claim association and a versioned manifest.
- Given scans, when extracting critical identifiers/dates/amounts, then require source-backed human confirmation before blocking comparisons use them. Ambiguous native-text extraction requires the same confirmation.
- Given unsupported, encrypted, damaged, over-limit or unreadable material, then show the specific coverage gap; never silently truncate or manufacture values.
- Given a duplicate request or source correction, then deduplicate retries; genuine revisions create a new immutable bundle and retain previous evidence.

**US-03: Distinguish evidence from coverage (PRD-F3).**

- Given the current sample profile, when checks run, then every check reports Completed, Needs review, Not run, Unsupported or Failed with source/rule version.
- Given a finding, when opened, then its exact source fields/pages and rule basis resolve on the same immutable version.
- Given model timeout or invalid evidence/output, then automation remains Failed/Not run; never substitute canned success. Manual comparison plus supervisor acknowledgement is the allowed P07 fallback.

**US-04: Close the correction loop (PRD-F4).**

- Given a true discrepancy, when requesting correction, then record responsible person/department, reason, source anchors, handoff and acknowledgement; the source author corrects the source system.
- Given a false positive, when dismissing, then retain named actor, reason and supporting evidence. No generic override can waive an unresolved core requirement.
- Given revised sources/rules, when rerun, then invalidate affected prior dispositions and finalization. Conservatively reopen all if dependency cannot be established.
- Given concurrent stale edits, when saving, then reject the stale write and preserve both history and current state.

**US-05: Record an honest review outcome (PRD-F5).**

- Given current P01?P09 resolution and closed/reasonedly cancelled correction tasks, when a named reviewer completes review, then mark Ready for final submission review and export the current version's coverage, findings, decisions and provenance.
- Given any unresolved required check, identity conflict, open task or stale source/rule version, then completion is blocked transactionally.
- Given an old exported record after revision, then retain it with a visible stale status in the app; a downloaded file identifies its version and must not imply perpetual currency.
- Given operational metrics, then counts and duration denominators come from stored events, never invented financial recovery.

**US-06: Resume after failures (PRD-F6).**

- Given a clean environment, when following documented startup/deploy steps with credentials, then the same app supports import through export with persistent state.
- Given worker termination or duplicate delivery, then recover the job with bounded retries and one published result per run.
- Given a backup restore, then restore linked database and document versions within the planned recovery bounds and reconcile jobs without silently finalizing cases.

### 4.1 Initial completion contract

Profile `SAMPLE-ADULT-MEDICAL-1` is an internal synthetic evaluation contract, not an official PhilHealth schema. Seven mandatory artifacts: CF2-equivalent claim summary, CF4 clinical summary, CF5 supplementary summary, sample eSOA XML, discharge summary, sample CSF and eligibility evidence. Extra laboratory/chart attachments become required only by an explicit reviewer expectation with reason.

| ID | Required check | Completion / resolution |
|---|---|---|
| P01 | Adult medical inpatient scope; facility, encounter/claim, DOB and admission anchors | Unknown scope, missing anchors or age under 18 blocks this profile. Correct extraction against source or obtain revised source; no override. |
| P02 | All seven artifacts typed, matched and readable | Missing/unmatched/unreadable required content blocks. Replace or source-transcribe a legible original. No core-artifact waiver. |
| P03 | Claim identifiers, DOB/admit/discharge, diagnosis and disposition; CF4 admission reason/course/treatment/outcome; CF5 diagnosis/code/disposition; eSOA encounter/currency/lines/discounts/total | Missing source values block. Code presence is not coding validity. Explicit none only when stated in source; extraction corrections retain provenance. |
| P04 | Equivalent patient/encounter identifiers across documents | Explicit conflicts block; name variation alone is a question dismissible with matching IDs and evidence. Remove wrong association only through a new version or corrected source. |
| P05 | Equivalent dates/disposition and chronology | Birth after admission, discharge before admission or true disagreement requires source correction. Resolve ambiguous parsing first; no minimum-stay inference or waiver. |
| P06 | Supported sample eSOA PHP arithmetic | Sum gross lines minus explicit discounts equals net within PHP 0.01. No comparison with benefit amount. Unknown financial semantics are Unsupported; correct extraction/source. |
| P07 | Narrative agreement with source anchors | Every AI question needs human disposition. True discrepancies need source correction; false positives need evidence/reason. AI failure allows documented manual comparison plus supervisor acknowledgement. No unresolved clinical-question waiver. |
| P08 | Manual presence review of expected sample marks, printed signatory and date | Missing required content needs completed source. No authenticity or legal-signature certification; sample marks are fictional. |
| P09 | Reviewer-declared extra attachments | Require readable matching attachment and recorded review. Sole v1 exception: supervisor withdraws a mistakenly declared extra requirement with applicability reason; never a core artifact. |
| P10 | Current-version closeout | P01?P09, tasks and reviewer complete; no bypass. Source/rule changes reopen affected review and mark prior report stale. |

The report lists excluded checks: official XML conformity, clinical appropriateness, eligibility determination, coding validity, filing-period compliance, signature authenticity and payer acceptance. Presence of eligibility evidence does not establish entitlement. Source absence in the bundle never proves care was absent.

## 5. App Flow & UX Intent

**Design reference:** [DSD](dsd-sentinel-node.md).

### 5.1 Screen Inventory

| Screen | Purpose | States: empty / loading / error / success |
|---|---|---|
| Sign-in | Named access, privileged MFA | Credentials absent / signing in / generic failure with retry / queue |
| Queue | Assigned work, import entry | Import sample action / skeleton / retry without fake rows / filtered records |
| Import | Files, matching, coverage | Add files / upload+extract stages / per-file retry/unsupported / versioned manifest |
| Case workbench | Evidence, findings, corrections, history | No run yet / queued+running / failed check with fallback / current results |
| Review/export | Completion and printable record | Requirements outstanding / save or export pending / blockers or stale conflict / versioned record |
| Supervisor overview | Assignment, disputes and event metrics | No events / loading / retry / measured counts |
| Administration | Accounts, published profiles and diagnostics | No config / loading / validation failure / recorded change |

### 5.2 Navigation Model & Information Architecture

Desktop sidebar: Claims, Overview (supervisor), Administration (admin). Case workbench tabs: Review, Corrections, History. Global account menu, environment indication, current case/version and role remain visible.

| Destination | Route | Auth / feature |
|---|---|---|
| Sign-in | /login | Public; no clinical data, PRD-F1 |
| Queue/import | /claims, /claims/new | Reviewer/supervisor, PRD-F1/PRD-F2 |
| Case and tabs | /claims/:id | Assigned reviewer or supervisor, PRD-F2/PRD-F3/PRD-F4 |
| Report | /claims/:id/reports/:report_id | Same case permission, PRD-F5 |
| Overview | /overview | Supervisor, PRD-F5 |
| Administration | /admin | Admin; does not confer clinical access, PRD-F1/PRD-F6 |

Every deep link rechecks server permissions. No anonymous document links. Prepared sample demonstrations use controlled sample access; public visitors cannot upload arbitrary records.

### 5.3 App Flow

Receive ? match ? check coverage ? inspect evidence ? disposition ? request/handoff correction ? import revised sources ? rerun ? named final review ? export ? existing hospital submission process.

Incomplete/unsupported documents stay in review; corrections lead to Awaiting correction; new source versions return to In review. Case states: Received, In review, Awaiting correction, Ready for final submission review, Archived. Job progress and check statuses are separate. Leaving a screen preserves saved state. Session expiry requires sign-in then safe resume; duplicate submit cannot create duplicate work. Explicit manual fallback preserves the failed automation status.

### 5.4 Onboarding Flow

Invitation-based named accounts; no open registration. Reviewer role and assignment are configured before first access. First value: find the seeded date conflict and inspect both sources. Target under 15 minutes, unmeasured. Resume a saved case; privileged MFA is required. Use only account identifiers necessary to invite and distinguish reviewers.

### 5.5 UX Constraints

Desktop 1366?768, keyboard accessible, narrow-screen stacking. English first. Filipino/mixed language and handwriting remain manually reviewable but no promised automated coverage. Original and extraction shown separately. Asia/Manila display with explicit dates and PHP formatting.

Limits per bundle: 25 MB/file, 100 MB total, 150 pages, 30 files; reject before processing beyond bounds. No truncation.

One environment indication: ?Evaluation workspace: sample patient records.? Exports retain provenance. Do not repeatedly label records static or misrepresent them as actual hospital records.

### 5.6 Instrumentation & Event Taxonomy

| Event | Fires when | Metadata properties | Metric |
|---|---|---|---|
| bundle_imported | Version committed | opaque case/version, counts, bytes, elapsed | Import effort and failures |
| check_run_finished | Run terminal | rule/model version, states, duration, queue wait | Coverage, latency, failure rate |
| finding_dispositioned | Review decision committed | opaque finding, action, actor ID | Accepted/dismissed ratios |
| correction_handed_off / correction_acknowledged | Reviewer records handoff | task ID, timestamps | Handoff turnaround |
| review_completed / review_reopened | Guarded transition | version, actor, reason code | Completion and rework |
| report_exported | Authorized export | report ID, format | Export audit |

Use snake_case, metadata only. No third-party patient analytics. Internal operational events are access controlled; account-linked audit records remain personal data. Active review time is measured separately in the supervised study so an open browser tab is not treated as work.

## 6. Out of Scope for This Release

PRD-F8 and excluded populations/packages in IDEA. Also multi-hospital tenancy, SSO, local folder connectors, full return/denial management, pricing/payments, universal XML adapters and encounter-manifest reconciliation. Hospital adapter is a later qualification step, mandatory for operational pilot. No automated messaging to correction recipients.

## 7. AI / Agent Feature Specifications

- Model-assisted narrative comparison using remote Nemotron 3 Super through Token Factory; exact deployed model identifier/settings must be pinned before evaluation.
- Inputs: relevant current-version synthetic source excerpts with page/field anchors. Output: bounded discrepancy questions, evidence and abstentions, validated against source.
- Humans decide all findings, correct source records, acknowledge manual fallback and finalize review.
- Provider failure produces explicit Failed/Not run plus the P07 fallback. No model tools, claim mutation or submission.
- Context and retry caps are specified in SDD ?8; actual price and funded spending ceiling must be set before calls. No numeric cost claim is established.

## 8. Dependencies & Assumptions

Assumptions: bounded workload, readable sample exports, OCR utility, reviewer benefit and chosen stack suitability. Dependencies: provider access/region/terms, cloud quota/cost and exact versions; two actual reviewers for evaluation; sponsor/export/profile/data arrangements for operational pilot. These are unfulfilled, not owner preferences to re-ask. [SCRUTINY](scrutiny-sentinel-node.md) owns the assessment.

## 9. Implementation Plan

| Phase | Entry | Exit | DRI | Top risk |
|---|---|---|---|---|
| Requirements | Approved decisions | Reconciled scope and test plan | Yushin | Drift from earlier proposal |
| Design | Stable requirements | Reviewable screens/contracts; exact build choices verified | Yushin | OCR/input complexity |
| Development | Explicit owner instruction resumes app work | All Must-Haves implemented and locally verified | Yushin | Provisional scaffold mismatch |
| Testing | Functional end-to-end slice | QAD, security, AI, restore and UI evidence | Yushin | False completion |
| Deployed evaluation (A) | Release gates met | HTTPS workflow demonstrated, reviewer criteria met | Yushin | Provider/operations gaps |
| Operational pilot (B) | A plus sponsor/export/data approvals | Shadow-use evaluation with hospital keeping submission authority | Yushin with named hospital lead before B | Unqualified inputs |
| Maintenance | A or B released | Review metrics, incidents, costs and scope after first week and at 30 days | Yushin | Unmonitored failure |

**Rollout:** Separate sample environment, supervised accounts first. Proposed B study: two weeks and 50 consecutive in-scope claims, only after explicit real-data authorization. No production URL currently exists.

**Rollback plan (single source):** Any unauthorized access, data loss, false ready state, wrong-version evidence, or sustained core-flow failure triggers containment. Pause affected writes/finalization and AI; preserve records; redeploy the previous immutable image with compatible schema. If data is corrupted, restore a coordinated database/object checkpoint into isolation, reconcile post-checkpoint events, verify permissions and smoke tests, then switch traffic. Exact executable command awaits packaging and must be rehearsed before release; do not invent a working command.

**RFC cross-reference:** None. Current single-host modular design is conventional and reversible; no new irreversible architecture decision this cycle.

## Self-Check

- [x] Six Must-Haves have stable IDs, scenarios, routes and completion rules.
- [x] Scope, human authority, events and rollout/rollback intent are explicit.
- [ ] Implementation, deployment, measurements and release gates evidenced.

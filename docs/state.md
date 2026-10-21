# Project State: Sentinel Claims

**Project slug:** `sentinel-node`
**Owner:** Yushin
**Last updated:** 2026-10-21

## 1. Position

**Current milestone:** Implement, entered 2026-10-21. **Next milestone:** Verify the first offline prototype.
**Exit condition:** Complete the local import, evidence review, correction, revised-source review, guarded closeout/export, local OCR and recovery tasks; execute disconnected browser acceptance.
**Current blocker:** No owner pause remains. Docker is absent from the current command path, so container/PostgreSQL verification must wait for an available runtime; it does not block the next account/domain tasks.
**Product:** Hospital PhilHealth reviewers reconcile prepared adult medical inpatient claims and source corrections before submission through the existing hospital system.
**Engagement:** Hospital readiness first; local offline prototype before hosted evaluation. **Vault status:** none.

## 2. Active signals

| Signal | Evidence | Consequence |
|---|---|---|
| S1 / S2 / S4 | Approved UI, backend/auth/data and workflow | PRD, DSD, SDD |
| S5 | Owner explicitly resumed the build | BUILD guide; task-by-task implementation |
| S7 / S9 / S12 / S20 | Eventual hosted release, named accounts and remote model path | QAD, CLR, AIA, OPS remain release dependencies; offline core has no provider dependency |
| S11 / S16 | Public repository and multiple contributors | Reader-facing status and L1 practices required |
| S22 / S27 / S29 | Hackathon context, time box and claims activity | Pitch deferred; no delivery-date promise; CLR postures retained |
| S23 | Scaffold checkpointed and tested against existing PRD/SDD | Active CHANGE: offline-prototype |

No production deploy, real patient data, pricing, named buyer or investment decision exists. No SAD or new RFC is justified. The existing conventional architecture is retained.

## 3. Operating frameworks

Milestones. Work inline on `feat/offline-prototype` in the existing isolated worktree.
L1 is required by multiple contributors; current evidence is local tests only, no CI/preview/deploy pipeline. Packaging task adds CI. Do not claim the required level already exists.

## 4. Open assumptions

| ID | Assumption / uncertainty | Risk / resolution |
|---|---|---|
| A1 | Build rate uncalibrated | Yushin; no date promise until measured |
| A2 | Reviewer benefit and OCR/model quality unmeasured | QAD evaluation before readiness claim |
| A3 | Synthetic patient records only; staff/account data can be real PII | Local protection before invitations; new decision before patient records |
| A4 | One team, five users/two audits, 100 imports/day, 10k metadata | Load test before capacity claim |
| A5 | Hospital export/profile can be qualified later | Mandatory before operational pilot |
| A6 | Cloud provider/region/terms/cost and OCR/database container versions unresolved | Verify at the relevant later task; installed Python stack recorded in BUILD |
| A7 | Current design defaults remain reversible | Tests and reviewer evidence govern refinement |
| A8 | Yushin operates supervised evaluation | Confirm alert channel/availability before invitations |
| A9 | Offline means local server after dependency/image installation, without external runtime calls | Not an air-gapped installer or cross-device synchronization; final task independently blocks egress |

No further product approval is required to continue the already authorized tasks. External runtime or data-scope changes still require the applicable facts/authorization.

## 5. Decisions

| ID | Decision | Evidence class / revisit |
|---|---|---|
| D1 | Sentinel Claims audience name; sentinel-node technical slug | Accepted human decision |
| D2 | Adult medical inpatient scope and P01-P10 | Accepted baseline; PRD owns behavior |
| D3 | Synthetic patients, environment notice and export provenance | Human decision; explicit new authorization for real records |
| D4 | External FMD v3.0.1 at 4979fda, read-only | Never commit/push to engine repository |
| D5 | MIT project license and public repository | Project canonical |
| D6 | Local prototype precedes deployed evaluation A and operational pilot B | Human direction; later release gates retained |
| D7 | Owner resumed implementation and authorized project commits/branch on 2026-10-21 | Latest explicit instruction supersedes pause |
| D8 | Offline default; online inference requires explicit opt-in plus credentials | Agent implementation choice under offline-first instruction; tests in Task 1 |

## 6. Context exclusions

The old nightly/revenue proposal and old prototype plan are historical. Keep local research untouched. Scaffold is now committed, not a completed app; shared-token access and single-XML/chart assumptions remain to replace. Canonical requirements and active change govern.

## 7. Next actions

1. Task 3: immutable versioned bundles and private local originals.
2. Tasks 4-7: profile, complete workbench, correction events/revisions and guarded reports.
3. Tasks 8-10: local OCR, PostgreSQL packaging/recovery, then disconnected acceptance.

Task 1 is complete at `08b0c09`: dependency resolution restored; six offline tests RED to GREEN; 37 tests pass with one deprecation warning. This verifies the foundation, not the full prototype.

Task 2 is implemented: named CLI-provisioned accounts, encrypted privileged TOTP, expiring/revocable sessions, assignment and child-resource authorization. Twenty account scenarios and a real Chromium desktop/mobile login check pass. Login is working; the evidence workbench is pending. Default named mode denies old tokens. Explicit development migration mode remains available. Keep the local encryption key private and backed up; full PostgreSQL/recovery evidence remains Task 9.

Artifact plan: update STATE and draft product/system position; add BUILD and one CHANGE proposal/design/delta/tasks/verification set; engine generates INDEX/LOG and root build instructions. Do not regenerate the full suite.

## 8. Self-Check

- [x] Latest owner instruction, current branch, verified progress and remaining tasks recorded.
- [x] App verification is distinguished from future prototype, hosted and hospital gates.

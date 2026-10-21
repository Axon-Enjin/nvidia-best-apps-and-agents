# Project State: Sentinel Claims

**Project slug:** `sentinel-node`
**Owner:** Yushin
**Last updated:** 2026-10-21

## 1. Position

**Current milestone:** Shape, entered 2026-10-21. **Next milestone:** Implement, only after the owner explicitly resumes application work. Exit: build-ready design/contracts and implementation authorization.
**Current blocker:** Application work is paused by owner instruction. Documentation reconciliation is authorized; SCRUTINY is **PROCEED WITH FIXES**. No deployment or evaluation-ready result is established.
**Product:** Hospital PhilHealth reviewers compare prepared adult medical inpatient claims, coordinate corrections and record review before existing-system submission.
**Engagement:** Hospital workflow evaluation first; hackathon secondary. **Vault status:** none.

## 2. Active signals

| Signal | Evidence | Consequence |
|---|---|---|
| S1 / S2 / S4 | Approved UI, backend/auth/data and nontrivial workflow | PRD, DSD, SDD |
| S7 / S9 / S12 / S20 | Intended hosted release, named accounts, AI/provider API | QAD, CLR, AIA, OPS; contract/failure tests |
| S11 | Public repository README | Existing public entrypoint reconciled |
| S16 | Git history includes Nanashi and Carlos Jerico Dela Torre | L1 practices required when implementation resumes |
| S22 / S27 | Hackathon context and time box | Pitch deferred until demo preparation; no deadline readiness claim |
| S29 | Claims context and potential future health processing | CLR ?7 posture register |

Deliberate absences: no live deployment (S8), authorized actual patient records (S10), revenue/buyer/investment decision (S13?S15), or docs-cycle implementation (S5). No BUILD, commercial suite, SAD or RFC is justified now. Conventional reversible architecture does not require a new RFC. No external users are enrolled; QAD contains the pending reviewer study.

## 3. Operating frameworks

Milestones; no sprint commitment. Engineering **L1 required**, actual CI not evidenced; previous L0 assumption about one committer is obsolete. Subagents: none this cycle. Unfinished local scaffold is provisional, not a verified brownfield baseline.

## 4. Open assumptions

| ID | Assumption / uncertainty | Risk / owner / resolution |
|---|---|---|
| A1 | Build rate remains uncalibrated | Yushin; no date promise until measured |
| A2 | Net review benefit and OCR/model quality are unknown | Reversible scope; Yushin; QAD study/evals before readiness claim |
| A3 | Only synthetic patient records authorized; accounts can contain real PII | Yushin; CLR controls before invitations; new decision before real health records |
| A4 | One team, five users/two audits, 100 imports/day, 10k metadata and single-host deployment suffice | Reversible sizing; Yushin; load test and quota/price verification |
| A5 | Hospital export/profile can be qualified later | Yushin with eventual sponsor; mandatory before operational pilot |
| A6 | Provider endpoint/terms/region, OCR library, exact versions and budget remain unverified | Yushin; verify/pin before live calls/provisioning |
| A7 | SDD caps, typed entity sketch, DSD tokens and OPS thresholds operationalize accepted decisions | Reversible design defaults; Yushin; validate during implementation and tests |
| A8 | Owner can operate supervised evaluation | Yushin; confirm availability and actual alert channel before invitations |

No new preference answer is needed to finish authorized docs. These are evidence/deployment dependencies, not achieved facts.

## 5. Decisions

| ID | Decision | Evidence class / revisit |
|---|---|---|
| D1 | Audience name Sentinel Claims; technical slug retained | Human Decision, delegated baseline accepted 2026-10-21 |
| D2 | Adult medical inpatient pre-submission review, P01?P10 in PRD | Human Decision; scope changes propagate |
| D3 | Synthetic patient data only; one environment notice and export provenance | Human Decision; explicit new authorization before real records |
| D4 | External FMD v3.0.1 at commit 4979fda; no engine commits/pushes | Human Decision + verified checkout; AGENTS locates engine |
| D5 | MIT project license; public repo | Project Canonical; engine license is separate |
| D6 | Separate deployed evaluation A from operational pilot B | Accepted baseline; QAD/CLR define pending evidence |
| D7 | Application pause persists; docs and current-repo commit authorized | Owner instruction; resume only explicitly |

## 6. Context exclusions

Earlier nightly/headless revenue proposal, old prototype plan and October 12 empty framing are historical, not current requirements. Preserve research and unfinished app files. [PILOT-DECISIONS.md](../PILOT-DECISIONS.md) records accepted choices; PRD/DSD/SDD/QAD/CLR/AIA/OPS now own detailed requirements. Sample profiles never establish official schema compatibility.

## 7. Next actions

1. Owner resumes implementation when ready; then verify/pin build choices and assess scaffold against PRD without discarding local work.
2. Implement/check the vertical correction loop in [BUILD-CHECKLIST.md](../BUILD-CHECKLIST.md), then complete all release evidence.
3. Qualify hospital export/data arrangements only for operational pilot B; never infer them from sample evaluation.

Artifact plan completed for this documentation slice: IDEA/SCRUTINY reconciled; PRD/DSD/SDD specify accepted behavior; QAD/CLR/AIA/OPS define release evidence; STATE and engine-generated INDEX/LOG maintain position/history. Artifact status remains Draft pending implementation reconciliation; substantive scope is already accepted. No BUILD or pitch is generated during the application pause.

## 8. Self-Check

- [x] Position, decisions, signals, assumptions and exclusions reconciled.
- [x] Only triggered artifacts populated; tests/deployment/control outcomes remain pending.

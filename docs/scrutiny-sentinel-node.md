# IDEA Scrutiny Gate (SCRUTINY)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.3
**Owner:** Yushin, project owner
**Status:** Draft
**Last reconciled:** 2026-10-21
**IDEA:** [Idea brief](idea-sentinel-node.md)

## 1. Verdict

**Decision:** PROCEED WITH FIXES

**One-line rationale:** The owner settled the user, pain, scope and deliverable; no fatal contradiction is established, but workflow value and deployment readiness remain unproven.

This replaces the 2026-10-12 verdict based on empty framing. The owner subsequently resumed implementation on 2026-10-21, selecting the offline local prototype next. This verdict permits the defined build/evaluation work; it does not clear release gates.

Items carried forward:

- PRD ?8 and QAD ?7: measure benefit against manual/vendor-supported review, including import and correction overhead.
- PRD ?6 and SDD ?4: internal sample XML cannot establish hospital compatibility.
- SDD ?8, QAD ?7 and AIA ?4: validate evidence, OCR confirmation and bounded AI behavior.
- CLR ?1/?3/?7 and OPS: synthetic patient records only; prove account privacy and operations before release.
- PRD ?9: no delivery-date promise or completed deployment follows from the unfinished scaffold.

## 2. Claim & Reference Audit

**Coverage:** Claims extracted: 5; load-bearing: 5; verified: 1; unverified: 4; contradicted: 0. Product choices are decisions, not empirical claims.

| # | Category | Claim | Finding | Source | Severity if wrong |
|---|---|---|---|---|---|
| FC-1 | Problem | Hospital claims work includes checking supporting documents and preparing/transmitting a claim | Verified, limited to the published workflow | [QCGH Accounting Division](https://www.qcgh.org/accounting.html), checked 2026-10-21 | Significant |
| FC-2 | Solution | Coordinated source-linked corrections reduce net effort | Unverified; needs check | QAD reviewer study planned; no timing results | Significant |
| FC-3 | Technical | Printed-scan extraction and bounded comparisons meet targets | Unverified; needs check | QAD evaluation planned | Significant |
| FC-4 | Integration | A pilot hospital can provide usable exports | Unverified; needs check | No hospital/vendor profile obtained | Significant |
| FC-5 | Delivery | Complete scope meets capacity and time box | Unverified; needs check | No load test, deployed URL or calibrated build rate | Significant |

### 2.1 References Integrity

IDEA references the local decision record, workflow research, DSD and QAD. These exist after reconciliation and support provenance or planned behavior, not achieved outcomes. No reference establishes customer demand. QCGH's primary page resolves and supports FC-1, not a universal workflow or Sentinel's performance.

## 3. Gap Analysis

| # | Missing input | Needed by | Blocker or TBD |
|---|---|---|---|
| G-1 | Hospital export/schema and check applicability | SDD ?4, PRD ?8 | TBD for operational pilot |
| G-2 | Reviewer participation and measured benefit | QAD ?7 | TBD before evaluation-ready claim |
| G-3 | Model ID, terms, region, quota and hosting cost | SDD ?6/?8, CLR ?1 | TBD before provisioning; no purchase authorized |
| G-4 | Security, restore, workload and UI evidence | QAD ?6, OPS | TBD before release |

## 4. Assumption Stress-Test

**Load-bearing assumption:** Versioned evidence and correction coordination add value beyond existing submission software.

**Strongest argument against it:** Existing validation may catch the useful issues. Uploading and confirming OCR can duplicate work; false positives can create unnecessary requests.

**Does it hold?** At risk, not contradicted. Public workflows support plausibility, not discovery with the eventual hospital.

**Cheapest test:** Two reviewers perform counterbalanced manual/app sample tasks after a working vertical slice exists. Measure total effort and missed seeded issues. No external users are enrolled; QAD records the pending study without inventing validation results.

### 4.1 Audience / 10-second stress

| Check | Finding |
|---|---|
| Stranger hook | Pass: find a date conflict and close its source correction |
| Named user and pain | Pass: hospital reviewer before initial submission |
| Repeatable one-liner | Pass: compare prepared claims, coordinate corrections, record review |
| Why leave the status quo? | Weak until net effort improves |

**Audience verdict:** At risk until the reviewer study; specific enough to build and evaluate.

## 5. Feasibility & Scope

| Check | Finding |
|---|---|
| Minimum loop shippable | Plausible; implementation resumed, schedule still uncalibrated |
| Production-grade reachable | Conventional design; controls and restore still need proof |
| Honest cut line | Sample evaluation distinguished from operational pilot; no clinical or financial guarantee |

## 6. Risk & Regulatory Pre-flight

| Flag | Present? | Pulls in |
|---|---|---|
| User PII | Yes, planned named accounts | CLR ?1/?3 |
| Real health/children's data | No authorized patient data; future health use needs new decision | CLR ?3 |
| Regulated context | Yes, claims workflow | CLR ?7 |
| AI with untrusted input | Yes, uploaded documents | SDD ?8, QAD ?7, AIA |
| Security-critical paths | Yes, documents, roles, exports, deletion | SDD ?5, QAD abuse cases |
| Hosted release | Intended, not existing | OPS, CLR |

## 7. Blocking Questions

None for the authorized offline prototype. The previous owner pause is lifted by the 2026-10-21 instruction to continue the build. Release conditions remain unmet.

## Self-Check

- [x] Verdict matches findings; the verified claim has a primary source.
- [x] Claims, references, audience stress and downstream risks are recorded.

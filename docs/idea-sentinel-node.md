# Idea Brief (IDEA)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.3
**Owner:** Yushin, project owner
**Status:** Draft
**Last reconciled:** 2026-10-21
**Event / context:** Hospital workflow evaluation; hackathon submission is secondary.

## 1. The Spark

**One-line pitch:** Sentinel Claims helps hospital PhilHealth reviewers compare prepared claims with supporting records, coordinate corrections, and document review before submission through their existing system.

**Problem:** A reviewer must match several documents to a discharged encounter, compare their contents, chase source corrections, and check revised copies without losing prior decisions.

**Insight (why us, why now):** A versioned review workspace can keep the discrepancy, its source evidence, correction responsibility, and subsequent resolution together. Its value must be tested against existing vendor validation.

**Riskiest assumption:** Import and evidence-confirmation effort costs less than the checking and coordination work saved. This has not been measured with a hospital team.

## 2. Who It's For

**Primary user (named, specific):** The hospital PhilHealth claims reviewer responsible for prepared adult general medical inpatient ACR claims after discharge and before initial submission. No actual hospital or customer is claimed.

**Their moment of pain:** The claim and discharge summary show different discharge dates. The reviewer locates both passages, finds who can fix the originating record, and checks whether the replacement resolves the discrepancy.

**Success in their words:** Intended outcome, not a customer quotation: I can explain the discrepancy, hand off the correction, and finish the revised review with previous evidence intact.

## 3. Scope & Cut Line

| Capability | Core to the one thing? |
|---|---|
| Named roles, assignment, versioned bundle import and printed-scan OCR | Yes; establish who reviewed which sources |
| Coverage, deterministic checks and evidence-linked AI questions | Yes; expose gaps as well as findings |
| Correction responsibility, manual handoff, reimport and history | Yes; close the correction loop |
| Human final review record and deployed persistent application | Yes; the requested deliverable |

**If we only ship one thing:** Import a sample bundle, locate a date discrepancy at two source anchors, request correction, reimport the corrected bundle, and export the completed internal review with the original finding preserved.

**Explicitly out of scope (v0):** Submission, HIS writes, autonomous coding or clinical decisions, payment guarantees, signature authentication, live policy search, pediatric/maternity/surgical/outpatient/special-package coverage, and real patient records. Technical slug remains `sentinel-node`.

## 4. Success & Judging Criteria

**How we know it worked:** A deployed, persistent sample-data workflow meets [QAD](qad-sentinel-node.md). Behavior must be real even when records are fixed fixtures.

| Criterion | Required evidence |
|---|---|
| Correct completion | Deterministic fixture expectations and zero false finalization with unresolved required checks |
| Useful AI | Three pinned runs, each at least 90% precision and 80% recall on annotated synthetic discrepancies |
| Reviewer benefit | Two practicing reviewers, ten cases each; no increase in missed seeded issues and target 20% lower median active review time; import/handoff measured separately |
| Operational pilot | Separate gate: sponsor, qualified export profile, approved processing arrangements and reviewer validation |

All results remain unmeasured. Synthetic results cannot establish clinical accuracy or payer acceptance. Decision provenance is [PILOT-DECISIONS.md](../PILOT-DECISIONS.md); workflow evidence is [PILOT-WORKFLOW-RESEARCH.md](../PILOT-WORKFLOW-RESEARCH.md).

## 5. Concept Visuals

No approved concept image exists. The local walkthrough is historical explanatory material. [DSD](dsd-sentinel-node.md) specifies the queue and evidence workbench, not implemented UI.

## 6. Open Questions

| Question | Owner | Resolve by |
|---|---|---|
| Does the workbench save net effort? | Yushin | Supervised evaluation |
| Which hospital/vendor export can be qualified? | Yushin with eventual hospital reviewer | Operational pilot |
| Which provider endpoint, region, quota and preset are available? | Yushin | Before provisioning/live evaluation |

**Spike plan:** No disposable spike is needed for the current slice. The owner resumed implementation on 2026-10-21; build and evaluate the complete offline correction loop through the active change plan. Clinical/hospital value remains unmeasured.

## Self-Check

- [x] Specific user, pain, insight and minimum outcome replace old placeholders.
- [x] Cut line, unmeasured assumptions and decision provenance are explicit.

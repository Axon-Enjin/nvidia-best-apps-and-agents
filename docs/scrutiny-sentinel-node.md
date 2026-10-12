# IDEA Scrutiny Gate (SCRUTINY)

**Project:** Sentinel Node
**Date:** 2026-10-12
**Version:** 0.1
**Owner:** team owner
**Status:** Draft
**Last reconciled:** 2026-10-12
**IDEA:** [idea-sentinel-node.md](idea-sentinel-node.md)

---

## 1. Verdict

**Decision:** DO NOT BUILD YET

**One-line rationale:** Fatal flaw 2. The lock bar has no confirmed problem, no named user, and no concrete pain moment.

**If PROCEED WITH FIXES, items carried into the build:**

- None. The build stops until the team owner answers §7.

---

## 2. Claim & Reference Audit

**Coverage:** Claims extracted: 5; load-bearing: 5; verified: 4; unverified: 1; contradicted: 0.

| # | Category | Claim (from IDEA) | Finding | Source (required if Verified) | Severity if wrong |
|---|----------|-------------------|---------|-------------------------------|-------------------|
| FC-1 | Problem | The PhilHealth claims-auditor writeup is the product direction. | Unverified; needs check | README.md states it as the recommended build. The team owner has not confirmed it. | Fatal |
| FC-2 | Technical/Feasibility | The entry must run on Nebius Token Factory or Nebius AI Cloud and use at least one NVIDIA open model such as Nemotron. | Verified | HACKATHON.md section 4, retrieved 2026-09-28 | Fatal |
| FC-3 | Solution | The product name for this track is Sentinel Node. | Verified | README.md, 2026. The "(claims)" subtitle is not part of this claim. | Significant |
| FC-4 | Technical/Feasibility | The submission needs a public repo, an OSI license, and a working demo URL. | Verified | HACKATHON.md section 6, retrieved 2026-09-28 | Fatal |
| FC-5 | Technical/Feasibility | The submission deadline is Oct 30, 2026, 10:00 AM PT (Oct 31, 1:00 AM PHT). | Verified | HACKATHON.md section 1, retrieved 2026-09-28 | Significant |

### 2.1 References Integrity

| # | Reference | Backs claim | Resolves? | Supports it? | Finding |
|---|-----------|-------------|-----------|--------------|---------|
| R-1 | README.md, 2026 | FC-3 | Yes | Yes | Verified |
| R-2 | README.md, 2026 | FC-1 | Yes | Partly | Unverified |
| R-3 | HACKATHON.md, retrieved 2026-09-28 | FC-2, FC-4, FC-5 | Yes | Yes | Verified |

---

## 3. Gap Analysis

| # | Missing input | Needed by (doc) | Blocker or TBD |
|---|---------------|-----------------|----------------|
| G-1 | Named primary user | IDEA §2, later PRD | Blocker |
| G-2 | Concrete pain moment | IDEA §2 | Blocker |
| G-3 | Confirmed problem | IDEA §1 | Blocker |
| G-4 | The one product behavior to demo | IDEA §3 | Blocker |
| G-5 | Whether a UI exists | DSD, if a screen is required | TBD |

---

## 4. Assumption Stress-Test

**Load-bearing assumption:** The PhilHealth claims-auditor writeup is Sentinel Node.

**Strongest argument against it:** The team owner marked that writeup as an open question and said not to resolve it from the README.

**Does it hold?** At risk. Nothing in the repo proves the writeup is stale, and nothing in this session confirms it.

**Cheapest test:** The team owner confirms or rejects the direction. A code spike would not settle it. Effort is UNCALIBRATED.

### 4.1 Audience / 10-second stress

| Check | Finding |
|-------|---------|
| Stranger hook: who hurts and why, in 10 seconds, without slides | Fail. A stranger cannot tell what Sentinel Node does. |
| Named user and pain present in IDEA §2 | Fail. Both are [FILL]. |
| One-liner repeatable (not generic SaaS) | Fail. The name is repeatable. The job is not. |
| Why not keep coping with the status quo? | Fail. No confirmed pain. |

**Audience verdict:** Blocks build. Fatal flaw 2, a hollow lock bar.

---

## 5. Feasibility & Scope

| Check | Finding |
|-------|---------|
| "If we ship only one thing" is shippable in the window | The hackathon rules are shippable as constraints. The product behavior is [FILL], so the demo is not yet scoped. Effort is UNCALIBRATED. |
| Production-grade reachable (security, data, rollback) | Not started. No code in this repo. |
| Cut line honest, not hiding work | Yes. Application code, real personal data, and the unconfirmed direction are out of this slice. |

---

## 6. Risk & Regulatory Pre-flight

| Flag | Present? | Pulls in |
|------|----------|----------|
| Collects user data / PII | N until the direction is confirmed | CLR §1 and §3 if it becomes Y |
| Children, health, payment, biometric, or precise-location data | N until the direction is confirmed. Standing rule: synthetic data only. | CLR §3 if it becomes Y |
| Regulated activity (license, franchise, permit, sector rule) | N until the direction is confirmed | CLR §7 if it becomes Y |
| AI component with untrusted input or tools | Y. The submission must call an NVIDIA open model. | SDD §8.1, QAD, and AIA after the gate clears |
| Security-critical paths (auth, money, deletes) | N until the direction is confirmed | SDD §5 and QAD if it becomes Y |
| Public deploy | Y. The repo is to go public and the submission needs a demo URL. | OPS and CLR after the gate clears |

---

## 7. Blocking Questions

1. Team owner: is the PhilHealth claims-auditor direction Sentinel Node, or a stale description?
2. After that answer: who is the named user, what is the pain moment, and what single behavior must the demo show?

---

## Self-Check

- [x] Verdict matches the findings; DO NOT BUILD YET names a fatal flaw (1, 2, or 3)
- [x] Coverage line filled; every load-bearing claim has a row
- [x] No Verified row without a source
- [x] §2.1 audits every reference cited in the IDEA (or states there are none)
- [x] §4.1 filled, even in Quick Mode
- [x] §6 flags name the docs they pull in; regulatory flags route to CLR §7, not to §7 here
- [x] On PROCEED WITH FIXES, every fix names the doc it lands in

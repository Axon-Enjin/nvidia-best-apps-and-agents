# Project State: Sentinel Node

**Project slug:** `sentinel-node`
**Owner:** team owner
**Last updated:** 2026-10-12

---

## 1. Position

| Field | Value |
|-------|-------|
| **Current milestone** | Frame |
| **Entered on** | 2026-10-12 |
| **Exit condition** | The team owner confirms or rejects the PhilHealth claims-auditor direction, and the IDEA lock bar is filled with a real problem, user, and pain moment. |
| **Next milestone** | Decide |
| **Current blocker** | Direction is [FILL]. Scrutiny verdict is DO NOT BUILD YET. |
| **Owner of the next step** | team owner |

**What we are building, in one line:** Sentinel Node, the Best Apps and Agents entry. The product behavior is [FILL].

**Engagement type:** hackathon submission

**Vault status:** none

---

## 2. Active signals

Only signals that are true.

| Signal | True? | Evidence | Requires |
|--------|-------|----------|----------|
| S7 Release to users intended | yes | HACKATHON.md requires a working demo by Oct 30, 2026, 10:00 AM PT | QAD and OPS when the gate clears and a PRD exists. Not this slice. |
| S11 Public surface shipped | yes | README.md exists. The repo is to go public and be judged. | Keep the existing README. Do not replace it. |
| S12 AI/ML component ships in the product | yes | HACKATHON.md requires at least one NVIDIA open model (Nemotron) on Nebius Token Factory or AI Cloud | AIA after PRD, SDD, QAD, and CLR exist. Deferred. |
| S22 Audience presentation | yes | HACKATHON.md requires a judged demo video | PITCH after IDEA, PRD, and the release gate. Deferred. |
| S27 Time box | yes | Submission deadline in HACKATHON.md | No artifact |

**Deliberate absences:**

- S1: no UI in the repo. Whether Sentinel Node has a screen is [FILL], so no DSD.
- S2: no backend, data store, or auth in the repo, so no SDD this slice.
- S5: this cycle is docs only, so no BUILD.
- S8: no production deploy.
- S9 and S10: personal data and health data are not assumed. Synthetic data only. Both become open again if the direction is confirmed.
- S13: no confirmed revenue model, so no UES.
- S16: a second committer is not evidenced. Main dev is Yushin. Engineering stays L0.
- S23: no application code and no PRD, so this is not a brownfield change.
- S28: this is the team's hackathon repo, not an external repo.
- S30: the cheapest test of the open direction is the team owner's answer, not a spike.

---

## 3. Operating frameworks

| Dimension | Choice | Why |
|-----------|--------|-----|
| **Project management** | milestones | New idea with a fixed submission date. No sprint cadence is evidenced. |
| **Engineering maturity** | L0 | Default. No second committer and no repeated regressions. |
| **Subagents** | none | No repeated specialist spawn has happened. |

---

## 4. Open assumptions

| ID | Assumption | Risk if wrong | Reversible? | Owner | Resolve by |
|----|-----------|---------------|-------------|-------|------------|
| A1 | Build effort is UNCALIBRATED. No measured rate was supplied. | A guessed schedule would be fiction. | yes | team owner | when a measured rate exists |
| A2 | Sentinel Node has no UI until the direction says otherwise. | A required screen would add design work. | yes | team owner | with the direction answer |
| A3 | The product does not collect health or other personal data until the direction says otherwise. | A health-data product needs a different protection bar. Synthetic data only still stands. | yes | team owner | with the direction answer |

**Open questions for the user:**

1. Team owner: is the PhilHealth claims-auditor direction Sentinel Node, or a stale description?

---

## 5. Decisions

| ID | Question | Decision | Evidence class | Review when |
|----|----------|----------|----------------|-------------|
| D1 | What is the product name? | Sentinel Node | Human Decision | if the owner renames it |
| D2 | Is the PhilHealth claims-auditor writeup the product? | [FILL]. Not confirmed. Do not build on it. | Human Decision | team owner answer |
| D3 | What data may the docs and any later demo use? | Synthetic data only | Human Decision | if the direction is confirmed |
| D4 | Where does the doc engine live? | FMD v3.0.1, referenced, not copied into this repo | Project Canonical | on an engine upgrade |

---

## 6. Context exclusions

| Excluded | Reason | Where it lives now |
|----------|--------|--------------------|
| Pricing, market sizes, and health-system statistics in the research report | Direction is unconfirmed, so those figures are not product facts | `Hackathon-AI-Agent-Research.md` |

---

## 7. Next actions

1. Team owner confirms or rejects the PhilHealth claims-auditor direction.
2. Refill the IDEA lock bar from that answer and re-run Scrutiny.
3. Generate no suite docs while the verdict is DO NOT BUILD YET.

**Artifact plan for this slice** (only artifacts whose trigger fired):

| Artifact | Why it is justified now | Status |
|----------|-------------------------|--------|
| STATE | First run on a new project | done |
| IDEA | No Frame artifact existed, and the product name was captured | done |
| SCRUTINY | Required before any plan from the IDEA | done |
| INDEX | First artifacts were written to docs/ | done |
| LOG | First FMD action | done |

PITCH, QAD, AIA, OPS, and CLR wait. Their signals are true, and their needs are not met while the gate blocks.

---

## 8. Self-Check

| Check | Done |
|-------|------|
| Milestone and exit condition are current | [x] |
| Every listed signal has real evidence | [x] |
| Every assumption made this session is in §4 | [x] |
| Artifact plan contains no untriggered artifact | [x] |
| Context exclusions updated after any pivot | [x] |

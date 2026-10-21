# Sentinel Claims

A planned PhilHealth claim review workspace for hospital reviewers: compare prepared claims with supporting records, coordinate corrections, and document review before submission through the hospital's existing system.

**Current status:** Implementation is underway. The next milestone is a complete local sample-record workflow that works offline after installation. Reproducible setup and remote-inference guards are verified; the full review interface and workflow remain unfinished. Hosted deployment and operational hospital use require additional verification.

Start with the [product summary](PRODUCT.md), [experience guide](DESIGN.md), and [build checklist](BUILD-CHECKLIST.md). Contributors should read the [session handoff](HANDOFF.md) before making changes.

## Planned workflow

Import a versioned bundle ? inspect coverage and source-linked findings ? request a source correction ? import the revised bundle ? recheck ? export the named reviewer's record.

Initial scope is adult general medical inpatient claims before initial submission. Submission automation, clinical/coding decisions and reimbursement guarantees are excluded.

## Project context

This repository also holds the Best Apps & Agents track research for the Nebius x NVIDIA Global AI Hackathon. Hospital workflow readiness takes priority over prize-specific features.

| Document | Purpose |
|---|---|
| [Product decisions](PILOT-DECISIONS.md) | Accepted decisions and their rationale |
| [Workflow research](PILOT-WORKFLOW-RESEARCH.md) | Hospital process evidence and its limits |
| [Event reference](HACKATHON.md) | Recorded rules and dates; recheck official rules before submission |
| [Sponsor context](ORG.md) | Original sponsor background |
| [Research prompt](PROMPT.md) | Original research request |
| [Opportunity research](Hackathon-AI-Agent-Research.md) | Historical proposals, not the current product specification |

The earlier nightly headless auditor, market estimates and revenue positioning are historical hypotheses. They do not establish capability, customer demand or measured outcomes.

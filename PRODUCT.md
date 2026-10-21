# Sentinel Claims

Updated: 2026-10-21. The owner approved proceeding with the recommended product changes and FMD reconciliation. This summary replaces the earlier implementer proposal. Application development is still paused. The accepted baseline has been reconciled with the external v3.0.1 engine.

The detailed accepted baseline is [PILOT-DECISIONS.md](PILOT-DECISIONS.md), including its SAMPLE-ADULT-MEDICAL-1 checklist and release criteria. [PILOT-WORKFLOW-RESEARCH.md](PILOT-WORKFLOW-RESEARCH.md) contains the hospital workflow evidence. The canonical [product requirements](docs/prd-sentinel-node.md) now own detailed behavior and P01?P10; [design](docs/dsd-sentinel-node.md), [architecture](docs/sdd-sentinel-node.md) and [evaluation](docs/qad-sentinel-node.md) describe delivery and acceptance. This file remains a concise entrypoint.

## Purpose and priority

Help hospital PhilHealth claims reviewers compare prepared claims with supporting records, coordinate corrections, and document review before submission through their existing hospital system.

Hospital pilot readiness leads product decisions. The required outcome is a functional deployed application. A deployed evaluation with synthetic records and operational use of actual hospital records have distinct entry criteria.

## First-release scope

One hospital claims team; adult general medical inpatient ACR claims after discharge and before initial submission. Reviewers, supervisors, and administrators have named accounts and explicit permissions. Other claim categories, returns/appeals, and multi-hospital operation are later work.

The workflow is: import a versioned document bundle, confirm membership and coverage, inspect evidence-linked findings, assign corrections, import revised sources, rerun checks, and record **Ready for final submission review**. Submission remains in the hospital's existing system.

Required capabilities:

- Review queue, assignment, supported input profiles, coverage reporting, and private source-document viewing.
- Multiple documents per version, supported readable XML, PDFs, and printed-scan OCR with confirmation of critical extracted fields.
- Deterministic consistency checks and a tested live Nemotron-assisted comparison path, with explicit errors and manual-review fallback.
- Evidence anchors, reasoned finding dispositions, manual signature-presence review, correction ownership/handoff, and revision comparison.
- Persistent, attributable review history; stale-review protection; printable/CSV review exports; and operational metrics calculated from actual case events.
- Deployed HTTPS access, durable processing, access controls, backups/restoration, and documented local setup.

## Data and evidence

Synthetic patient records remain the authorized boundary. Fixed sample records use the normal workflow; content-derived findings and saved actions must be real. Identify the evaluation environment and the provenance of exports without repeated "static data" labels.

The internal sample profile exercises the complete workflow; it is not an official eClaims schema or proof of hospital compatibility. Missing inputs, unsupported formats, failed checks, and clinical uncertainty remain distinguishable. No-finding results only describe completed checks. New source/rule versions invalidate affected review decisions.

## Delivery baseline

Retain Python/FastAPI, SQLAlchemy, and the small browser client. PostgreSQL is the standard local Docker and deployed database. Use separate web/worker processes, a durable database queue, and private object storage with a local filesystem adapter for development. SQLite can remain as optional lightweight development support.

Target a hosted CPU container deployment on Nebius AI Cloud with remote Nemotron inference through Token Factory. Region, account capacity, exact model/preset, and cost must be checked before provisioning. Planning targets are five concurrent reviewers and 100 imported cases/day; performance and recovery targets are requirements, not measured results.

## Success and boundaries

The first demonstrable success is a real content-derived discrepancy that a reviewer inspects, routes for correction, and verifies against a revised source, with the prior evidence and decisions preserved across sessions and restarts.

The accepted baseline defines 40 synthetic evaluation bundles, deterministic/evidence checks, AI precision/recall targets, failure recovery, and comparative reviewer evaluation. Operational hospital use additionally requires a qualified hospital export profile, appropriate processing/hosting arrangements, and validated workflow fit. No deployment, benchmark, actual hospital partnership, or interoperability approval is currently established.

Direct claim submission, autonomous clinical/coding decisions, source-system write-back, signature-authenticity certification, and reimbursement guarantees are excluded. Preserve the provisional code until implementation is explicitly authorized and it can be assessed against this baseline.

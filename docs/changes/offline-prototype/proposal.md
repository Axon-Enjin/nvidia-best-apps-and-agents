# Proposal: Offline first working prototype

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Status:** In Progress
**Owner:** Yushin

## Intent

Complete the hospital review and correction workflow locally before introducing hosting or remote-model dependencies.

## Scope

The owner explicitly resumed implementation on 2026-10-21 and requested a checkpoint commit, a new build branch, and written implementation steps. The scaffold is preserved at `e8c0ace`; work continues on `feat/offline-prototype`.

- Restore reproducible setup and make offline the default runtime mode.
- Build named local accounts, role/assignment controls, versioned bundles, coverage and deterministic checks.
- Complete evidence review, correction handoff, revised-source review, guarded completion and local reports.
- Include locally installed printed-scan OCR, local persistence, restart recovery and backup/restore before calling the first prototype complete.
- Verify the complete browser workflow with external networking blocked.

## Out of scope

Cloud provisioning, remote inference as a prerequisite, browser-to-cloud synchronization, offline edits replicated between separate installations, real patient records, local LLM hardware provisioning, payer submission and clinical decisions.

This is a locally hosted application, not a service-worker cache of a hosted site. Browsers still need access to the local app/server; all app assets and data processing stay local. Installation may download dependencies and images. A separate air-gapped installation package is later work.

## Approach

Retain FastAPI/SQLAlchemy and the existing worker. PostgreSQL remains the standard local/container target; the existing SQLite path remains a single-machine development convenience, with no claim of PostgreSQL concurrency verification. Use local private file storage through an adapter compatible with later object storage. Offline mode disables provider inference at API, worker and adapter boundaries. Narrative review uses the already-approved manual comparison plus supervisor acknowledgement; it never masquerades as AI completion.

Full deployed-evaluation and operational-hospital gates remain in the PRD/QAD. This prototype is an intermediate milestone, not a downgrade of the eventual release requirements.

## PRD trace

| Feature | Prototype contribution |
|---|---|
| PRD-F1 | Local named accounts, privileged MFA, assignment and authorization |
| PRD-F2 | Local immutable bundle/source storage, import and printed OCR |
| PRD-F3 | P01-P10 and explicit unavailable AI/manual review |
| PRD-F4 | Correction ownership, handoff, revision and append-only events |
| PRD-F5 | Current-version completion, reports and event metrics |
| PRD-F6 | Reproducible local runtime, durable worker and recovery |

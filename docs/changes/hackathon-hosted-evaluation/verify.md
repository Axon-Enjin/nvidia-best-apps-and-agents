# Verify: Hackathon hosted evaluation

**Date:** 2026-10-23
**Overall:** NOT STARTED (S1 records the decisions; no feature is implemented)

## Completeness

- OPEN: all tasks in [tasks.md](tasks.md) except S1 are unstarted. S1 is complete when this record validates, the build guide is materialized and one docs commit exists.
- OPEN: the seven gates (CI; server with Linux OCR; scripted live check; restore drill; AI safety AI-02 to AI-09; spending stop; uptime alert) have no evidence yet.

## Correctness

### Provisioning check, 2026-10-23 (read-only, before S1)

- PASS: Nebius CLI signed in as the owner through the Google federation; tenant `tenant-e00kcdt6g6axsxyzw5` is `ACTIVE`, created 2026-10-22; default project `project-u00ef29xkc00crdak3t6x4`, region `us-central1`.
- PASS: platform `cpu-d3` offers preset `2vcpu-8gb`; public image `ubuntu24.04-driverless` (0.2.1108, recommended for `cpu-d3`) is `READY`; the default network exists; no instances, no serverless AI jobs or endpoints exist.
- UNKNOWN: AI Cloud billing. The CLI has no account-billing status command, and quota listings omit limit values, so it is not known whether a VM can be created or whether a payment method is on file. Owner check at console.nebius.com is still open (stop before entering a card).
- UNKNOWN: Token Factory account. `NEBIUS_API_KEY` is empty in `.env`, so no Nemotron probe has run. The Philippines billing blocker is unchanged.
- PASS: `TAVILY_API_KEY` is set in `.env` (value not read).
- FINDING: the app's default model setting is `nvidia/nemotron-3-super-120b-a12b` (`apps/api/src/sentinel/config.py:68`); the earlier handoff wrote it without the `nvidia/` prefix. Public pages list that ID with the prefix and give indicative prices of $0.30 per million input tokens and $0.90 per million output tokens. No Nebius page confirms the Nano ID or its price; `nvidia/nemotron-3-nano-30b-a3b` is an assumption until the probe lists it.

## Coherence

- OPEN: PRD, SDD, AIA, QAD, OPS, CLR, DSD, `PRODUCT.md`, `HACKATHON.md` and the older change records still describe the offline prototype. They move in S19.

## Review quality

- N/A until implementation starts.

## Findings

- WARNING: the Token Factory account is the main schedule risk; last safe day for a working key is about Oct 26.

# Operations & Observability Runbook (OPS)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin
**Status:** Draft
**Last reconciled:** 2026-10-21
**SDD:** [System design](sdd-sentinel-node.md)
**PRD:** [Requirements](prd-sentinel-node.md)

Target runbook for PRD-F6. No hosted URL, configured monitoring destination, running backup or production incident exists in the evidence. Commands and alert delivery must be exercised before release.

## 1. SLOs & SLIs

| SLI | Target | Planned measurement | Breach action |
|---|---|---|---|
| Availability during supervised evaluation | Detect two consecutive failed minute probes; no contractual SLA | HTTPS readiness probe outside host | Alert Yushin; stop session and diagnose |
| Queue/case interaction p95 | <2 seconds with five users/two audits | Request duration histogram and browser checks | Inspect database/storage; pause imports if overloaded |
| Audit processing p95 | Text <2 minutes; scans <5 minutes, queue wait separate | Job created/leased/completed timestamps by type | Inspect worker/provider; communicate queued state |
| Data recovery | RPO 24 hours, RTO one business day | Coordinated backup manifest and timed restore drill | Suspend new imports on stale backups |
| Integrity | Zero false completion or wrong-version evidence | Guardrail failures, QAD and user reports | Stop finalization, investigate, follow rollback source |

These are targets. Measurement sources must be wired and verified.

## 2. Observability; Logs, Metrics, Traces

| Pillar | Planned tool / content | Retention |
|---|---|---|
| Logs | Structured JSON from web/worker; safe error category, duration, opaque request/job IDs | 30 days |
| Metrics | Request/job durations, failures, queue age, retries, backup age, PRD events, provider usage | 90 days evaluation |
| AI traces | Metadata only: model/prompt versions, token counts, provider request ID, result category | 30 days; no raw prompts or documents |
| Audit | Restricted actor/action/entity/time and review history | 90 days evaluation; expiry/deletion recorded |

Admin diagnostics show queue health, failure classes, backup age and cost/budget state. Correlate request_id ? job_id ? run_id without printing patient/account content. No raw document text, extracted values, session tokens, passwords, model prompts/responses or signed URLs in logs. Account-linked audit is personal data and remains access controlled. Monitoring backend and alert channel are selected/configured during deployment, not claimed installed.

## 3. Alerting & On-Call

| Alert | Condition | Severity | Named owner | Channel |
|---|---|---|---|---|
| App unavailable | Two failed minute probes | P1 | Yushin | Operator-controlled channel TBD and test delivery before release |
| Backup stale | No verified successful checkpoint in 26 hours | P1 | Yushin | Same verified channel |
| Worker stalled | Oldest runnable job >5 minutes with no healthy worker heartbeat | P1 during evaluation | Yushin | Same verified channel |
| Integrity/access incident | Any false completion, wrong-case source or unauthorized disclosure report | P0 | Yushin | Immediate direct operator contact |
| Inference failures/budget | Three consecutive provider failures or configured spend ceiling reached | P1 for AI-assisted path | Yushin | Same verified channel; pause inference |

Single-operator, best-effort supervised evaluation; no staffed 24/7 service is claimed. Confirm Yushin's availability for each reviewer session and provide an actual contact method before inviting participants. No messages were sent as part of writing this runbook.

## 4. Incident Response

Acknowledge and record time, affected versions and safe correlation IDs. Contain first: revoke affected sessions, pause imports/inference/finalization as appropriate, isolate suspected uploads and preserve access-restricted evidence. Communicate impact and next update to participating reviewers through the agreed channel. Diagnose only after containment.

For personal-data exposure, determine scope/recipients, preserve evidence, involve the accountable operator and promptly notify affected users as appropriate; assess applicable notification duties using current official guidance. Do not invent a universal statutory deadline or paste patient details into an issue.

**Rollback:** [PRD ?9](prd-sentinel-node.md#9-implementation-plan) owns triggers and mechanism. Packaging must provide and rehearse its executable command before release.

Planned runtime controls: pause imports, disable new inference, pause finalization, revoke sessions and restrict the application to read-only. Admin changes are audited; disabling AI leaves failed/not-run coverage visible and requires the defined manual path. No flag silently loosens completion rules.

Verify recovery with permissions, source hashes, version consistency and a sample correction loop. Write a project postmortem for every P0/P1 within 48 hours; attach corrective actions and test evidence. No postmortem artifact is needed before an incident exists.

## 5. Routine Operations

- Before each evaluation session: health check, backup age, worker/provider reachability, account/assignment check, sample provenance and support contact.
- Daily: encrypted coordinated DB/object backup; keep seven recovery points and verify manifest/hash counts. Never regard upload success alone as restore proof.
- Restore drill: before first release and after material storage/schema changes; restore in isolation, reconcile pending jobs and deletion ledger, test roles/history/evidence and measure RPO/RTO.
- Retention: evaluate 90-day expiry, revoke exports/access where applicable, remove primary copies and let backups expire; maintain deletion evidence until no affected backup remains.
- Secrets: rotate on exposure or personnel change and review quarterly. Use environment/secret storage; never repository values.
- Dependencies: scan at packaging; prioritize exploitable critical fixes before next external session. Re-run affected QAD flows.
- Cost: inspect daily during evaluation; configure an explicit monetary ceiling from the approved budget before live inference. Provider quota and price remain external facts to verify.
- Certificates/domain: use automatic renewal with expiry monitoring; ownership and actual domain are not yet configured.
- Hospital pilot: replace sample-only retention/recovery assumptions with approved hospital values before using actual records.

## Self-Check

- [x] Targets, measurements, incident procedure, named operational owner and rollback reference specified.
- [ ] Monitoring and alert channel wired, alert received, backup restored and deployment/rollback rehearsed.

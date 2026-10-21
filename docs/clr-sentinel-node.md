# User Protection & Regulatory Posture Register (CLR)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin, project owner
**Status:** Draft
**Last reconciled:** 2026-10-21
**PRD:** [Requirements](prd-sentinel-node.md)
**SDD:** [System design](sdd-sentinel-node.md)

Planning register, not a privacy policy, legal opinion or compliance certification. Postures below apply the owner's delegated decisions and standing synthetic-data boundary; no hospital approval or external appointment is implied.

## 0. Target Markets

Philippines hospital reviewers are the intended audience. EU/UK/California markets are not targeted. The future HTTPS site may be globally reachable; geographical reach is not equivalent to a proven exemption. Accounts are invitation-only and imports restricted to supervised synthetic evaluation. Reassess before accepting overseas users or hospital records.

## 1. Data Inventory / Record of Processing

| Activity | Purpose / subjects | Categories | Recipients / transfer | Retention / basis |
|---|---|---|---|---|
| Accounts and sessions | Named reviewer access | Name/identifier, email if needed, role, protected credentials, session/MFA metadata | App operator and host; actual host region TBD | Evaluation lifecycle, maximum 90 days; sessions expire/revoke earlier. Lawful basis/notice must be documented before inviting real accounts. |
| Sample uploads and extraction | Exercise review workflow | Fictional patient forms, text and confirmed values | Private host/storage, OCR worker | 90 days; authorized synthetic fixtures only |
| Model comparisons | Evidence-linked questions | Minimal synthetic excerpts/anchors | Token Factory; exact region, retention and training terms unverified | App results 90 days; provider terms must be recorded before use |
| Review/history/exports | Accountability and correction tracking | Actor-linked decisions, task recipient, versioned report | Assigned reviewers, supervisors, authorized export recipients | 90 days; real staff identifiers are personal data even with fictional patients |
| Operations and security | Detect failures and unauthorized access | Opaque IDs, action/time, durations, necessary access metadata | Restricted operator/hosting services | 90 days for evaluation audit/metrics; diagnostic logs 30 days; no raw documents/prompts/secrets |
| Backup/restore and deletion | Recover and enforce expiry | Encrypted coordinated snapshots, minimal deletion ledger | Private backup storage/operator | Seven daily points; deletion ledger retained until affected backups expire |

No patient health data, children's records, biometrics, payment cards, precise location, advertising IDs or behavioral tracking is authorized. Uploaded scans can contain such data accidentally; restrict/quarantine imports and suspend processing on discovery. A synthetic-data checkbox alone is insufficient.

For future health processing, document controller/processor roles, purpose/lawful basis, notice/consent where required, recipient/region, retention and hospital instructions before changing the data boundary. Current sample policy is not a hospital retention policy.

## 2. Obligations Awareness

The [NPC IRR](https://privacy.gov.ph/implementing-rules%20regulations-data-privacy-act-2012/) addresses security and processor safeguards; outsourcing arrangements and processing location need attention. Reviewed 2026-10-21 through official indexed content; direct fetch returned 403 on the latest retry. This supports review of actual arrangements, not a claim those arrangements exist.

The [NPC advisory register](https://privacy.gov.ph/pips-and-pics/advisories-circulars/) lists Advisory 2024-04 on AI systems processing personal data. Exact applicability to eventual processing remains to be assessed; AIA records retrieval limits. PhilHealth submission certification and schema obligations belong to a future integration assessment; Sentinel v1 does not submit claims.

Foreign privacy/AI obligations are unassessed beyond the stated target scope; revisit on geographical/data expansion. No invented exemption or blanket statutory deadline is used.

## 3. User-Protection Bars

| Flag | Present? | Bar | Met? / evidence |
|---|---|---|---|
| Personal account/staff data | Planned | Minimal collection, notice, access/correction/deletion path, least privilege and secrets outside code | No; PRD-F1/PRD-F6, QAD AB-01/AB-06 pending |
| Breach risk | Planned | Detect, contain, preserve evidence, assess and promptly notify affected users; evaluate applicable legal duties | No; OPS incident drill pending |
| Patient health data | Not authorized | For any future use: approved purpose/permission, encryption, logged access, deletion and human oversight | Not demonstrated; operational pilot blocked until authorized and evidenced |
| Children/payment/location/ad-tech | No | Do not collect; revisit if scope changes | Excluded by scope, not tested detection |
| Benefit-related review influence | Planned | Human decision, reason and supervisor dispute/reopen path; no payer decision | No; PRD-F3/PRD-F4/PRD-F5 tests pending |
| Untrusted uploads/model text | Planned | Quarantine, bounded parsing, escaped output, source validation | No; SDD ?5/?8 and QAD abuse/AI cases pending |

No present protection bar is marked met merely because it is specified.

## 4. Terms of Use / EULA Readiness

Evaluation terms, acceptable use, privacy notice, account support/deletion contact, liability/dispute terms and content-processing permission are not drafted or published. MIT source license is not an application privacy policy or hospital processing agreement. No paid tier, app store or payment terms apply. Operator prepares these before external account invitations; seek qualified review for actual hospital arrangements.

## 5. IP and Asset Readiness

MIT is present for this project. Dependency/model/OCR licenses and an SBOM must be checked against pinned versions before distribution. System fonts require no hosted font assets. No approved logo, trademark clearance or hospital branding license is claimed. Sample marks are fictional; do not imitate real signatures.

No training/fine-tuning is planned. Provider base-model provenance and runtime terms remain to be recorded. Do not send source records to unrelated analytics/training systems. Private application routes require auth and no indexing; crawler directives cannot substitute for authorization. Contributor assignment status is unknown; revisit before commercialization.

## 6. App Store / Platform Compliance

No mobile store submission. Hosting and inference account terms remain a live-deployment dependency. If submitting to the hackathon, recheck current rules and supply only sample-data access.

## 7. Regulatory Posture Register

| ID | Obligation / relevance | Posture and rationale | Exposure / evidence limit | Owner and date | Revisit / fallback |
|---|---|---|---|---|---|
| CLR-P1 | PH personal-data handling for accounts/staff events | COMPLY: minimize, document basis/notice, secure access and support rights | Breach, complaints and potential legal consequences; exact applicability/penalties not assessed | Yushin, 2026-10-21 | Before invitations; disable affected access if protection fails |
| CLR-P2 | Host/inference processor terms, location and safeguards | COMPLY: record actual recipients and terms before sending permitted content | Unapproved disclosure/transfer risk; account terms unknown | Yushin, 2026-10-21 | Before provider activation or region change; stop inference/import |
| CLR-P3 | Hospital health-record handling and claims-system integration | DEFER for sample-only scope; no real-data processing or submission now | No real-record exemption inferred; legal/contractual and patient harm exposure need assessment | Yushin, 2026-10-21 | Before B or any actual patient record; quarantine and return/delete under approved instructions |
| CLR-P4 | AI processing of personal data, NPC Advisory 2024-04 | COMPLY with applicable transparency/accountability protections; complete applicability review before real-data AI | Advisory exists; exact full-text obligations not fully verified this retry | Yushin, 2026-10-21 | Before data-scope/model/provider changes; keep synthetic-only/manual fallback |
| CLR-P5 | Foreign privacy and AI obligations | DEFER: no targeted overseas rollout; applicability still open for reachable site/accounts | No safe-harbor claim; reassess actual users and deployment facts | Yushin, 2026-10-21 | Before overseas enrollment/marketing; restrict invitations |
| CLR-P6 | PH registration/officer and organizational paperwork, where applicable | COMPLY: determine applicable registration/accountability duties before external operation | Thresholds and legal operator identity unresolved; not assumed exempt | Yushin, 2026-10-21 | Before external evaluation or entity change; delay invitations while protection responsibilities are unset |

No CONTEST posture or intentional unlawful operation is selected. This register does not price or accept personal criminal exposure; no such liability determination has been made. A future decision involving that exposure requires a specifically identified accountable founder and qualified assessment. Paperwork questions do not stop synthetic-only development; unmet user-protection bars prevent release.

## Self-Check

- [x] Data activities, retention, boundaries and owner/posture/revisit entries recorded.
- [ ] Actual provider terms, lawful-basis assessment, notices and protection evidence completed.

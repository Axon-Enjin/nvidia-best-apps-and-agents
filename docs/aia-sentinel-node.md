# AI Assurance Dossier (AIA)

**Project:** Sentinel Claims
**Date:** 2026-10-21
**Version:** 0.1
**Owner:** Yushin
**Status:** Draft
**Last reconciled:** 2026-10-21
**PRD:** [Requirements](prd-sentinel-node.md)
**SDD:** [System design](sdd-sentinel-node.md)
**QAD:** [Evaluation plan](qad-sentinel-node.md)
**CLR:** [Protection register](clr-sentinel-node.md)

Assurance plan, not certification. No evaluation result is recorded as achieved.

## 0. Trigger and Scope

PRD-F3 uses AI to propose evidence-linked narrative discrepancy questions. PRD-F2 supplies confirmed extraction; PRD-F4 and PRD-F5 retain human disposition and completion. The boundary is one current synthetic case, with no tools, source mutation, submission or eligibility decision. Future real-data use could affect benefits-related work and requires the separate operational gate. No definitive statutory risk classification is asserted.

## 1. Model / System Card

### 1.1 Intended use

Assist adult medical inpatient pre-submission document comparison for named hospital reviewers. Patients could be affected in a future authorized pilot; current patient records are fictional. Prohibited uses: diagnosis, coding/upcoding, eligibility/benefit decisions, medical-necessity assertions, submission and claims that absent supporting text proves absent care.

Reviewers inspect evidence, decide findings and finalize. Supervisors resolve disputes and acknowledge manual fallback. Authoritative source corrections remain with hospital staff.

### 1.2 Model(s) and data

| Stage | Identifier / version | Role / data |
|---|---|---|
| OCR | Not selected or pinned | Printed sample scans; critical values require source confirmation |
| Comparison | Nemotron 3 Super family via Token Factory; exact endpoint/model/config not pinned | Current-version synthetic excerpts with page/field anchors |
| Deterministic validation | Versioned sample profile P01?P10 | Contract/coverage/consistency and output evidence checks |

No fine-tuning or training dataset is planned. Base-model provenance/license and account-specific data terms must be recorded before live evaluation. The 40-bundle evaluation set is specified in QAD but not yet created.

Runtime sources are untrusted data. Validate bounded JSON, allowed check IDs and evidence against actual current sources. Invalid output fails the comparison; it does not become a finding or a success. Provider retention/training terms and region remain unverified for the selected account; only synthetic content is authorized.

### 1.3 Limitations and performance caveats

Quality targets are unmeasured. English first; mixed-language, handwriting, ambiguous OCR and unknown schemas cannot receive implicit automated coverage. Plausible explanations can still be wrong. Provider errors, context limits or missing source content require visible incomplete status. Manual P07 comparison plus supervisor acknowledgement is allowed while the automated result remains failed/not run. Synthetic performance does not establish hospital fit, clinical accuracy or payer acceptance.

## 2. NIST AI RMF Risk Register

Mapping uses the voluntary [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) and [GenAI Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), checked 2026-10-21. The table is our application of the framework, not a NIST assessment. Likelihood is unmeasured; all controls remain open until tested.

| Risk ID | Risk | Function / GenAI category | Severity | Mitigation | Eval | Owner / status |
|---|---|---|---|---|---|---|
| AIA-R1 | Embedded instructions change behavior | Map/Manage; Information Security | High | SDD ?8.1, no tools, schema/evidence boundary | AI-04/AI-07 | Yushin / Open |
| AIA-R2 | Invented mismatch or evidence | Measure/Manage; Confabulation | High | SDD ?8.1, exact anchors and human disposition | AI-01/AI-03 | Yushin / Open |
| AIA-R3 | Cross-case or account disclosure | Govern/Manage; Data Privacy | High | SDD ?5/?8, one-case context, minimized logs | AI-06 | Yushin / Open |
| AIA-R4 | Reviewer over-trusts automation | Map/Measure; Human-AI Configuration | High | PRD-F3/PRD-F5 explicit coverage and human completion | AI-02/AI-05, S-05 | Yushin / Open |
| AIA-R5 | Unsafe rendered output | Manage; Information Security | High | SDD ?5/?8.1 escaping and output validation | AI-08 | Yushin / Open |
| AIA-R6 | Provider limits, drift or outage | Govern/Manage; Value Chain and Component Integration | Medium | SDD ?8 caps/pins, explicit failure/manual path | AI-09, S-03 | Yushin / Open |

Yushin reviews this register before every model/prompt/extractor/rule change and after any harmful output. No acceptance of residual risk overrides a failed protection bar.

## 3. SMACTR Self-Audit

| Stage | Evidence | Done? |
|---|---|---|
| Scoping | PRD ?6/?7 and this ?0/?1 | Documented |
| Mapping | SDD ?2/?8 trust boundaries | Design only; implementation pending |
| Artifact collection | This card and register | Partial; provider terms, pinned versions and dataset absent |
| Testing | QAD ?3/?7 | Not run |
| Reflection | Safety bars below | Release not approved |

Residual risk: source errors, OCR uncertainty and reviewer automation bias can persist even with exact citations. Measure misses, false positives and user effort; reduce scope if the evaluation fails. Full source checking by a human remains necessary.

## 4. Cross-links and Escalation

Architecture/control source: SDD ?8/?8.1. Test evidence source: QAD. Data/terms/posture source: CLR ?1/?7. Document instructions never override the application task; no retrieval or tool execution authority is granted by uploaded text.

| Flag | Present? | Required bar | Met? |
|---|---|---|---|
| Benefits-related review influence | Intended | Meaningful human decision, evidence and supervisor appeal/reopen path | No, tests pending |
| Automated significant-effect decision | Prohibited | No such authority; reject submission/mutation outputs | Not yet demonstrated |
| Health-sensitive inference | Future use only; samples now | Approved data purpose/permission, conservative coverage and human fallback | No real-data approval |
| Unresolved provider/data provenance | Provider terms/version incomplete | Resolve terms/version; remove unapproved data | No |
| Untrusted input reaches reviewer UI | Yes | Label as data, validate evidence/output, pass red-team evaluations | No |

Any applicable unmet bar prevents release. On suspected leakage or false ready state: pause inference/finalization, preserve minimal evidence, escalate to Yushin and follow OPS. Never silently replace failed output with a canned demonstration. Regulatory posture references: CLR-P2, CLR-P3, CLR-P4 and CLR-P5.

## 5. Regulatory Awareness

Checked 2026-10-21; applicability is provisional and depends on real deployment facts.

| Reference | Finding and limit | Posture |
|---|---|---|
| [NPC Advisory 2024-04](https://privacy.gov.ph/pips-and-pics/advisories-circulars/) | Official register confirms guidance for AI processing personal data. Full PDF returned 403 on this retry; no detailed obligation is claimed newly verified. | CLR-P4; complete full-text review before real-data AI |
| [DOST NAIS-PH account](https://www.dost.gov.ph/knowledge-resources/news/86-2025-news/3989-dost-builds-on-) | Primary source describes ethics/policy as part of national strategy; not a product certification | Voluntary alignment; no invented license duty |
| NIST AI RMF / GenAI Profile | Voluntary organization of risk/control evidence | N/A regulatory posture |
| ISO/IEC 42001 | No certification sought or claimed; no conformance assessment performed | N/A this slice |
| [European Commission AI Act timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) | Commission lists general application from 2 August 2026 and exceptions. No EU rollout or classification assessed here; do not copy a stale generic 2026?2027 schedule into launch claims. | CLR-P5; reassess before overseas expansion |

## Self-Check

- [x] Intended use, limits, traceability, risks and control/eval links documented.
- [ ] Model/version/terms, testing evidence and all applicable safety bars completed.

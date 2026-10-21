# Sentinel Claims: delegated product decisions

Current update, 2026-10-21: the owner has resumed implementation and requested an offline first working prototype. The [active implementation plan](docs/changes/offline-prototype/tasks.md) governs the build. Pause references in the dated decision history below describe the earlier documentation stage and are no longer the current instruction. Scope and real-data boundaries remain in force.

Date: 2026-10-21. Status: accepted product baseline. After delegating the decisions and receiving the report, the owner instructed: "proceed with the FMD reconciliation. Proceed with the changes that you recommend to the earlier proposal, then write or populate the FMD". This authorizes adopting the recommended product/experience changes and reconciling documentation. Application development remains paused. These decisions are not claims about completed software, hospital approval, or measured performance.

This dated decision record has been reconciled into the canonical [product requirements](docs/prd-sentinel-node.md), [design](docs/dsd-sentinel-node.md), [system design](docs/sdd-sentinel-node.md), [test plan](docs/qad-sentinel-node.md), [protection register](docs/clr-sentinel-node.md), [AI assurance](docs/aia-sentinel-node.md) and [operations plan](docs/ops-sentinel-node.md). Those artifacts own detailed requirements. This record preserves the accepted rationale; it is not proof of implementation or deployment. The external FMD v3.0.1 engine is now available and remains read-only.

## 1. Decisions already made by the owner

- Hospital pilot readiness leads first-release tradeoffs, ahead of hackathon optimization.
- Deliver a functional, deployed application. Fixed sample records are acceptable.
- Serve a hospital PhilHealth claims reviewer checking prepared claims against supporting records before submission.
- Build independently when implementation is eventually authorized; a hospital collaboration is not a prerequisite to software development.
- Keep local setup easy and support deployment and growth. Preserve existing work.
- Synthetic records remain the authorized data boundary. The owner wants realistic presentation without repeated "static data" labels.
- The owner delegated the remaining decisions, then authorized proceeding with the recommended changes and FMD reconciliation. This documentation work does not revoke the explicit application implementation pause.

## 2. Product and positioning

**Audience-facing name: Sentinel Claims.** Keep `sentinel-node` as the technical project slug. This is a naming decision, not a trademark/domain availability claim; do not buy a domain or claim exclusivity.

**Descriptor:** PhilHealth claim review workspace.

**Promise:** Find discrepancies. Trace the evidence. Close the review.

**One-line product:** Sentinel Claims helps hospital PhilHealth reviewers compare prepared claims with supporting records, coordinate corrections, and document their review before submission through the hospital's existing system.

**Pain moment selected:** A reviewer receives a prepared claim and several documents, has to establish which belong to the encounter, compare them, chase corrections, and repeat the review after revisions. The product is designed to reduce that coordination and checking burden. Public workflows support this sequence; its frequency, cost, and severity at our future pilot hospital remain unmeasured.

**Primary outcome:** The reviewer can find an actionable discrepancy, inspect its evidence, identify who must correct the source, and verify the revised bundle without losing the prior review. Review time and unnecessary correction requests are evaluation measures. Reimbursement improvements are a later hypothesis.

## 3. Evidence behind the direction

These are documented facts. The choices in the remaining sections are our product decisions, not claims that hospitals already use Sentinel this way.

| Source | What it establishes | Product implication |
|---|---|---|
| [PhilHealth Advisory 2026-0030](https://www.philhealth.gov.ph/advisories/2026/PA2026-0030.pdf), read 2026-10-21 | Claim information should accurately and consistently reflect the clinical record, including diagnoses, procedures, dates, and treatment. | Prioritize evidence-linked comparisons. Avoid claiming a finding establishes medical necessity or a payment entitlement. |
| [PhilHealth Circular 2026-0012, sections V.C.3–4](https://www.philhealth.gov.ph/circulars/2026/PC-2026-0012.pdf), read 2026-10-21 | CF5 adds data to the existing forms; personnel review is required when it is populated from CF2/CF4. eSOA is part of the inpatient claim. | Design around a document bundle with explicit human review. CF5's additional diagnoses are not automatically inconsistent with a shorter CF2 list. |
| [PhilHealth Advisory 2026-0022](https://www.philhealth.gov.ph/advisories/2026/PA2026-0022.pdf), read 2026-10-21 | eSOA submission uses XML; a PDF SOA does not substitute for it. | Distinguish reviewable documents from valid submission artifacts. A PDF comparison does not establish XML compliance. |
| [PhilHealth Advisory 2026-0010, FAQ](https://www.philhealth.gov.ph/advisories/2026/PA2026-0010.pdf), checked in this research | CF5 XML templates and system requirements are provided through PhilHealth's ITMD certification process. | An invented internal schema cannot establish hospital interoperability. Obtain and test a supported export before claiming compatibility. |
| [PhilHealth Advisory 2026-0040](https://www.philhealth.gov.ph/advisories/2026/PA2026-0040.pdf), read 2026-10-21 | The later migration notice sets July 1, 2026 for decommissioning lower eClaims versions. | Do not derive a current integration from the old 2013 implementation guide or the earlier April migration notice. |

See [PILOT-WORKFLOW-RESEARCH.md](PILOT-WORKFLOW-RESEARCH.md) for hospital role/correction workflows and vendor overlap. Sources establish a plausible workflow, not customer discovery, willingness to pay, or proof of the app's accuracy. Check applicability and later amendments before enabling each policy rule.

## 4. First pilot boundary and roles

**One hospital, one claims team, one supported export profile.** Start with adult general medical inpatient ACR claims after discharge, before initial submission. Exclude pediatric, maternity/newborn, surgical, outpatient, dialysis-specific, Z-benefit, and other specialized packages from first-release coverage. Detect or ask the reviewer to confirm the supported scope; unknown applicability stays unresolved. This is a scope choice, not a claim that those excluded claims are invalid.

Target 3–5 named reviewers and one supervisor; these are planning assumptions, not an existing partnership. The financial sponsor is assumed to be the billing/PhilHealth unit head. Confirm the actual buyer later. Do not invent a hospital name, testimonial, customer count, or pilot agreement.

| Role | First-release permissions |
|---|---|
| Reviewer | Import assigned cases, inspect records, disposition findings with reasons, create correction tasks, upload revisions, and mark a complete review ready for final submission review. |
| Supervisor | Review all cases, assign/reassign reviewers, resolve disputed findings, reopen cases, approve documented noncritical exceptions, and view operational metrics. |
| Administrator | Invite/disable accounts, configure the supported profile and published rule pack, manage retention and operations. Clinical/review actions require an explicitly assigned reviewer or supervisor role. |

Billing encoders, medical records staff, and attending clinicians are correction recipients. V1 records the responsible person/department and provides an exportable correction sheet; it does not require every department to adopt a new login or send messages automatically. The reviewer records handoff and acknowledgement. Clinical documentation changes remain with authorized hospital staff.

## 5. Core workflow

1. **Receive:** An encoder prepares the claim in the existing hospital/eClaims system. A reviewer receives readable exports and supporting records, or opens a prepared sample case in the evaluation environment.
2. **Match:** Create/select a case using facility, encounter, and claim references. Assign document types. Display document membership and conflicts for confirmation; a matching name alone is insufficient.
3. **Check coverage:** Show expected, received, readable, unsupported, and unverified inputs. Report checks that cannot run. An absent file means unavailable in the reviewed bundle, not nonexistent in the hospital.
4. **Review:** Run structured consistency checks and AI-assisted text comparison. Each finding opens the relevant source fields/pages, explains the difference, and shows the rule or comparison basis.
5. **Decide and route:** The reviewer requests correction, dismisses a false positive with a reason, or escalates uncertainty. Assign correction responsibility and track its handoff. Never silently rewrite a claim or chart.
6. **Recheck:** Staff correct the originating system/document. The reviewer imports a new bundle version. Compare old/new results, reopen affected decisions, and preserve previous evidence and actions.
7. **Finish review:** After unresolved findings and coverage gaps are addressed, a named reviewer marks the version **Ready for final submission review** and exports the review/correction record. The hospital performs final checks and submits using its existing certified system.

Example success case: a draft form and discharge summary have different discharge dates. Sentinel shows both locations; the reviewer assigns a source correction to the encoder; an updated export is imported; the mismatch disappears on the new run, and the history still shows the original discrepancy and its resolution. This is a synthetic evaluation scenario, not an observed hospital outcome.

## 6. Feature cut

**Required for the first release:**

- Named sign-in, roles, one hospital workspace, assignment, and case access checks.
- Work queue with reference, discharge date, assignee, age in queue, completeness, and review state. Filter by assignee/state and sort by age. A filing due date is displayed only when explicitly supplied or computed from a verified applicable rule; no universal deadline assumption.
- Document upload, membership confirmation, immutable versions, OCR for supported printed scans, source viewer, and an import report.
- Coverage checklist and a bounded, published set of deterministic checks.
- Evidence-linked AI findings for textual discrepancies, with clear incomplete/error states.
- Reasoned decisions, departmental correction tasks, manual handoff tracking, revision comparison, and append-only review history.
- Final internal review record downloadable as CSV plus a printable report. Include source/rule versions, coverage limits, reviewer identity, and outstanding/excepted items.
- Operational counts derived from stored cases and events: awaiting documents, awaiting correction, ready for final review, turnaround, and accepted/dismissed findings. Do not invent revenue saved or reimbursement probability.
- Deployed HTTPS application, persistence, worker recovery, backup/restore, and an operator runbook.

**Later:** additional claim profiles; a tested hospital export adapter; a local folder connector; SSO; richer return-to-hospital tracking; multi-hospital operation; proven clinical/package rules; encounter-manifest reconciliation for claims never prepared.

**Excluded:** direct PhilHealth submission, claim generation, autonomous coding or upcoding, medical advice, signature authenticity certification, reimbursement guarantees, automatic HIS writes, and a general chatbot. No runtime web searches become claim rules without reviewed publication. Commercial pricing and payments are outside the pilot; use a time-limited evaluation with scope and exit criteria before proposing a contract.

## 7. Inputs and interoperability

The case is a **versioned bundle**: claim summary/CF2, CF4, CF5 where applicable, eSOA, and supporting records such as the discharge summary, relevant chart pages, laboratory reports, and signature/eligibility documents required by the selected checklist. Preserve the distinction between a source file, an extracted value, and a reviewer correction to extraction.

- Accept text PDFs, clear printed scanned PDFs, PNG/JPEG attachments, and explicitly supported readable XML. English is the first supported interpretation language. Filipino/mixed-language and handwritten passages can be viewed and manually reviewed, but are not promised automated coverage.
- PDF/image OCR is first-release scope because a reviewer workflow includes scans. Display original images with extracted text; uncertain dates, identifiers, or amounts require confirmation. Manual transcription is stored separately, with user and source location, and never overwrites the source.
- Encrypted or unknown XML, damaged files, unsupported layouts, and unreadable handwriting produce an incomplete/unsupported result. Do not decrypt using hospital credentials, guess a schema, or manufacture missing values.
- Initial limits: 25 MB/file, 100 MB and 150 pages/case version, 30 files/version. Validate before processing; no silent truncation. These are engineering limits to verify under load, not observed hospital bundle sizes.
- Initial evaluation uses the documented **Sentinel sample-bundle profile**. A browser wizard collects identifiers and document types; reviewers do not author XML or a developer manifest. An internal JSON/XML fixture is not called an official eClaims export.
- For an operational hospital pilot, qualify one real export profile with the hospital/vendor, including current schema/version, readable pre-encryption access, attachment matching, sample cases, and import tests. Record exactly which profile is supported. Until then, readiness is for supervised workflow evaluation, not verified HIS interoperability.
- Printed claim forms remain reviewable when XML is unavailable, but submission-format validation is explicitly unavailable and must not appear passed.

## 8. Checks, AI, and decision rules

**Deterministic:** supported-profile required inputs/fields; exact encounter/identifier conflicts; impossible date ordering; comparison of equivalent dates/amounts; arithmetic consistency where line items and subtotal definitions are known; duplicate source uploads; and supported schema validation. Severity depends on applicability and reliable extraction. Avoid naive equality of CF2/CF5 diagnosis lists, billed amounts versus benefit amounts, or differing representations of names.

**AI-assisted:** compare explicitly documented diagnoses, treatment narratives, disposition, and dates across sources; produce a short discrepancy explanation and exact source anchors. The system may say that support was not found in the reviewed material; it must not infer that care was not delivered. Absence is a review question, not proof of a clinical error.

Default model family: NVIDIA Nemotron 3 Super through Nebius Token Factory, with the exact available endpoint/model revision pinned and recorded when implementation begins. Nebius currently documents the model and structured-output controls; neither establishes performance on these records. Select or revise the model on the evaluation set, not on marketing benchmarks. [Nebius Nemotron](https://nebius.com/services/token-factory/nemotron), [structured output documentation](https://docs.tokenfactory.nebius.com/ai-models-inference/json).

Every accepted finding needs source document/version, page/field location, extraction provenance, rule/prompt/model version, and an explanation supported by that evidence. Programmatically verify anchors exist; separately evaluate whether the explanation actually follows from the evidence. Genuine quotes can still support a wrong conclusion. Document text is untrusted input, not instructions. The model receives no write/submit tools and cannot fetch external patient information.

Check coverage states: **Completed / Needs review / Not run / Unsupported / Failed**. Case workflow states: **Received / In review / Awaiting correction / Ready for final submission review / Archived**. Show processing progress independently. A no-finding result means no discrepancy found in completed checks, not a clean or approved claim.

Required unresolved coverage gaps, identity mismatch, missing required inputs, unreviewed findings, or a new bundle version block finalization. False positives may be dismissed with reasons; noncritical exceptions require a supervisor and remain visible in the report. A technical failure cannot be dismissed as a passed check. Where AI cannot complete, a reviewer may perform an explicit manual review with evidence and a supervisor acknowledgement; automated coverage still remains failed/not run. Never substitute canned findings for a failed live call.

Re-uploading identical content reuses the existing version or warns about duplication. New or superseded source/rule versions invalidate finalization and affected finding dispositions. Exported reports remain tied to the reviewed version; the UI flags an old report as stale after changes. Concurrent edits must reject stale updates rather than overwrite another reviewer's decision.

### Initial evaluation checklist: SAMPLE-ADULT-MEDICAL-1

This is our fixed sample-evaluation contract, not an official PhilHealth checklist. It deliberately includes the artifacts the application must exercise. Operational adoption requires a separately qualified hospital profile. No screen/report may equate completion of this checklist with meeting every submission requirement.

Required sample artifacts: claim summary containing CF2-equivalent fields, CF4 clinical summary, CF5 supplementary summary, sample eSOA XML, discharge summary, sample CSF, and sample eligibility evidence. Claim/clinical summaries may be supported PDFs or sample XML; the sample eSOA has a declared internal version and explicit line amounts, discounts, and totals. It is never exported as a PhilHealth-submittable eSOA. The sample CSF uses clearly fictional acknowledgement marks rather than imitating real signatures. Extra laboratory/chart attachments are required when the reviewer declares them expected for the case, with a recorded reason. Additional documents are otherwise optional and excluded checks are visible.

| ID / check | Sources and preconditions | Completion/blocking rule | Manual resolution / override |
|---|---|---|---|
| P01 Scope and identity anchors | Reviewer-confirmed adult medical inpatient profile; claim summary with facility, encounter/claim reference, date of birth and admission date. | Unknown profile, missing anchors, or age under 18 blocks this profile. | Correct an extraction against a legible source or obtain a revised source. Unsupported cases remain outside scope; no override. |
| P02 Bundle membership and readability | All seven required artifacts, typed and associated with the encounter; readable content or a legible original for manual review. | Missing required artifact, unmatched document, or an unreadable required passage blocks completion. | Replace/match the document, or record a source-anchored transcription where the original is legible. Mandatory artifacts cannot be waived. |
| P03 Required field presence | Claim: identifiers, birth/admission/discharge dates, final diagnosis text and disposition. CF4: admission reason, ward course, treatment and outcome. CF5: primary diagnosis/code and disposition. eSOA: encounter, currency, lines, discounts and total. | A required value absent in the source blocks completion; optional fields do not. Check code presence, not clinical correctness or code-library validity. | Extraction correction is permitted with provenance. Missing source content requires source completion. Explicit "none" can satisfy treatment/discount fields only when actually stated; never infer it. |
| P04 Cross-document identity | Compare explicit patient/encounter identifiers for the same declared encounter; require confirmed extraction. | Conflicting explicit identifiers block completion. A name variation alone produces a review question. | Remove a wrongly associated document into a new bundle version or obtain a corrected source. Reviewer may dismiss a name-only alert with matching identifiers and a reason; no override of a known identity conflict. |
| P05 Dates and disposition | Equivalent fields in claim summary, CF4/CF5 and discharge summary; unambiguous dates with matching meanings. | Birth after admission, discharge before admission, or conflicting equivalent dates/disposition requires resolution. Ambiguous date parsing requires confirmation first. | Correct extraction/normalization with source evidence. A genuine discrepancy needs source correction; no administrative waiver. No minimum length-of-stay or benefit rule is inferred. |
| P06 Sample eSOA arithmetic | Supported internal sample version, reliable numeric extraction, PHP values, and explicitly defined line/discount semantics. | Net total must equal summed gross line amounts minus listed discounts within PHP 0.01. Never compare that total to the PhilHealth benefit amount. | Correct extraction or obtain revised source. Other financial representations are unsupported for this check, not guessed. No override of an unresolved arithmetic mismatch. |
| P07 Narrative agreement | Claim diagnosis/treatment/disposition statements and readable corresponding CF4/discharge passages. | AI flags only evidence-supported questions. Every finding requires a reasoned human disposition; true discrepancies require correction. | Reviewer can dismiss a false positive with cited evidence. If AI fails, record a manual comparison and supervisor acknowledgement; automation remains marked failed/not run. An unresolved clinical question cannot be waived. |
| P08 Signature/acknowledgement presence | Manual inspection of the sample CSF and designated certification areas on the sample forms. | Reviewer confirms each expected mark/printed signatory/date or requests completion. The app never verifies signer authenticity or legal validity. | Obtain completed source if a required mark is absent. No override of absence. Sample marks exercise the workflow only. |
| P09 Additional expected attachments | Reviewer-declared laboratory/chart attachments, with reason for expectation and encounter association. | A declared required attachment must be available/readable and its review recorded. | A supervisor may withdraw a mistakenly declared extra requirement with a documented applicability reason. This is the sole V1 noncritical exception; it cannot remove a core artifact or excuse contrary evidence. |
| P10 Review closeout | Current bundle/rule version, all P01–P09 dispositions, manual checklist items, completed correction tasks, named reviewer. | Block if a required item is unresolved, a task is still open, or source/rule changes have invalidated review. | Recheck affected items and close/cancel tasks with reasons. No bypass. Preserve stale prior reports as history. |

Reliable extraction means native structured parsing for the supported sample contract, or source-backed human confirmation of every critical identifier/date/amount used in a blocking result from OCR. An OCR confidence score alone is insufficient. On text PDFs, ambiguous extraction similarly requires confirmation. This adds reviewer effort intentionally and must be included in timing measurements.

Official XML/schema conformance, clinical appropriateness, package eligibility, coding validity, filing-period compliance, signature authenticity, and payer acceptance are **outside this evaluation checklist**. The report lists that scope boundary. They are not silently "passed," and they cannot become mandatory then disappear through a generic override. A published hospital profile must explicitly define any added required checks and their completion rules.

## 9. Experience and sample data

Desktop-first English workspace, readable at 1366×768, with keyboard navigation and a narrow-screen fallback. Use a queue, a focused case workbench with evidence beside findings, and a compact history/corrections view. Keep the earlier calm light-paper/forest/teal direction; use amber for attention and red for blocking issues, always with text/icons. Use explicit dates and PHP formatting where appropriate, and Asia/Manila for displayed operational timestamps.

Primary vocabulary: **Claim, Supporting records, Finding, Request correction, Needs review, Review history**. Keep infrastructure, model tuning, and schema details in diagnostics/settings, except when a format limitation affects the reviewer's next action.

Use realistic, internally consistent fictional records and varied case states. Do not add "static" badges to every record. Identify the environment once as **Evaluation workspace — sample patient records**, and mark downloadable exports so they cannot be mistaken for hospital records. No real hospital branding, forged signatures, real membership identifiers, invented customer testimonials, or fabricated payment outcomes.

The records can be fixed; **the behavior must be real**: findings come from file contents, correction decisions persist, uploads change results, history survives refresh/restart, and metrics come from stored actions. The published evaluation environment has a separate database/storage from any future hospital deployment. Public visitors use prepared sample bundles; authenticated evaluation staff may upload only authorized synthetic samples. User uploads are not silently treated as safe merely because a checkbox was ticked.

## 10. Delivery decisions

Keep the existing Python/FastAPI/SQLAlchemy direction and small browser client. Use PostgreSQL for both the standard local Docker setup and deployment; the existing SQLite path may remain for lightweight development but is not a supported pilot deployment. Use separate web and worker processes with a durable database queue. Store documents in private object storage, with a local filesystem adapter for development. No Kubernetes, separate queue broker, or microservice split is needed for this target.

Initial deployment choice: a CPU VM on Nebius AI Cloud running the containers behind HTTPS, PostgreSQL on persistent storage, and private Nebius Object Storage for documents/backups. Inference is remote through Token Factory; no dedicated GPU is required by our design. Initial sizing target is approximately 4 vCPU/16 GB RAM, adjusted to an available preset and measured load. Provider region, account quota, actual price, and the selected preset must be confirmed before provisioning; no cloud purchase is authorized by this decision record. VM/storage offerings are documented by [Nebius Compute](https://docs.nebius.com/compute) and [Nebius Storage](https://nebius.com/services/storage).

This is a modest single-hospital deployment with a single-host failure domain, not high availability. Keep web/worker/database/storage boundaries so each can be separated later. Growth is measured before introducing more infrastructure.

Planning targets: 5 concurrent reviewers, 100 imported cases/day, and 10,000 retained case metadata records. Under a representative load of five active users and two concurrent audits, aim for ordinary queue/case interactions at p95 under 2 seconds, text-only audit processing at p95 under 2 minutes, and supported scanned cases at p95 under 5 minutes. Report queue wait separately. These are acceptance targets, not measured capabilities.

Named accounts and server-side authorization, secure sessions, MFA for privileged roles, private document access, upload size/type checks and malware handling, encrypted transport/storage/backups, secrets outside source control, and metadata-only application logs are release requirements. Audit access, exports, review actions, profile/rule changes, and account administration. Do not send patient content to analytics or error trackers.

For the synthetic evaluation, take daily encrypted backups, retain seven recovery points, and test restoration to a clean environment; target RPO 24 hours and RTO one business day. Review those values with the hospital before operational use. Retain evaluation work for 90 days, then export/delete under the operator's control; maintain backup expiry and deletion records. Actual hospital retention is a dependency, not inferred from this sample-data policy. Local startup must work from documented commands with sample data; full AI review requires connectivity and configured credentials.

Health-record processing requires hospital-specific purpose, access, retention, processor/hosting arrangements, and data-flow review. These are release dependencies before real records, not a claim of compliance based on a login screen. NPC's IRR addresses security controls and processor contracts, including processing location. [NPC IRR, rules VI and X](https://privacy.gov.ph/implementing-rules%20regulations-data-privacy-act-2012/). Choose the actual hospital region and inference arrangement only after that review; the sample deployment does not establish data residency suitability.

## 11. Acceptance and pilot evaluation

Two explicit milestones preserve the owner's deployed-app requirement:

**A. Deployed workflow evaluation:** a functioning, accessible app with sample records and all required workflow, persistence, evidence, access, and recovery behaviors. No functional screen or button is a mock. Available to hospital reviewers for a supervised evaluation.

**B. Operational hospital pilot:** milestone A plus a named hospital sponsor, qualified export profile, hospital-approved data/hosting arrangements, agreed retention/recovery targets, trained reviewers, and reviewed check applicability. Run alongside the existing process first; the hospital keeps submission authority. No evidence currently establishes milestone B.

Before calling milestone A ready, verify:

1. A reviewer completes import → evidence review → correction handoff → revised import → final review record through the deployed URL. A second account can take over appropriately; unauthorized account/role access is denied, including direct file URLs.
2. Prepare 40 locked synthetic evaluation bundles separate from prompt-development cases: 20 with explicit discrepancies, 10 clean, and 10 incomplete/unsupported/adversarial cases. Include corrected version pairs, scanned/text equivalents, wrong encounter, date conflict, missing expected document, unreadable scan, conflicting amounts with known definitions, unsupported XML, duplicated upload, and document-embedded instructions. Preserve expected findings and source anchors.
3. Require all specified deterministic checks to match the fixture expectations and zero false finalization on incomplete/unsupported cases. Every displayed evidence link must resolve to the right version. These bounded fixture results are not population-level accuracy claims.
4. For AI findings, target at least 90% precision and 80% recall on the explicitly annotated discrepancy set, with separately reported denominators, misses, abstentions, and OCR errors. Run three times with pinned settings; require targets on each run. Unmet targets trigger narrowing or disabling the failing check, not hiding the result. Report this small synthetic benchmark honestly.
5. Test timeout/rate limit, invalid model output, worker restart, duplicate requests, stale concurrent edits, source replacement after finalization, restore, and redaction of operational logs. Existing historical tests do not satisfy this gate.
6. Observe two practicing claims reviewers on ten varied sample cases each, with matched manual-review and app-assisted tasks in counterbalanced order. Target no increase in missed seeded issues and at least 20% lower median active review time. Record import/setup and correction-handoff time separately so the app cannot appear faster by moving work to someone else. These are go/no-go targets, not achieved results; failure means revise scope/workflow. This evaluation does not require a partnership before development.

Once real-record use is authorized, start with a proposed two-week supervised evaluation of 50 consecutive in-scope claims. Record additional issues accepted by staff, false positives, import time, reviewer effort, and correction turnaround. Compare against existing vendor validation. Submission/return/payment outcomes remain separate later measures; do not count every finding as money recovered.

## 12. Changes to the earlier proposal

| Earlier proposal or local scaffold | Decision and reason |
|---|---|
| Sentinel Node as audience-facing name | Use Sentinel Claims so the name identifies the job. Preserve the repo slug and existing files. |
| One XML file and one text chart | Use a versioned document bundle with explicit membership and coverage; a realistic review involves several documents. |
| Unsupported image-only PDFs | Add printed-scan OCR and manual verification; do not claim handwriting coverage. |
| A shared workspace without named actor/role controls | Add named reviewers, supervisor permissions, assignments, and traceable decisions. |
| Finding decisions alone | Add correction responsibility, handoff tracking, revised-source review, and stale-result handling. |
| Internal XML contract as sufficient import scope | Keep it for fixtures; qualify one real hospital export profile before claiming operational compatibility. |
| Optional model calls as the entire AI story | Require a tested live AI-assisted path for release, with explicit failure/manual fallback. No canned runtime results. |
| Broad claims-auditor/revenue positioning | Narrow to pre-submission document reconciliation for adult medical inpatient claims. Measure workflow outcomes before financial claims. |
| Potential live policy search | Use reviewed, versioned rules with effective dates and source references; browsing is an administrative research activity. |
| SQLite local / PostgreSQL deploy | Make PostgreSQL the standard local and hosted environment to reduce concurrency differences. Preserve lightweight SQLite only as optional development support. |

## 13. External dependencies and next action

Decisions have been made where judgment is sufficient. Facts still needed are: actual host account/region/quota/cost; a supported model endpoint; a hospital sponsor and real export profile for milestone B; hospital-specific processing/retention arrangements; and reviewer evaluation results. No interview, integration, security review, model benchmark, or deployment has been completed by writing this document.

The current hackathon rules still allow a runtime Token Factory inference call to satisfy the platform requirement and allow private applications with testing credentials. Keep a separate sample-data evaluation environment accessible for judging if submitting, and prioritize the hospital workflow over prize-specific features. The current deadline is October 30, 2026 at 10:00 AM Pacific. This is not a promise that the full pilot scope fits that date. [Official rules, checked 2026-10-21](https://nebiusglobalaihackathon.devpost.com/rules).

Reconciliation completed on 2026-10-21: framing and scrutiny now reflect the approved scope, with PROCEED WITH FIXES and downstream evidence requirements. See HANDOFF.md and the latest documentation log for verification scope. Application implementation still requires an explicit instruction to resume; preserve the provisional code and assess it against the canonical baseline at that time.

Review record: an independent planning review identified an undefined initial completion checklist. Section 8 now fixes that with P01–P10, required sample artifacts, manual signature-presence review, and explicit exception rules. The follow-up review found no remaining material contradiction in that section or its adjacent rules. Local Markdown links in this record, the workflow research, and HANDOFF.md were checked successfully. That earlier review was document-only. The later FMD reconciliation and check results are recorded in docs/log-sentinel-node.md; no application tests, deployment verification or hospital validation were performed.

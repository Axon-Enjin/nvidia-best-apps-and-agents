# Hospital claims workflow research

Researched 2026-10-21. Standalone decision input; not an FMD artifact or authorization to resume development. No hospital partner, authorized patient dataset, vendor integration, or clinical validation is assumed.

## Verified workflow evidence

**Quezon City General Hospital: billing hands discharged cases to a dedicated PhilHealth section.** Billing checks completeness; the PhilHealth section receives discharged claims, encodes them into eClaims, checks entries, reviews the Claim Signature Form and attachments, scans/uploads documents, and transmits. The same section separately handles returned and denied claims: it reviews PhilHealth's RTH letter and validation report, addresses discrepancies, obtains/scans documents, validates and refiles. Denials involve reconsideration/appeal work. This establishes a real pre-transmittal checkpoint and a separate post-submission correction workflow; it does not establish a universal hospital staffing model. [QCGH Accounting Division](https://www.qcgh.org/accounting.html)

**Premiere Medical Center: claim preparation and checking have distinct responsibilities.** Its published flow assigns CF2 and CF4 encoding to claims processors. CF4 content is drawn from the patient chart, including admission reason, examination, ward course and medications. Claim checkers look for incomplete forms, missing attachments and missing signatures. They request attending-physician completion of missing operative documentation, incomplete ward course and professional signatures. Prepared claims and SOA enter the processing section daily. The listed document set includes CSF, SOA, PBEF, CF2, CF4 and condition-dependent records. This is useful evidence of handoffs, not a current national documentary checklist. Its page includes benefit thresholds and local eligibility practices that must not be adopted as national policy without checking the applicable current circular. [Premiere Medical Center claims flow](https://www.pmcne.ph/general-5-1)

**Existing vendor systems already cover important basic validation and tracking.** Bizbox's public BEACON API help index lists uploaded-Excel validation, incomplete-data extraction, doctor-order/medicine templates, CF4 XML generation, missing CF4/eSOA checks, claim issues, document uploads and return-deficiency/refiling operations. This is evidence of documented vendor capabilities, not verification of their execution quality or permission to integrate. The research tool retrieved the indexed help contents; direct opening of that page failed. Do not infer an open, stable or customer-authorized API from a public help index. [BEACON API help](https://beacon.bizbox.ph/Help)

**The inputs and integration requirements extend beyond one PDF.** PhilHealth publishes CF1, CF2, CF3, CF4 and CSF, their guidance, package-specific documents, and eClaims certification, storage, engagement and account/cipher-key materials. Their availability supports planning for structured records plus attachments and versioned requirements. It does not establish which exact export any hospital can provide or that this project is certified. [PhilHealth downloads](https://www.philhealth.gov.ph/downloads/)

## Suggested product decisions (inference and judgment)

1. Place the first release after claim preparation and before transmission. Primary operator: hospital claims reviewer; supporting roles: preparer, responsible clinical/document owner and supervisor. Use role assignments that one person can hold in a small team.
2. Make the complete loop: receive claim bundle → review documents and discrepancies → assign a specific correction → replace corrected source documents → rerun affected checks → reviewer closes the review → export a review record for the existing submission process.
3. Prioritize cross-document identity/date/amount inconsistencies and absent or unreadable supporting evidence. Pair each finding with source locations, the compared values, the requested action and an owner. Missing document, failed extraction and clinical uncertainty need distinct explanations.
4. Start with a narrowly defined inpatient claim profile. Treat document requirements as profile- and effective-date-specific. Unsupported packages should be explicit; one universal completeness score would overstate coverage.
5. Preserve source versions. Never silently amend the hospital record, invent a diagnosis, or treat a possible clinical inconsistency as a proven error. Corrections occur in the responsible source workflow, followed by reimport and review.
6. Use an internal completion status such as “Review complete,” with coverage and unresolved limitations visible. It must not imply payer approval, successful transmission or guaranteed reimbursement.
7. Keep first-release handoffs inside the app and provide a downloadable correction summary. Hospital staff can route that through their established channels; automatic clinical messaging and vendor write-back require a later integration decision.
8. Keep return-to-hospital cases, denials/appeals and unpaid-claim reconciliation outside the initial core workflow. Model them as different future work types rather than conflating them with pre-submission findings.
9. A proposed import contract can accept a structured claim manifest and readable documents, but “hospital compatible” remains unproven until an authorized representative export is mapped and tested. An encrypted final transmission bundle may not be the useful upstream review input.

## What remains unverified

- Actual division of labor, review volume, recurring discrepancy types and correction turnaround at a prospective pilot hospital.
- Whether its vendor exposes readable draft data, attachment files, stable identifiers, version metadata and exports without duplicating manual encoding.
- Current package rules, filing periods and electronic schema versions; this note is workflow evidence, not a complete regulatory review.
- Incremental benefit over the hospital's current validation. Measure reviewer-confirmed useful findings, false alerts, correction completion and review time before making savings or return-reduction claims.
- Synthetic cases can exercise the loop and persistence, but cannot establish real-record extraction accuracy, clinical correctness, integration readiness or hospital adoption.

These unknowns should be explicit pilot entry checks. They do not prevent defining or independently building the eventual synthetic-data product once implementation is authorized.

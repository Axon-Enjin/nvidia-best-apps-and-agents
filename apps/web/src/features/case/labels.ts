// Plain-language names for technical identifiers. Identifiers stay visible as
// secondary references wherever they matter (check IDs, action codes).

const DOCUMENT_LABELS: Record<string, string> = {
  cf2: "CF2 claim summary",
  cf4: "CF4 clinical summary",
  cf5: "CF5 supplementary summary",
  esoa: "Statement of account (eSOA)",
  discharge: "Discharge summary",
  csf: "CSF signature form",
  eligibility: "Eligibility evidence",
};

const CHECK_LABELS: Record<string, string> = {
  P01: "Claim scope (adult medical inpatient)",
  P02: "Required documents",
  P03: "Required values",
  P04: "Patient and encounter identity",
  P05: "Dates and discharge status",
  P06: "Statement of account arithmetic",
  P07: "Narrative agreement",
  P08: "Signature marks, printed names and dates",
  P09: "Extra attachments",
  P10: "Current-version closeout",
};

const FIELD_LABELS: Record<string, string> = {
  facility_id: "Facility ID",
  encounter_ref: "Encounter reference",
  claim_ref: "Claim reference",
  patient_id: "Patient ID",
  scope: "Scope",
  dob: "Date of birth",
  admission_date: "Admission date",
  discharge_date: "Discharge date",
  diagnosis: "Diagnosis",
  diagnosis_code: "Diagnosis code",
  disposition: "Disposition",
  admission_reason: "Admission reason",
  course: "Course",
  treatment: "Treatment",
  outcome: "Outcome",
  currency: "Currency",
  total: "Total",
  printed_name: "Printed name",
  mark: "Mark",
  signed_date: "Signed date",
};

const DOCUMENT_STATUS: Record<string, string> = {
  readable: "Readable",
  needs_confirmation: "Scan: confirm values",
  unreadable: "Unreadable",
  unsupported: "Unsupported format",
  unmatched: "Identity does not match the claim",
  ambiguous: "Conflicting values inside the document",
  quarantined: "Waiting for processing",
};

const EVENT_LABELS: Record<string, string> = {
  correction_created: "Correction requested",
  correction_handoff: "Handoff recorded",
  correction_acknowledged: "Acknowledgement recorded",
  correction_resolved: "Correction resolved",
  correction_cancelled: "Correction cancelled",
  manual_p07: "Manual comparison recorded",
  supervisor_ack: "Supervisor acknowledgement",
  manual_p08: "Presence review recorded",
  dismissed: "Narrative question dismissed",
  extra_expected: "Extra attachment required",
  extra_reviewed: "Extra attachment reviewed",
  extra_withdrawn: "Extra attachment requirement withdrawn",
  recheck: "Checks re-run",
  extraction_confirmed: "Scan value confirmed",
  finalized: "Review completed",
};

const MANUAL_PRESENCE = "Named manual presence review is required.";

export function documentLabel(type: string, filename?: string): string {
  if (type === "attachment") return filename ? `Attachment ${filename}` : "Attachment";
  return DOCUMENT_LABELS[type] ?? type.toUpperCase();
}

export function checkLabel(id: string): string {
  return CHECK_LABELS[id] ?? id;
}

export function fieldLabel(key: string): string {
  const known = FIELD_LABELS[key];
  if (known) return known;
  const words = key.replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export function documentStatusText(status: string): string {
  return DOCUMENT_STATUS[status] ?? status;
}

export function documentStatusTone(status: string): "passed" | "attention" | "blocking" | "neutral" {
  if (status === "readable") return "passed";
  if (status === "needs_confirmation") return "attention";
  if (status === "quarantined") return "neutral";
  return "blocking";
}

export function eventLabel(action: string): string {
  return EVENT_LABELS[action] ?? action;
}

type CheckLike = { id: string; status: string; blocking_reasons: string[] };

/** Expected human reviews are attention (amber); problems in the sources are blocking (red). */
export function checkSeverity(check: CheckLike): "passed" | "attention" | "blocking" {
  if (check.status === "passed") return "passed";
  if (check.id === "P07" || check.id === "P09") return "attention";
  if (check.id === "P08" && check.blocking_reasons.every((reason) => reason === MANUAL_PRESENCE)) return "attention";
  return "blocking";
}

export function checkStatusText(check: CheckLike): string {
  const severity = checkSeverity(check);
  if (severity === "passed") return "Passed";
  if (severity === "attention") return "Needs manual review";
  if (check.status === "flagged") return "Discrepancy";
  if (check.status === "unsupported") return "Unsupported";
  return "Incomplete";
}

const DOC = "(cf2|cf4|cf5|esoa|discharge|csf|eligibility|attachment)";

/** Rewrites the review service's reasons as sentences with plain names; unknown text passes through. */
export function plainReason(reason: string): string {
  const rules: [RegExp, (...groups: string[]) => string][] = [
    [/^Conflicting (\w+) values across sources\.$/, (key) => `${fieldLabel(key)} differs between documents.`],
    [/^Ambiguous (\w+); use a confirmed ISO date\.$/, (key) => `${fieldLabel(key)} is ambiguous; confirm it as a date like 2026-10-14.`],
    [/^(\w+) differs from case membership\.$/, (key) => `${fieldLabel(key)} differs from the claim's identity.`],
    [new RegExp(`^${DOC}: missing/unknown (\\w+)$`), (type, key) => `${documentLabel(type)}: ${fieldLabel(key)} is missing or unknown.`],
    [new RegExp(`^${DOC}: missing (\\w+)$`), (type, key) => `${documentLabel(type)}: ${fieldLabel(key)} is missing.`],
    [new RegExp(`^Missing ${DOC}\\.$`), (type) => `${documentLabel(type)} is missing.`],
    [new RegExp(`^Require exactly one readable matched ${DOC}\\.$`), (type) => `Needs exactly one readable, matching ${documentLabel(type)}.`],
  ];
  for (const [pattern, write] of rules) {
    const match = pattern.exec(reason);
    if (match) return write(...match.slice(1).map((group) => group ?? ""));
  }
  return reason;
}

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  checkLabel,
  checkSeverity,
  checkStatusText,
  documentLabel,
  documentStatusText,
  eventLabel,
  fieldLabel,
  plainReason,
} from "./labels.ts";

test("document types read as plain names", () => {
  assert.equal(documentLabel("cf2"), "CF2 claim summary");
  assert.equal(documentLabel("discharge"), "Discharge summary");
  assert.equal(documentLabel("esoa"), "Statement of account (eSOA)");
  assert.equal(documentLabel("attachment", "lab-result.pdf"), "Attachment lab-result.pdf");
  assert.equal(documentLabel("unknown_kind"), "UNKNOWN_KIND");
});

test("checks and fields read as plain names", () => {
  assert.equal(checkLabel("P05"), "Dates and discharge status");
  assert.equal(checkLabel("P08"), "Signature marks, printed names and dates");
  assert.equal(checkLabel("P99"), "P99");
  assert.equal(fieldLabel("discharge_date"), "Discharge date");
  assert.equal(fieldLabel("dob"), "Date of birth");
  assert.equal(fieldLabel("some_new_field"), "Some new field");
});

test("backend reasons become plain sentences", () => {
  assert.equal(plainReason("Conflicting discharge_date values across sources."), "Discharge date differs between documents.");
  assert.equal(plainReason("Conflicting dob values across sources."), "Date of birth differs between documents.");
  assert.equal(plainReason("cf4: missing course"), "CF4 clinical summary: Course is missing.");
  assert.equal(plainReason("csf: missing/unknown signed_date"), "CSF signature form: Signed date is missing or unknown.");
  assert.equal(plainReason("patient_id differs from case membership."), "Patient ID differs from the claim's identity.");
  assert.equal(plainReason("Missing cf4."), "CF4 clinical summary is missing.");
  assert.equal(plainReason("Require exactly one readable matched esoa."), "Needs exactly one readable, matching Statement of account (eSOA).");
  assert.equal(plainReason("Ambiguous admission_date; use a confirmed ISO date."), "Admission date is ambiguous; confirm it as a date like 2026-10-14.");
  assert.equal(plainReason("Discharge precedes admission."), "Discharge precedes admission.");
});

const check = (id: string, status: string, blocking_reasons: string[]) => ({ id, status, blocking_reasons });

test("manual reviews are attention, deterministic problems are blocking", () => {
  assert.equal(checkSeverity(check("P05", "flagged", ["Conflicting discharge_date values across sources."])), "blocking");
  assert.equal(checkSeverity(check("P05", "passed", [])), "passed");
  assert.equal(checkSeverity(check("P07", "incomplete", ["Record source-backed manual comparison and separate supervisor acknowledgement."])), "attention");
  assert.equal(checkSeverity(check("P08", "incomplete", ["Named manual presence review is required."])), "attention");
  assert.equal(checkSeverity(check("P08", "incomplete", ["csf: missing/unknown mark", "Named manual presence review is required."])), "blocking");
  assert.equal(checkSeverity(check("P09", "incomplete", ["Review the expected extra attachment or obtain a reasoned supervisor withdrawal."])), "attention");
});

test("status text never relies on color", () => {
  assert.equal(checkStatusText(check("P05", "flagged", ["x"])), "Discrepancy");
  assert.equal(checkStatusText(check("P03", "incomplete", ["x"])), "Incomplete");
  assert.equal(checkStatusText(check("P06", "unsupported", ["x"])), "Unsupported");
  assert.equal(checkStatusText(check("P07", "incomplete", ["x"])), "Needs manual review");
  assert.equal(checkStatusText(check("P01", "passed", [])), "Passed");
  assert.equal(documentStatusText("needs_confirmation"), "Scan: confirm values");
  assert.equal(documentStatusText("unsupported"), "Unsupported format");
  assert.equal(documentStatusText("unmatched"), "Identity does not match the claim");
  assert.equal(eventLabel("correction_handoff"), "Handoff recorded");
  assert.equal(eventLabel("supervisor_ack"), "Supervisor acknowledgement");
  assert.equal(eventLabel("brand_new_action"), "brand_new_action");
});

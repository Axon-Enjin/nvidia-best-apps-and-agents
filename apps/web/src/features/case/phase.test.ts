import assert from "node:assert/strict";
import { test } from "node:test";

import type { ClaimDetail, ReviewState } from "../../lib/api-types.ts";
import { phaseStatus, resolvePhase } from "./phase.ts";

type Job = NonNullable<ClaimDetail["latest"]>;
const job = (status: string): Job => ({
  id: "j", claim_id: "c", status, created_at: 0, finished_at: null, attempts: 1, use_model: false,
  xml_name: "", chart_name: null, result: null, error: status === "failed" ? "Parser stopped." : null,
});

function claim(overrides: Partial<ClaimDetail> = {}): ClaimDetail {
  return {
    id: "c", facility_id: "F", encounter_ref: "E", claim_ref: "C", patient_id: "P", revision: 3,
    current_bundle_id: "b2", assignee_id: "a", state: "In review", reference: "C", sample: false,
    bundles: [{ case_id: "c", bundle_id: "b2", version: 2, revision: 3, import_job_id: "j", coverage: [] }],
    latest: job("succeeded"), history: [], ...overrides,
  };
}

function review(overrides: Partial<ReviewState> = {}): ReviewState {
  const passed = (id: string) => ({ id, label: id, status: "passed", blocking_reasons: [], anchors: [], differences: [] });
  return {
    rule_version: "R", bundle_id: "b2", profile_status: "evaluated", model_status: "not_run_offline", outcome: "incomplete",
    checks: ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10"].map(passed),
    findings: [], fields: {}, coverage: [], revision: 3, bundle_version: 2, tasks: [], expectations: [], events: [],
    blockers: [], can_finalize: false, confirmations: [], ...overrides,
  };
}

const flagged = { id: "P05", label: "P05", status: "flagged", blocking_reasons: ["x"], anchors: [], differences: [] };

test("no current version, processing or failed checks lead to Import", () => {
  assert.equal(resolvePhase(claim({ current_bundle_id: null, latest: null, bundles: [] }), null), "import");
  assert.equal(resolvePhase(claim({ latest: job("queued") }), null), "import");
  assert.equal(resolvePhase(claim({ latest: job("running") }), null), "import");
  assert.equal(resolvePhase(claim({ latest: job("failed") }), review()), "import");
});

test("scan values awaiting confirmation lead to Import", () => {
  const confirmations = [{ document_id: "d", type: "cf2", status: "needs_confirmation", pending: ["dob"], confirmed: {}, fields: ["dob"] }];
  assert.equal(resolvePhase(claim(), review({ confirmations })), "import");
});

test("a returning reviewer with open issues resumes in Review", () => {
  assert.equal(resolvePhase(claim(), review({ checks: [flagged] })), "review");
});

test("completion allowed or done leads to Complete", () => {
  assert.equal(resolvePhase(claim(), review({ can_finalize: true })), "complete");
  assert.equal(resolvePhase(claim({ state: "Ready for final submission review" }), review()), "complete");
});

test("phase status says what each phase holds", () => {
  assert.deepEqual(phaseStatus(claim({ current_bundle_id: null, latest: null, bundles: [] }), null), {
    import: "Not started", review: "Waiting for checks", complete: "Not ready",
  });
  assert.equal(phaseStatus(claim({ latest: job("running") }), null).import, "Processing");
  const confirmations = [{ document_id: "d", type: "cf2", status: "needs_confirmation", pending: ["dob", "patient_id"], confirmed: {}, fields: [] }];
  assert.equal(phaseStatus(claim(), review({ confirmations })).import, "2 scan values to confirm");
  const open = review({ checks: [flagged, { ...flagged, id: "P07" }], blockers: [{ id: "P05", reasons: [] }, { id: "P07", reasons: [] }] });
  assert.equal(phaseStatus(claim(), open).import, "Version 2 imported");
  assert.equal(phaseStatus(claim(), open).review, "2 issues need attention");
  assert.equal(phaseStatus(claim(), open).complete, "2 blockers remain");
  assert.equal(phaseStatus(claim(), review({ checks: [{ ...flagged, id: "P07" }] })).review, "1 issue needs attention");
  assert.equal(phaseStatus(claim(), review({ can_finalize: true })).complete, "Ready to complete");
  assert.equal(phaseStatus(claim({ state: "Ready for final submission review" }), review()).complete, "Completed");
  assert.equal(phaseStatus(claim(), review()).review, "All checks resolved");
});

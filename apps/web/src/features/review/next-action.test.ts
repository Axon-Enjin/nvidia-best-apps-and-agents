import assert from "node:assert/strict";
import { test } from "node:test";

import type { Actor, Check, CorrectionTask, ReviewEvent, ReviewState } from "../../lib/api-types.ts";
import { hasOpenTask, nextAction, taskStep } from "./next-action.ts";

const reviewer: Actor = { id: "r1", username: "reviewer", roles: ["reviewer"] };
const supervisor: Actor = { id: "s1", username: "supervisor", roles: ["supervisor"] };

const check = (id: string, status = "incomplete", reasons = ["x"]): Check => ({
  id, label: id, status, blocking_reasons: status === "passed" ? [] : reasons, anchors: [], differences: [],
});

let revision = 0;
const event = (action: string, actor: Actor, payload: ReviewEvent["payload"] = {}, bundle = "b2"): ReviewEvent => ({
  id: `e${++revision}`, bundle_id: bundle, rule_version: "R", revision, actor_id: actor.id ?? "", actor: actor.username,
  action, payload: { reason: "because", ...payload }, created_at: revision,
});

const task = (status: string, bundle = "b2", checkId = "P05"): CorrectionTask => ({
  id: "t1", check_id: checkId, department: "Records", person: "Clerk", reason: "differs", anchors: [], status, bundle_id: bundle, created_at: 0,
});

function review(overrides: Partial<ReviewState> = {}): ReviewState {
  return {
    rule_version: "R", bundle_id: "b2", profile_status: "evaluated", model_status: "not_run_offline", outcome: "incomplete",
    checks: [check("P05", "flagged")], findings: [], fields: {}, coverage: [], revision: 9, bundle_version: 2, tasks: [],
    expectations: [], events: [], blockers: [], can_finalize: false, confirmations: [], ...overrides,
  };
}

test("a cited scan awaiting confirmation comes first", () => {
  const cited = { ...check("P02"), anchors: [{ field: "dob", value: "x", page: 1, bundle_id: "b2", document_id: "scan" }] };
  const state = review({ confirmations: [{ document_id: "scan", type: "cf2", status: "needs_confirmation", pending: ["dob"], confirmed: {}, fields: [] }] });
  assert.equal(nextAction(cited, state, reviewer).kind, "confirm_scans");
});

test("deterministic problems lead to a correction request", () => {
  assert.equal(nextAction(check("P05", "flagged"), review(), reviewer).kind, "request_correction");
  assert.equal(nextAction(check("P08", "incomplete", ["csf: missing/unknown mark", "Named manual presence review is required."]), review(), reviewer).kind, "request_correction");
});

test("an open correction task leads to its next step, even once the check passes", () => {
  assert.deepEqual(nextAction(check("P05", "flagged"), review({ tasks: [task("open")] }), reviewer), { kind: "correction_step", taskId: "t1" });
  assert.deepEqual(nextAction(check("P05", "passed"), review({ tasks: [task("acknowledged", "b1")] }), reviewer), { kind: "correction_step", taskId: "t1" });
  assert.equal(nextAction(check("P05", "passed"), review({ tasks: [task("resolved", "b1")] }), reviewer).kind, "none");
  assert.equal(hasOpenTask("P05", review({ tasks: [task("handed_off")] })), true);
  assert.equal(hasOpenTask("P05", review({ tasks: [task("cancelled")] })), false);
});

test("P07 needs a manual comparison, then a different supervisor", () => {
  assert.equal(nextAction(check("P07"), review(), reviewer).kind, "record_manual_p07");
  const recorded = review({ events: [event("manual_p07", reviewer)] });
  assert.deepEqual(nextAction(check("P07"), recorded, reviewer), { kind: "await_acknowledgement", recordedBy: "reviewer" });
  const action = nextAction(check("P07"), recorded, supervisor);
  assert.equal(action.kind, "acknowledge_p07");
  const bySupervisor = review({ events: [event("manual_p07", supervisor)] });
  assert.deepEqual(nextAction(check("P07"), bySupervisor, supervisor), { kind: "await_acknowledgement", recordedBy: "supervisor" });
});

test("a recheck or scan confirmation reopens the manual comparison", () => {
  const reopened = review({ events: [event("manual_p07", reviewer), event("recheck", reviewer)] });
  assert.equal(nextAction(check("P07"), reopened, supervisor).kind, "record_manual_p07");
  const confirmed = review({ events: [event("manual_p07", reviewer), event("extraction_confirmed", reviewer)] });
  assert.equal(nextAction(check("P07"), confirmed, supervisor).kind, "record_manual_p07");
  const older = review({ events: [event("manual_p07", reviewer, {}, "b1")] });
  assert.equal(nextAction(check("P07"), older, supervisor).kind, "record_manual_p07");
});

test("P08 with only the presence requirement leads to a presence review", () => {
  assert.equal(nextAction(check("P08", "incomplete", ["Named manual presence review is required."]), review(), reviewer).kind, "record_manual_p08");
});

test("P09 leads to the pending attachment review", () => {
  const expectations = [
    { id: "x1", type: "attachment", reason: "lab", reviewed: true },
    { id: "x2", type: "attachment", reason: "imaging", reviewed: false },
  ];
  assert.deepEqual(nextAction(check("P09"), review({ expectations }), reviewer), { kind: "review_extra", expectationId: "x2" });
});

test("correction steps follow handoff, acknowledgement, corrected import, then resolution", () => {
  const passed = review({ checks: [check("P05", "passed")] });
  assert.equal(taskStep(task("open"), review()).action, "correction_handoff");
  assert.equal(taskStep(task("open"), review()).label, "Record handoff");
  assert.equal(taskStep(task("handed_off"), review()).action, "correction_acknowledged");
  const sameVersion = taskStep(task("acknowledged", "b2"), passed);
  assert.equal(sameVersion.importNeeded, true);
  assert.equal(sameVersion.action, null);
  const stillFailing = taskStep(task("acknowledged", "b1"), review());
  assert.equal(stillFailing.action, null);
  assert.equal(stillFailing.blocked, "The corrected version still fails this check.");
  assert.equal(taskStep(task("acknowledged", "b1"), passed).action, "correction_resolved");
  assert.equal(taskStep(task("resolved", "b1"), passed).action, null);
});

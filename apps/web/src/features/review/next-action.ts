import type { Actor, Check, CorrectionTask, ReviewEvent, ReviewState } from "../../lib/api-types.ts";

// What the reviewer can do next for one check, mirroring the review service's
// rules (review.py). The service still decides; this only chooses which
// action to offer and explains why others are not available.

export type NextAction =
  | { kind: "confirm_scans" }
  | { kind: "request_correction" }
  | { kind: "correction_step"; taskId: string }
  | { kind: "record_manual_p07" }
  | { kind: "await_acknowledgement"; recordedBy: string }
  | { kind: "acknowledge_p07"; recordedBy: string; eventId: string }
  | { kind: "record_manual_p08" }
  | { kind: "review_extra"; expectationId: string }
  | { kind: "none"; reason: string };

export type TaskStep = {
  action: "correction_handoff" | "correction_acknowledged" | "correction_resolved" | null;
  label: string;
  importNeeded: boolean;
  blocked?: string;
};

const CLOSED = new Set(["resolved", "cancelled"]);
const MANUAL_PRESENCE = "Named manual presence review is required.";

/** Events that still count for the current version: after the latest recheck or scan confirmation. */
export function currentEvents(review: ReviewState): ReviewEvent[] {
  const current = review.events.filter((event) => event.bundle_id === review.bundle_id && event.rule_version === review.rule_version);
  const cutoff = Math.max(-1, ...current.filter((event) => event.action === "recheck" || event.action === "extraction_confirmed").map((event) => event.revision));
  return current.filter((event) => event.revision > cutoff);
}

export function openTask(checkId: string, review: ReviewState): CorrectionTask | undefined {
  return [...review.tasks].reverse().find((task) => task.check_id === checkId && !CLOSED.has(task.status));
}

export function hasOpenTask(checkId: string, review: ReviewState): boolean {
  return openTask(checkId, review) !== undefined;
}

export function nextAction(check: Check, review: ReviewState, actor: Actor): NextAction {
  const awaiting = new Set(review.confirmations.filter((item) => item.status === "needs_confirmation").map((item) => item.document_id));
  if (check.status !== "passed" && check.anchors.some((anchor) => awaiting.has(anchor.document_id))) return { kind: "confirm_scans" };

  const task = openTask(check.id, review);
  if (task) return { kind: "correction_step", taskId: task.id };
  if (check.status === "passed") return { kind: "none", reason: "This check passed for the current version." };

  if (check.id === "P07") {
    const manual = [...currentEvents(review)].reverse().find((event) => event.action === "manual_p07");
    if (!manual) return { kind: "record_manual_p07" };
    if (actor.roles.includes("supervisor") && actor.id !== manual.actor_id) {
      return { kind: "acknowledge_p07", recordedBy: manual.actor, eventId: manual.id };
    }
    return { kind: "await_acknowledgement", recordedBy: manual.actor };
  }
  if (check.id === "P08" && check.blocking_reasons.every((reason) => reason === MANUAL_PRESENCE)) return { kind: "record_manual_p08" };
  if (check.id === "P09") {
    const pending = review.expectations.find((item) => !item.reviewed && !item.withdrawn);
    if (pending) return { kind: "review_extra", expectationId: pending.id };
  }
  return { kind: "request_correction" };
}

export function taskStep(task: CorrectionTask, review: ReviewState): TaskStep {
  if (task.status === "open") return { action: "correction_handoff", label: "Record handoff", importNeeded: false };
  if (task.status === "handed_off") return { action: "correction_acknowledged", label: "Record acknowledgement", importNeeded: false };
  if (task.status === "acknowledged") {
    if (task.bundle_id === review.bundle_id) return { action: null, label: "Import corrected version", importNeeded: true };
    const check = review.checks.find((item) => item.id === task.check_id);
    if (check?.status !== "passed") {
      return { action: null, label: "Resolve after recheck", importNeeded: false, blocked: "The corrected version still fails this check." };
    }
    return { action: "correction_resolved", label: "Resolve after recheck", importNeeded: false };
  }
  return { action: null, label: "", importNeeded: false };
}

"use client";

import Link from "next/link";

import { CircleCheck, Clock } from "@/components/ui/icons";
import { documentLabel } from "@/features/case/labels";
import type { BundleDetail, CorrectionTask, ReviewState } from "@/lib/api-types";

import { ActionForm } from "./action-form";
import { taskStep } from "./next-action";
import type { ActionContext } from "./use-action-form";
import type { TrackDirty } from "./use-dirty-set";

function steps(task: CorrectionTask, review: ReviewState) {
  const done = new Set<string>(["requested"]);
  if (["handed_off", "acknowledged", "resolved"].includes(task.status)) done.add("handed_off");
  if (["acknowledged", "resolved"].includes(task.status)) done.add("acknowledged");
  if (task.bundle_id !== review.bundle_id) done.add("imported");
  if (task.status === "resolved") done.add("resolved");
  return [
    { key: "requested", label: "Requested" },
    { key: "handed_off", label: "Handed off" },
    { key: "acknowledged", label: "Acknowledged" },
    { key: "imported", label: "Corrected version imported" },
    { key: "resolved", label: "Resolved" },
  ].map((step) => ({ ...step, done: done.has(step.key) }));
}

/** Request, handoff, acknowledgement, corrected import and resolution: each a separate, attributable event. */
export function CorrectionProgress({
  task,
  review,
  bundle,
  context,
  track,
}: {
  task: CorrectionTask;
  review: ReviewState;
  bundle: BundleDetail;
  context: ActionContext;
  track: TrackDirty;
}) {
  const step = taskStep(task, review);
  const list = steps(task, review);
  const current = list.find((item) => !item.done)?.key;
  const evidence = task.anchors
    .map((anchor) => {
      const document = bundle.documents.find((item) => item.id === anchor.document_id);
      return `${document ? documentLabel(document.type, document.filename) : "earlier version"} page ${anchor.page}`;
    })
    .join("; ");

  return (
    <section aria-label="Correction progress" className="panel grid gap-4 p-4">
      <div className="grid gap-1">
        <p className="eyebrow">Correction requested</p>
        <p className="font-semibold">
          {task.department} · {task.person}
        </p>
        <p>{task.reason}</p>
        {evidence ? <p className="text-sm text-ink-muted">Evidence: {evidence}</p> : null}
      </div>
      <ol aria-label="Correction steps" className="grid gap-1.5 border-y border-rule-faint py-3">
        {list.map((item) => (
          <li key={item.key} className="flex items-center gap-2 text-sm">
            {item.done ? (
              <CircleCheck aria-hidden="true" className="size-4 text-passed" />
            ) : (
              <Clock aria-hidden="true" className={`size-4 ${item.key === current ? "text-attention" : "text-ink-muted"}`} />
            )}
            <span className={item.key === current ? "font-semibold" : item.done ? "" : "text-ink-muted"}>{item.label}</span>
            <span className="text-ink-muted">· {item.done ? "done" : item.key === current ? "next" : "not yet"}</span>
          </li>
        ))}
      </ol>

      {step.action ? (
        <ActionForm
          key={`${task.id}-${step.action}`}
          context={context}
          reasonLabel="Note for this step"
          submitLabel={step.label}
          build={({ reason }) => ({ action: step.action ?? "", reason, task_id: task.id, check_id: task.check_id })}
          savedMessage={`Saved: ${step.label.toLowerCase().replace(/^record /, "")} recorded under your name.`}
          onDirtyChange={track("step")}
        />
      ) : null}
      {step.importNeeded ? (
        <div className="grid gap-2">
          <p>The responsible person corrects the authoritative documents outside this workspace. Import the corrected originals as a new version; checks re-run, then resolve this correction.</p>
          <Link href={`/claims/${context.claimId}/import`} className="btn btn-primary justify-self-start no-underline">
            Import corrected version
          </Link>
        </div>
      ) : null}
      {step.blocked ? (
        <p className="border-l-4 border-blocking bg-blocking-tint px-4 py-3 font-semibold text-blocking">
          {step.blocked} Import another corrected version, or cancel this correction with a reason.
        </p>
      ) : null}

      <details className="border-t border-rule-faint pt-2">
        <summary className="min-h-11 py-2 font-semibold">Cancel this correction</summary>
        <ActionForm
          context={context}
          emphasis="secondary"
          reasonLabel="Cancellation reason"
          submitLabel="Cancel correction"
          build={({ reason }) => ({ action: "correction_cancelled", reason, task_id: task.id, check_id: task.check_id })}
          savedMessage="Saved: correction cancelled with your reason."
          onDirtyChange={track("cancel")}
        />
      </details>
    </section>
  );
}

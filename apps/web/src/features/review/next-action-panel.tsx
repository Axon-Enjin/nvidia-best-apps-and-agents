"use client";

import Link from "next/link";
import { useState } from "react";

import { documentLabel } from "@/features/case/labels";
import { useSession } from "@/features/session/session-provider";
import type { BundleDetail, Check, ClaimDetail, ReviewEvent, ReviewState } from "@/lib/api-types";

import { ActionForm } from "./action-form";
import { CorrectionProgress } from "./correction-progress";
import type { EvidenceOptions } from "./evidence-picker";
import type { EvidencePage } from "./evidence";
import { currentEvents, nextAction, type NextAction } from "./next-action";
import type { ActionContext } from "./use-action-form";
import { useDirtySet } from "./use-dirty-set";

const when = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });

function RecordedComparison({ event, bundle }: { event: ReviewEvent; bundle: BundleDetail }) {
  const evidence = (event.payload.anchors ?? [])
    .map((anchor) => {
      const document = bundle.documents.find((item) => item.id === anchor.document_id);
      return `${document ? documentLabel(document.type, document.filename) : "document"} page ${anchor.page}`;
    })
    .join("; ");
  return (
    <div className="panel grid gap-1 p-4">
      <p className="eyebrow">Manual comparison recorded</p>
      <p>
        <span className="font-semibold">{event.actor}</span>
        <span className="text-ink-muted"> · {when.format(new Date(event.created_at * 1000))}</span>
      </p>
      <p>{event.payload.reason}</p>
      {evidence ? <p className="text-sm text-ink-muted">Evidence: {evidence}</p> : null}
    </div>
  );
}

/**
 * One primary next action for the selected check. A form with unsaved input
 * keeps its action in place even if a refresh would offer a different one.
 */
export function NextActionPanel({
  check,
  claim,
  bundle,
  review,
  version,
  pages,
  onDirtyChange,
}: {
  check: Check;
  claim: ClaimDetail;
  bundle: BundleDetail;
  review: ReviewState;
  version: number;
  pages: EvidencePage[];
  onDirtyChange: (dirty: boolean) => void;
}) {
  const { actor } = useSession();
  const computed = nextAction(check, review, actor);
  const [pinned, setPinned] = useState<NextAction | null>(null);
  const shown = pinned ?? computed;
  const { track } = useDirtySet((dirty) => {
    setPinned(dirty ? shown : null);
    onDirtyChange(dirty);
  });

  const context: ActionContext = { claimId: claim.id, revision: claim.revision, bundleId: bundle.bundle_id, ruleVersion: review.rule_version };
  const statuses = Object.fromEntries(review.confirmations.map((item) => [item.document_id, item.status]));
  const suggested: Record<string, number[]> = {};
  for (const page of pages) suggested[page.document.id] = [...(suggested[page.document.id] ?? []), page.page];
  const evidence = (required: string[] = [], documents = bundle.documents): EvidenceOptions => ({ documents, suggested, required, statuses, version });
  const saved = (what: string) => `Saved: ${what} recorded under your name for version ${version}.`;
  const manual = [...currentEvents(review)].reverse().find((event) => event.action === "manual_p07");

  let body: React.ReactNode = null;
  switch (shown.kind) {
    case "request_correction":
      body = (
        <ActionForm
          context={context}
          revealLabel="Request correction"
          intro={
            <p>
              The sources disagree or are incomplete. The authoritative documents are corrected outside this workspace: name who
              will correct them, then import the corrected version.
            </p>
          }
          reasonLabel="Reason"
          submitLabel="Save correction request"
          owner
          evidence={evidence()}
          build={({ reason, department, person, anchors }) => ({ action: "correction_created", check_id: check.id, reason, department, person, anchors })}
          savedMessage={saved("correction request")}
          onDirtyChange={track("request")}
        />
      );
      break;
    case "correction_step": {
      const task = review.tasks.find((item) => item.id === shown.taskId);
      body = task ? <CorrectionProgress task={task} review={review} bundle={bundle} context={context} track={track} /> : null;
      break;
    }
    case "record_manual_p07":
    case "await_acknowledgement":
    case "acknowledge_p07":
      body = (
        <div className="grid gap-4">
          {shown.kind === "record_manual_p07" ? (
            <ActionForm
              context={context}
              revealLabel="Record manual comparison"
              intro={
                <p>
                  AI comparison did not run offline. Compare the narratives in the claim, clinical, supplementary and discharge
                  summaries and record what you found. A different supervisor then acknowledges it.
                </p>
              }
              reasonLabel="Comparison notes"
              submitLabel="Save manual comparison"
              evidence={evidence(["cf2", "cf4", "cf5", "discharge"])}
              build={({ reason, anchors }) => ({ action: "manual_p07", check_id: "P07", reason, anchors })}
              savedMessage={saved("manual comparison")}
              onDirtyChange={track("manual")}
            />
          ) : null}
          {shown.kind !== "record_manual_p07" && manual ? <RecordedComparison event={manual} bundle={bundle} /> : null}
          {shown.kind === "await_acknowledgement" ? (
            <p className="font-semibold">
              {shown.recordedBy === actor.username
                ? "You recorded this comparison, so a different supervisor must acknowledge it."
                : `Waiting for a supervisor other than ${shown.recordedBy} to acknowledge this comparison.`}
            </p>
          ) : null}
          {shown.kind === "acknowledge_p07" ? (
            <ActionForm
              context={context}
              revealLabel="Acknowledge comparison"
              intro={<p>Acknowledge {shown.recordedBy}&apos;s comparison only after checking it against the sources.</p>}
              reasonLabel="Acknowledgement note"
              submitLabel="Save acknowledgement"
              build={({ reason }) => ({ action: "supervisor_ack", check_id: "P07", reason })}
              savedMessage={saved("supervisor acknowledgement")}
              onDirtyChange={track("ack")}
            />
          ) : null}
          <details className="border-t border-rule-faint pt-2">
            <summary className="min-h-11 py-2 font-semibold">Dismiss this narrative question</summary>
            <ActionForm
              context={context}
              emphasis="secondary"
              intro={<p className="text-sm text-ink-muted">Records why a narrative question is not a discrepancy. The comparison and acknowledgement are still required.</p>}
              reasonLabel="Dismissal reason"
              submitLabel="Save dismissal"
              evidence={evidence()}
              build={({ reason, anchors }) => ({ action: "dismissed", check_id: "P07", reason, anchors })}
              savedMessage={saved("dismissal")}
              onDirtyChange={track("dismiss")}
            />
          </details>
        </div>
      );
      break;
    case "record_manual_p08":
      body = (
        <ActionForm
          context={context}
          revealLabel="Record presence review"
          intro={
            <p>
              Check that each signature form carries its fictional mark, printed name and date. This records presence only, not
              authenticity.
            </p>
          }
          reasonLabel="Presence review notes"
          submitLabel="Save presence review"
          evidence={evidence(["cf2", "cf4", "cf5", "csf"])}
          build={({ reason, anchors }) => ({ action: "manual_p08", check_id: "P08", reason, anchors })}
          savedMessage={saved("presence review")}
          onDirtyChange={track("presence")}
        />
      );
      break;
    case "review_extra": {
      const expectation = review.expectations.find((item) => item.id === shown.expectationId);
      const attachments = bundle.documents.filter((document) => document.type === "attachment");
      body = (
        <div className="grid gap-4">
          <p>
            Required extra attachment: <span className="font-semibold">{expectation?.reason}</span>
          </p>
          {attachments.length ? (
            <ActionForm
              context={context}
              revealLabel="Record attachment review"
              reasonLabel="Attachment review notes"
              submitLabel="Save attachment review"
              evidence={evidence(["attachment"], attachments)}
              build={({ reason, anchors }) => ({ action: "extra_reviewed", expectation_id: shown.expectationId, reason, anchors })}
              savedMessage={saved("attachment review")}
              onDirtyChange={track("extra")}
            />
          ) : (
            <p>
              Version {version} has no attachment. <Link href={`/claims/${claim.id}/import`}>Import a version that includes it</Link>.
            </p>
          )}
          {actor.roles.includes("supervisor") ? (
            <details className="border-t border-rule-faint pt-2">
              <summary className="min-h-11 py-2 font-semibold">Withdraw requirement</summary>
              <ActionForm
                context={context}
                emphasis="secondary"
                intro={<p className="text-sm text-ink-muted">Only for a requirement recorded by mistake; core documents cannot be waived.</p>}
                reasonLabel="Withdrawal reason"
                submitLabel="Withdraw requirement"
                build={({ reason }) => ({ action: "extra_withdrawn", expectation_id: shown.expectationId, reason })}
                savedMessage={saved("withdrawal")}
                onDirtyChange={track("withdraw")}
              />
            </details>
          ) : null}
        </div>
      );
      break;
    }
    case "none":
      body = <p className="text-ink-muted">{shown.reason}</p>;
      break;
    case "confirm_scans":
      body = null;
      break;
  }

  return (
    <section aria-label="Next action" className="grid gap-3 border-t-2 border-ink pt-3">
      <h3 className="eyebrow">Next action</h3>
      {body}
    </section>
  );
}

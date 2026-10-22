"use client";

import { useRouter } from "next/navigation";

import type { BundleDetail, ClaimDetail, ReviewState } from "@/lib/api-types";

import { ActionForm } from "./action-form";
import { HistoryPanel } from "./history-panel";
import type { ActionContext } from "./use-action-form";
import { useDirtySet } from "./use-dirty-set";

/** Less frequent actions and the record, one disclosure each. */
export function CaseTools({
  claim,
  bundle,
  review,
  version,
  onDirtyChange,
}: {
  claim: ClaimDetail;
  bundle: BundleDetail;
  review: ReviewState;
  version: number;
  onDirtyChange: (dirty: boolean) => void;
}) {
  const router = useRouter();
  const { track } = useDirtySet(onDirtyChange);
  const context: ActionContext = { claimId: claim.id, revision: claim.revision, bundleId: bundle.bundle_id, ruleVersion: review.rule_version };
  return (
    <section aria-label="Case tools" className="grid gap-1">
      <details className="border-t border-rule pt-2">
        <summary className="min-h-11 py-2 font-semibold">Require an extra attachment</summary>
        <ActionForm
          context={context}
          emphasis="secondary"
          intro={<p className="text-sm text-ink-muted">Adds a reasoned requirement for a laboratory or chart attachment; it becomes part of the Extra attachments check.</p>}
          reasonLabel="Why is it needed?"
          submitLabel="Save requirement"
          build={({ reason }) => ({ action: "extra_expected", reason })}
          savedMessage="Saved: extra attachment requirement recorded under your name."
          onDirtyChange={track("require")}
        />
      </details>
      <details className="border-t border-rule pt-2">
        <summary className="min-h-11 py-2 font-semibold">Re-run checks on version {version}</summary>
        <ActionForm
          context={context}
          emphasis="secondary"
          intro={<p className="text-sm text-ink-muted">Re-running reopens manual review. Earlier decisions stay in history.</p>}
          reasonLabel="Re-run reason"
          submitLabel="Re-run checks"
          build={({ reason }) => ({ action: "recheck", reason })}
          savedMessage="Saved: checks re-run under your name. Manual reviews reopen for this version."
          onDirtyChange={track("recheck")}
          onSaved={() => router.push(`/claims/${claim.id}/import`)}
        />
      </details>
      <HistoryPanel events={review.events} />
    </section>
  );
}

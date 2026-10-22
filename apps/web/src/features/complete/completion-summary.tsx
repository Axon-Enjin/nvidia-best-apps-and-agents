import Link from "next/link";

import { StatusText } from "@/components/ui/status-text";
import { checkLabel, checkSeverity, checkStatusText, documentStatusText, plainReason } from "@/features/case/labels";
import { currentEvents } from "@/features/review/next-action";
import type { BundleDetail, ClaimDetail, ReportRecord, ReviewState } from "@/lib/api-types";

const when = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-0.5 border-b border-rule-faint py-2 sm:grid-cols-[12rem_minmax(0,1fr)] sm:gap-4">
      <dt className="text-ink-muted">{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

/** Who did what, on which version, with which coverage, and exactly what still blocks completion. */
export function CompletionSummary({
  claim,
  bundle,
  review,
  version,
  current,
}: {
  claim: ClaimDetail;
  bundle: BundleDetail;
  review: ReviewState;
  version: number;
  current: ReportRecord | null;
}) {
  const imported = claim.bundles.find((item) => item.bundle_id === claim.current_bundle_id);
  const statuses = new Map<string, number>();
  for (const document of bundle.documents) {
    const status = review.confirmations.find((item) => item.document_id === document.id)?.status ?? document.status;
    statuses.set(status, (statuses.get(status) ?? 0) + 1);
  }
  const events = currentEvents(review);
  const latest = (action: string) => [...events].reverse().find((event) => event.action === action);
  const responsibility = [
    ["Manual comparison (P07)", latest("manual_p07")],
    ["Supervisor acknowledgement (P07)", latest("supervisor_ack")],
    ["Presence review (P08)", latest("manual_p08")],
  ] as const;
  const corrections = review.tasks.filter((task) => task.bundle_id === review.bundle_id || task.status !== "resolved");

  return (
    <section aria-labelledby="summary-heading" className="grid gap-6">
      <h2 id="summary-heading" className="border-t-2 border-ink pt-3 text-lg">
        Review summary
      </h2>
      <dl className="text-sm">
        <Row label="Claim">
          <span className="doc-ref">{claim.reference}</span> · patient <span className="doc-ref">{claim.patient_id}</span>
        </Row>
        <Row label="Current version">
          Version {version}
          {imported ? ` · imported at revision ${imported.revision}` : ""} · case revision {claim.revision}
        </Row>
        <Row label="Rules">
          <span className="doc-ref">{review.rule_version}</span>
        </Row>
        <Row label="AI comparison">
          {review.model_status === "not_run_offline" ? "Not run (offline); narrative agreement uses a named manual comparison." : review.model_status}
        </Row>
        <Row label="Coverage">
          {bundle.documents.length} documents:{" "}
          {[...statuses.entries()].map(([status, count]) => `${count} ${documentStatusText(status).toLowerCase()}`).join(", ")}
        </Row>
        {responsibility.map(([label, event]) => (
          <Row key={label} label={label}>
            {event ? (
              <>
                <span className="font-semibold">{event.actor}</span> · {when.format(new Date(event.created_at * 1000))}
              </>
            ) : (
              <span className="text-ink-muted">Not recorded for this version</span>
            )}
          </Row>
        ))}
        <Row label="Corrections">
          {corrections.length ? (
            <ul className="grid gap-0.5">
              {corrections.map((task) => (
                <li key={task.id}>
                  {checkLabel(task.check_id)}: {task.department} · {task.person} · {task.status.replace("_", " ")}
                </li>
              ))}
            </ul>
          ) : (
            <span className="text-ink-muted">None open</span>
          )}
        </Row>
        {current ? (
          <Row label="Completed by">
            <span className="font-semibold">{current.snapshot.actor}</span> · {when.format(new Date(current.snapshot.completed_at * 1000))}
          </Row>
        ) : null}
      </dl>

      <div className="grid gap-2">
        <h3 className="eyebrow">Checks</h3>
        <ul aria-label="Checks" className="grid gap-1 text-sm sm:grid-cols-2">
          {review.checks.map((check) => (
            <li key={check.id} className="flex flex-wrap items-baseline gap-x-2">
              <span className="doc-ref text-ink-muted">{check.id}</span>
              <span>{checkLabel(check.id)}</span>
              <StatusText tone={checkSeverity(check)} className="text-sm">
                {checkStatusText(check)}
              </StatusText>
            </li>
          ))}
        </ul>
      </div>

      <div className="grid gap-2">
        <h3 className="eyebrow">Remaining blockers</h3>
        {review.blockers.length ? (
          <ul aria-label="Remaining blockers" className="grid gap-3">
            {review.blockers.map((blocker) => {
              const task = blocker.id === "corrections" ? review.tasks.find((item) => !["resolved", "cancelled"].includes(item.status)) : undefined;
              const href =
                blocker.id === "processing"
                  ? `/claims/${claim.id}/import`
                  : `/claims/${claim.id}/review?issue=${task ? task.check_id : blocker.id}`;
              const label = blocker.id === "processing" ? "Local checks" : blocker.id === "corrections" ? "Open corrections" : checkLabel(blocker.id);
              return (
                <li key={blocker.id} className="border-l-4 border-blocking bg-surface px-4 py-2">
                  <Link href={href} className="font-semibold">
                    {label}
                  </Link>
                  {blocker.id.startsWith("P") ? <span className="doc-ref ml-2 text-ink-muted">{blocker.id}</span> : null}
                  <ul className="mt-1 grid gap-0.5 text-sm">
                    {blocker.reasons.map((reason) => (
                      <li key={reason}>{plainReason(reason)}</li>
                    ))}
                  </ul>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-ink-muted">None. Every check and correction is resolved for version {version}.</p>
        )}
      </div>
    </section>
  );
}

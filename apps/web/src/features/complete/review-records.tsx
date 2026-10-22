import { Download, ExternalLink } from "@/components/ui/icons";
import { StatusText } from "@/components/ui/status-text";
import { checkLabel } from "@/features/case/labels";
import type { ReportRecord } from "@/lib/api-types";

const when = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });

/** Immutable review records. Only the current one exports; earlier ones stay inspectable. */
export function ReviewRecords({ reports }: { reports: ReportRecord[] }) {
  if (!reports.length) {
    return <p className="text-ink-muted">No review record yet. Completing the review saves one for the current version.</p>;
  }
  return (
    <ul aria-label="Review records" className="divide-y divide-rule-faint border-y border-rule">
      {reports.map((report) => {
        const snapshot = report.snapshot;
        return (
          <li key={report.id} className="grid gap-2 py-3">
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <p className="font-semibold">
                Review record · <span className="doc-ref">version {snapshot.bundle_version} · revision {report.revision}</span>
              </p>
              {report.stale ? (
                <StatusText tone="neutral">Stale after later changes</StatusText>
              ) : (
                <StatusText tone="passed">Current</StatusText>
              )}
            </div>
            <p className="text-sm text-ink-muted">
              Completed by {snapshot.actor} · {when.format(new Date(snapshot.completed_at * 1000))} · {snapshot.provenance}
            </p>
            {report.stale ? (
              <details>
                <summary className="min-h-11 py-2 font-semibold">Inspect this record</summary>
                <div className="grid gap-2 text-sm">
                  <p>
                    Completed by {snapshot.actor} for version {snapshot.bundle_version} under {snapshot.rule_version}. Outcome:{" "}
                    {snapshot.outcome}.
                  </p>
                  <ul className="grid gap-0.5">
                    {snapshot.checks.map((check) => (
                      <li key={check.id}>
                        <span className="doc-ref">{check.id}</span> {checkLabel(check.id)}: {check.status}
                      </li>
                    ))}
                  </ul>
                  <details>
                    <summary className="min-h-11 py-2">Raw snapshot</summary>
                    <pre className="max-h-80 overflow-auto whitespace-pre-wrap break-words border border-rule bg-surface p-3 font-mono text-xs">
                      {JSON.stringify(snapshot, null, 2)}
                    </pre>
                  </details>
                </div>
              </details>
            ) : (
              <div className="flex flex-wrap gap-x-6 gap-y-2">
                <a href={`/api/reports/${report.id}/export?format=csv`} download className="inline-flex min-h-11 items-center gap-1.5 font-semibold">
                  <Download aria-hidden="true" className="size-4" />
                  Download CSV
                </a>
                <a href={`/api/reports/${report.id}/export?format=html`} target="_blank" rel="noopener" className="inline-flex min-h-11 items-center gap-1.5 font-semibold">
                  <ExternalLink aria-hidden="true" className="size-4" />
                  Open printable record
                </a>
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

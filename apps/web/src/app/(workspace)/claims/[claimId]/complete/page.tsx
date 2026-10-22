import type { Metadata } from "next";
import Link from "next/link";

import { StatusText } from "@/components/ui/status-text";
import { getCase, getReports } from "@/features/case/case-data";
import { CompletionSummary } from "@/features/complete/completion-summary";
import { FinalizeButton } from "@/features/complete/finalize-button";
import { ReviewRecords } from "@/features/complete/review-records";
import { READY_STATE } from "@/lib/api-types";

export const metadata: Metadata = { title: "Complete" };

export default async function CompletePhasePage({ params }: { params: Promise<{ claimId: string }> }) {
  const { claimId } = await params;
  const [{ claim, bundle, review, version }, reports] = await Promise.all([getCase(claimId), getReports(claimId)]);

  if (!bundle || !review || version === null) {
    return (
      <section className="panel max-w-2xl p-6">
        <h2 className="text-lg">Nothing to complete yet</h2>
        <p className="mt-2 text-ink-muted">Import and check a version of this claim first.</p>
        <Link href={`/claims/${claim.id}/import`} className="btn btn-primary mt-4 no-underline">
          Go to Import
        </Link>
      </section>
    );
  }

  const ready = claim.state === READY_STATE;
  const current = reports.items.find((report) => !report.stale) ?? null;

  return (
    <div className="grid max-w-5xl gap-10">
      <div className="grid gap-3">
        {ready ? (
          <div className="border-l-4 border-passed bg-passed-tint px-4 py-3">
            <StatusText tone="passed" className="text-lg">
              {READY_STATE}
            </StatusText>
            <p className="mt-1 text-sm">The internal review of version {version} is complete. Submission happens in the hospital&apos;s existing system.</p>
          </div>
        ) : (
          <FinalizeButton claimId={claim.id} revision={claim.revision} bundleId={bundle.bundle_id} ruleVersion={review.rule_version} allowed={review.can_finalize} />
        )}
      </div>

      <CompletionSummary claim={claim} bundle={bundle} review={review} version={version} current={current} />

      <section aria-labelledby="records-heading" className="grid gap-3">
        <h2 id="records-heading" className="border-t-2 border-ink pt-3 text-lg">
          Review records
        </h2>
        <ReviewRecords reports={reports.items} />
      </section>
    </div>
  );
}

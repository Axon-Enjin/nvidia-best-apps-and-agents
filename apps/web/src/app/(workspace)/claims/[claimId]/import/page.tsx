import type { Metadata } from "next";
import Link from "next/link";

import { getCase } from "@/features/case/case-data";
import { resolvePhase } from "@/features/case/phase";
import { ProcessingStatus } from "@/features/case/processing-status";
import { ConfirmScans, type ScanItem } from "@/features/import-phase/confirm-scans";
import { DocumentsTable } from "@/features/import-phase/documents-table";
import { EarlierVersions } from "@/features/import-phase/earlier-versions";
import { IntakeForm } from "@/features/intake/intake-form";

export const metadata: Metadata = { title: "Import" };

export default async function ImportPhasePage({ params }: { params: Promise<{ claimId: string }> }) {
  const { claimId } = await params;
  const { claim, bundle, review, version } = await getCase(claimId);
  const phase = resolvePhase(claim, review);
  const scans: ScanItem[] =
    bundle && review
      ? bundle.documents.flatMap((document) => {
          const requirement = review.confirmations.find((item) => item.document_id === document.id);
          return requirement && requirement.pending.length ? [{ document, requirement }] : [];
        })
      : [];
  const earlier = claim.bundles.map((item) => item.version).filter((item) => item !== version).sort((a, b) => b - a);

  return (
    <div className="grid gap-10">
      {claim.latest && bundle ? (
        <ProcessingStatus key={`${claim.latest.id}:${claim.latest.status}`} claimId={claim.id} job={claim.latest} version={version} />
      ) : null}

      {phase !== "import" ? (
        <div className="flex flex-wrap items-center gap-4">
          <Link href={`/claims/${claim.id}/${phase}`} className="btn btn-primary no-underline">
            {phase === "review" ? "Continue to review" : "Continue to completion"}
          </Link>
          <p className="text-ink-muted">Version {version} is imported and checked.</p>
        </div>
      ) : null}

      {scans.length ? <ConfirmScans revision={claim.revision} items={scans} /> : null}

      {bundle ? <DocumentsTable bundle={bundle} review={review} /> : null}

      <section aria-labelledby="version-heading" className="grid gap-4">
        <div className="border-t border-ink pt-3">
          <h2 id="version-heading" className="text-lg">
            {bundle ? "Import a corrected version" : "Import the originals"}
          </h2>
          <p className="mt-1 max-w-3xl text-ink-muted">
            {bundle
              ? "Corrections to the authoritative documents happen outside this workspace. Import the corrected originals as a new version; earlier versions and decisions stay in history, and checks re-run."
              : "This claim has no originals yet. Choose its manifest and the originals it names."}
          </p>
        </div>
        <IntakeForm mode="replace" claim={claim} nested={Boolean(bundle)} />
      </section>

      <EarlierVersions claimId={claim.id} versions={earlier} />
    </div>
  );
}

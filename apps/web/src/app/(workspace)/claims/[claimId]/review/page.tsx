import type { Metadata } from "next";
import Link from "next/link";

import { getCase } from "@/features/case/case-data";
import { openTask } from "@/features/review/next-action";
import { ReviewWorkspace } from "@/features/review/review-workspace";

export const metadata: Metadata = { title: "Review" };

export default async function ReviewPhasePage({
  params,
  searchParams,
}: {
  params: Promise<{ claimId: string }>;
  searchParams: Promise<{ issue?: string | string[] }>;
}) {
  const [{ claimId }, { issue }] = await Promise.all([params, searchParams]);
  const { claim, bundle, review, version } = await getCase(claimId);

  if (!bundle || !review || version === null || claim.latest?.status !== "succeeded") {
    return (
      <section className="panel max-w-2xl p-6">
        <h2 className="text-lg">Review opens when local checks finish</h2>
        <p className="mt-2 text-ink-muted">There is no checked version of this claim yet.</p>
        <Link href={`/claims/${claim.id}/import`} className="btn btn-primary mt-4 no-underline">
          Go to Import
        </Link>
      </section>
    );
  }

  const actionable = review.checks.filter((check) => check.id !== "P10");
  const requested = typeof issue === "string" ? issue : null;
  const initialIssue =
    actionable.find((check) => check.id === requested)?.id ??
    actionable.find((check) => check.status !== "passed" || openTask(check.id, review))?.id ??
    null;

  return <ReviewWorkspace claim={claim} bundle={bundle} review={review} version={version} initialIssue={initialIssue} />;
}

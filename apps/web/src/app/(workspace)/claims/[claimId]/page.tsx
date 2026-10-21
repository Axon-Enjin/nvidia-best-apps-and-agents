import { redirect } from "next/navigation";

import { getCase } from "@/features/case/case-data";
import { resolvePhase } from "@/features/case/phase";

/** A claim link opens the phase where action is needed. */
export default async function ClaimPage({ params }: { params: Promise<{ claimId: string }> }) {
  const { claimId } = await params;
  const { claim, review } = await getCase(claimId);
  redirect(`/claims/${claim.id}/${resolvePhase(claim, review)}`);
}

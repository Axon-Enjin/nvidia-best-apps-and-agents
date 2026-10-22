import type { ReactNode } from "react";

import { getCase, getConfig } from "@/features/case/case-data";
import { CaseHeader } from "@/features/case/case-header";
import { phaseStatus } from "@/features/case/phase";
import { PhaseNav } from "@/features/case/phase-nav";

export default async function CaseLayout({ children, params }: { children: ReactNode; params: Promise<{ claimId: string }> }) {
  const { claimId } = await params;
  const [{ claim, review, version }, config] = await Promise.all([getCase(claimId), getConfig()]);
  return (
    <>
      <CaseHeader claim={claim} version={version} review={review} config={config} />
      <PhaseNav claimId={claim.id} statuses={phaseStatus(claim, review)} />
      <div className="mt-6">{children}</div>
    </>
  );
}

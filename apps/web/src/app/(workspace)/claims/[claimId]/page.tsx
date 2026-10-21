import { notFound } from "next/navigation";

import type { ClaimDetail } from "@/lib/api-types";
import { backendGet } from "@/lib/backend";

export default async function ClaimPage({ params }: { params: Promise<{ claimId: string }> }) {
  const { claimId } = await params;
  if (!/^[0-9a-f]{32}$/.test(claimId)) notFound();
  const claim = await backendGet<ClaimDetail>(`/api/claims/${claimId}`);
  return <h1 className="doc-ref text-[1.75rem]">{claim.reference}</h1>;
}

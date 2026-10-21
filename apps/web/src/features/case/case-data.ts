// Server-side reads for one claim. React `cache` shares each read between the
// case layout and its page within a single request.
import { notFound } from "next/navigation";
import { cache } from "react";

import type { AppConfig, BundleDetail, ClaimDetail, ReportList, ReviewState } from "@/lib/api-types";
import { backendGet } from "@/lib/backend";

export const getClaim = cache((id: string) => backendGet<ClaimDetail>(`/api/claims/${id}`));
export const getBundle = cache((id: string, version: number) => backendGet<BundleDetail>(`/api/claims/${id}/bundles/${version}`));
export const getReviewState = cache((id: string) => backendGet<ReviewState>(`/api/claims/${id}/review-state`));
export const getReports = cache((id: string) => backendGet<ReportList>(`/api/claims/${id}/reports`));
export const getConfig = cache(() => backendGet<AppConfig>("/api/config"));

export type CaseData = {
  claim: ClaimDetail;
  bundle: BundleDetail | null;
  review: ReviewState | null;
  version: number | null;
};

export const getCase = cache(async (id: string): Promise<CaseData> => {
  if (!/^[0-9a-f]{32}$/.test(id)) notFound();
  const claim = await getClaim(id);
  const current = claim.bundles.find((bundle) => bundle.bundle_id === claim.current_bundle_id);
  if (!current) return { claim, bundle: null, review: null, version: null };
  const [bundle, review] = await Promise.all([getBundle(id, current.version), getReviewState(id)]);
  return { claim, bundle, review, version: current.version };
});

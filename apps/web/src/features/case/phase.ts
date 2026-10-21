import { READY_STATE, type ClaimDetail, type ReviewState } from "../../lib/api-types.ts";

export type Phase = "import" | "review" | "complete";
export const PHASES: readonly Phase[] = ["import", "review", "complete"];

type ClaimLike = Pick<ClaimDetail, "current_bundle_id" | "latest" | "state" | "bundles">;

const pendingScanValues = (review: ReviewState | null) =>
  (review?.confirmations ?? []).reduce((sum, requirement) => sum + requirement.pending.length, 0);

const openIssues = (review: ReviewState) => review.checks.filter((check) => check.id !== "P10" && check.status !== "passed").length;

const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`;

/** Where a returning reviewer has something to do; completed phases are never forced again. */
export function resolvePhase(claim: ClaimLike, review: ReviewState | null): Phase {
  if (!claim.current_bundle_id || !claim.latest || claim.latest.status !== "succeeded") return "import";
  if (pendingScanValues(review) > 0) return "import";
  if (claim.state === READY_STATE || review?.can_finalize) return "complete";
  return "review";
}

export function phaseStatus(claim: ClaimLike, review: ReviewState | null): Record<Phase, string> {
  const version = claim.bundles.find((bundle) => bundle.bundle_id === claim.current_bundle_id)?.version;
  const job = claim.latest?.status;
  let importStatus = `Version ${version ?? "?"} imported`;
  if (!claim.current_bundle_id) importStatus = "Not started";
  else if (job === "queued" || job === "running") importStatus = "Processing";
  else if (job === "failed") importStatus = "Checks failed";
  else if (pendingScanValues(review) > 0) importStatus = plural(pendingScanValues(review), "scan value to confirm", "scan values to confirm");

  let reviewStatus = "Waiting for checks";
  let completeStatus = "Not ready";
  if (review && job === "succeeded") {
    const issues = openIssues(review);
    reviewStatus = issues ? plural(issues, "issue needs attention", "issues need attention") : "All checks resolved";
    if (claim.state === READY_STATE) completeStatus = "Completed";
    else if (review.can_finalize) completeStatus = "Ready to complete";
    else completeStatus = plural(review.blockers.length, "blocker remains", "blockers remain");
  } else if (claim.state === READY_STATE) {
    completeStatus = "Completed";
  }
  return { import: importStatus, review: reviewStatus, complete: completeStatus };
}

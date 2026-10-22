"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";

import { useStatus } from "@/components/ui/notice";
import { useSession } from "@/features/session/session-provider";
import { errorText } from "@/lib/api-client";
import type { ReportRecord } from "@/lib/api-types";

/** Completion is offered only when the review service allows it; it decides again on submit. */
export function FinalizeButton({
  claimId,
  revision,
  bundleId,
  ruleVersion,
  allowed,
}: {
  claimId: string;
  revision: number;
  bundleId: string;
  ruleVersion: string;
  allowed: boolean;
}) {
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const busy = useRef(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function finalize() {
    if (!allowed || busy.current) return;
    busy.current = true;
    setPending(true);
    setError(null);
    try {
      await request<ReportRecord>(`/api/claims/${claimId}/finalize`, {
        method: "POST",
        json: { expected_revision: revision, bundle_id: bundleId, rule_version: ruleVersion },
      });
      announce("Internal review record saved. Ready for final submission review.");
      router.refresh();
    } catch (failure) {
      setError(errorText(failure));
    } finally {
      busy.current = false;
      setPending(false);
    }
  }

  return (
    <div className="grid gap-2">
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          className="btn btn-primary"
          aria-disabled={!allowed || pending ? "true" : undefined}
          aria-describedby={allowed ? undefined : "complete-blocked"}
          onClick={() => void finalize()}
        >
          {pending ? "Completing…" : "Complete review"}
        </button>
        {!allowed ? (
          <p id="complete-blocked" className="text-sm font-semibold text-ink-muted">
            Resolve the remaining blockers before completing.
          </p>
        ) : (
          <p className="text-sm text-ink-muted">Saves an immutable internal review record for this version.</p>
        )}
      </div>
      {error ? (
        <p role="alert" className="border-l-4 border-blocking bg-blocking-tint px-4 py-3 font-semibold text-blocking">
          {error}
        </p>
      ) : null}
    </div>
  );
}

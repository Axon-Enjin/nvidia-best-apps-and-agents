"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CircleAlert, CircleCheck, Clock } from "@/components/ui/icons";
import { useStatus } from "@/components/ui/notice";
import { useSession } from "@/features/session/session-provider";
import type { ClaimDetail, JobSummary } from "@/lib/api-types";

import { createPoller, type PollEnd } from "./poller";

const ACTIVE = new Set(["queued", "running"]);

/** Real processing state of the latest local check run, polled while it is queued or running. */
export function ProcessingStatus({ claimId, job, version }: { claimId: string; job: JobSummary; version: number | null }) {
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const [current, setCurrent] = useState(job);
  const [ended, setEnded] = useState<PollEnd | null>(null);
  const [round, setRound] = useState(0);

  useEffect(() => {
    if (!ACTIVE.has(job.status)) return;
    const poller = createPoller<ClaimDetail>({
      fetchOnce: (signal) => request<ClaimDetail>(`/api/claims/${claimId}`, { signal }),
      isDone: (claim) => !claim.latest || !ACTIVE.has(claim.latest.status),
      onValue: (claim) => {
        if (claim.latest) setCurrent(claim.latest);
      },
      onEnd: (reason) => {
        setEnded(reason);
        if (reason === "done") {
          announce(version ? `Local checks finished for version ${version}.` : "Local checks finished.");
          router.refresh();
        }
      },
    });
    poller.start();
    return () => poller.stop();
  }, [announce, claimId, job.status, request, round, router, version]);

  const retry = () => {
    setEnded(null);
    setRound((count) => count + 1);
  };

  let icon = <Clock aria-hidden="true" className="size-5 text-ink-muted" />;
  let headline = "Queued for local checks";
  let detail = "This page updates when they finish.";
  if (current.status === "running") {
    headline = "Checks are running";
    detail = current.attempts > 1 ? `Attempt ${current.attempts}. This page updates when they finish.` : detail;
  } else if (current.status === "succeeded") {
    icon = <CircleCheck aria-hidden="true" className="size-5 text-passed" />;
    headline = `Checks complete for version ${version ?? "?"}.`;
    detail = "Every document below was read locally; nothing left this machine.";
  } else if (current.status === "failed") {
    icon = <CircleAlert aria-hidden="true" className="size-5 text-blocking" />;
    headline = `Checks failed: ${current.error ?? "the local run stopped."}`;
    detail = "Import a corrected version, or re-run checks from Review.";
  }
  if (ended === "gave_up") detail = "Still processing after two minutes.";
  if (ended === "error") detail = "Could not refresh the processing state.";

  return (
    <div className="flex flex-wrap items-start gap-3 border-l-4 border-rule bg-surface px-4 py-3">
      {icon}
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{headline}</p>
        <p className="text-sm text-ink-muted">{detail}</p>
      </div>
      {ended === "gave_up" || ended === "error" ? (
        <button type="button" className="btn btn-secondary" onClick={retry}>
          Check again
        </button>
      ) : null}
    </div>
  );
}

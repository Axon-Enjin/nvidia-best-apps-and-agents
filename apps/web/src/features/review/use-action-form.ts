"use client";

import { useRouter } from "next/navigation";
import { useRef, useState, useTransition } from "react";

import { useStatus } from "@/components/ui/notice";
import { useSession } from "@/features/session/session-provider";
import { ConflictError, errorText, SessionExpiredError } from "@/lib/api-client";
import type { ReviewActionBody, ReviewState } from "@/lib/api-types";

export type ActionContext = { claimId: string; revision: number; bundleId: string; ruleVersion: string };
export type ActionPayload = Omit<ReviewActionBody, "expected_revision" | "bundle_id" | "rule_version">;

// The revision fence and the version guard both mean "someone saved first".
const STALE = /^(Case changed|Source and rule versions must be current)/;

/**
 * Saves one review event. A second activation while saving is ignored, a stale
 * revision keeps the draft and asks for the latest version, an expired session
 * opens sign-in, and nothing is ever resubmitted automatically.
 */
export function useActionForm(context: ActionContext) {
  const router = useRouter();
  const { request } = useSession();
  const { announce } = useStatus();
  const busy = useRef(false);
  const [pending, setPending] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // "Load latest" holds the form until the refreshed case has arrived, so the next save uses the new revision.
  const [refreshing, startRefresh] = useTransition();

  async function submit(payload: ActionPayload, savedMessage: string): Promise<boolean> {
    if (busy.current) return false;
    busy.current = true;
    setPending(true);
    setError(null);
    try {
      await request<ReviewState>(`/api/claims/${context.claimId}/review-events`, {
        method: "POST",
        json: { expected_revision: context.revision, bundle_id: context.bundleId, rule_version: context.ruleVersion, ...payload },
      });
      setConflict(false);
      announce(savedMessage);
      router.refresh();
      return true;
    } catch (failure) {
      if (failure instanceof ConflictError && STALE.test(errorText(failure))) setConflict(true);
      else if (failure instanceof SessionExpiredError) setError("Your session ended. Sign in again; your draft stays here until you save.");
      else setError(errorText(failure));
      return false;
    } finally {
      busy.current = false;
      setPending(false);
    }
  }

  function loadLatest() {
    startRefresh(() => {
      setConflict(false);
      router.refresh();
    });
  }

  return { pending, conflict, refreshing, error, submit, loadLatest };
}

"use client";

import { useCallback, useRef, useState } from "react";

import { DISCARD_DRAFT, useDraftGuard } from "@/features/session/use-draft-guard";
import type { BundleDetail, ClaimDetail, ReviewState } from "@/lib/api-types";

import { CaseTools } from "./case-tools";
import { differenceMarks, evidencePages } from "./evidence";
import { EvidenceReader } from "./evidence-reader";
import { IssueDetail } from "./issue-detail";
import { IssueList } from "./issue-list";
import { openTask } from "./next-action";

/**
 * Asymmetric review composition: a compact issue list, the selected issue and
 * its next action, and a generous source-reading column that stays in view.
 */
export function ReviewWorkspace({
  claim,
  bundle,
  review,
  version,
  initialIssue,
}: {
  claim: ClaimDetail;
  bundle: BundleDetail;
  review: ReviewState;
  version: number;
  initialIssue: string | null;
}) {
  const [selected, setSelected] = useState<string | null>(initialIssue);
  const [issueDirty, setIssueDirty] = useState(false);
  const [toolsDirty, setToolsDirty] = useState(false);
  const evidence = useRef<HTMLElement>(null);
  useDraftGuard(issueDirty || toolsDirty);

  const check = review.checks.find((item) => item.id === selected) ?? null;
  const openTasks = new Set(review.checks.filter((item) => openTask(item.id, review)).map((item) => item.id));

  function select(id: string) {
    if (id === selected) return;
    if (issueDirty && !window.confirm(DISCARD_DRAFT)) return;
    setIssueDirty(false);
    setSelected(id);
    const url = new URL(window.location.href);
    url.searchParams.set("issue", id);
    window.history.replaceState(null, "", url);
  }

  const onIssueDirty = useCallback((dirty: boolean) => setIssueDirty(dirty), []);
  const onToolsDirty = useCallback((dirty: boolean) => setToolsDirty(dirty), []);
  const marks = check ? differenceMarks(check, bundle.bundle_id, review.confirmations) : [];
  const pages = check ? evidencePages(check, bundle.documents, review.confirmations, bundle.bundle_id) : [];

  return (
    <div className="grid items-start gap-x-8 gap-y-10 lg:grid-cols-[minmax(15rem,19rem)_minmax(0,1fr)] xl:grid-cols-[minmax(15rem,18rem)_minmax(20rem,27rem)_minmax(0,1fr)]">
      <div className="grid gap-6 lg:sticky lg:top-4 lg:row-span-2 lg:max-h-[calc(100dvh-2rem)] lg:overflow-y-auto xl:row-span-1">
        <nav aria-label="Issues">
          <IssueList checks={review.checks} openTasks={openTasks} selected={selected} onSelect={select} />
        </nav>
        <CaseTools claim={claim} bundle={bundle} review={review} version={version} onDirtyChange={onToolsDirty} />
      </div>

      <section aria-label="Selected issue" className="min-w-0">
        {check ? (
          <IssueDetail
            key={check.id}
            check={check}
            marks={marks}
            pages={pages}
            version={version}
            claim={claim}
            bundle={bundle}
            review={review}
            onDirtyChange={onIssueDirty}
            onViewSource={() => {
              evidence.current?.focus();
              evidence.current?.scrollIntoView({ block: "start" });
            }}
          />
        ) : (
          <p className="border-t-2 border-ink pt-3 text-ink-muted">Choose an issue to see what differs and where.</p>
        )}
      </section>

      <section
        ref={evidence}
        id="source-evidence"
        tabIndex={-1}
        aria-label="Source evidence"
        className="min-w-0 scroll-mt-4 outline-none lg:col-start-2 xl:sticky xl:top-4 xl:col-start-3 xl:row-start-1 xl:max-h-[calc(100dvh-2rem)] xl:overflow-y-auto"
      >
        {check ? <EvidenceReader key={check.id} pages={pages} version={version} claimId={claim.id} /> : null}
      </section>
    </div>
  );
}

"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { StatusText } from "@/components/ui/status-text";
import { checkLabel, checkSeverity, checkStatusText, plainReason } from "@/features/case/labels";
import type { Check } from "@/lib/api-types";

import { DifferencesTable } from "./differences-table";
import type { DifferenceMark, EvidencePage } from "./evidence";

/** What differs, why it blocks completion, and what happens next for one selected check. */
export function IssueDetail({
  check,
  marks,
  pages,
  version,
  ruleVersion,
  claimId,
  onViewSource,
  action,
}: {
  check: Check;
  marks: DifferenceMark[];
  pages: EvidencePage[];
  version: number;
  ruleVersion: string;
  claimId: string;
  onViewSource: () => void;
  action?: ReactNode;
}) {
  const needsScanConfirmation = pages.some((page) => page.needsConfirmation) && check.status !== "passed";
  return (
    <div className="grid content-start gap-6">
      <header className="grid gap-1.5 border-t-2 border-ink pt-3">
        <p className="eyebrow">
          Issue · <span className="doc-ref normal-case">{check.id}</span> · rules <span className="doc-ref normal-case">{ruleVersion}</span>
        </p>
        <h2 className="text-[1.375rem]">{checkLabel(check.id)}</h2>
        <StatusText tone={checkSeverity(check)}>{checkStatusText(check)}</StatusText>
        <a
          href="#source-evidence"
          onClick={(event) => {
            event.preventDefault();
            onViewSource();
          }}
          className="link-button justify-self-start lg:hidden"
        >
          View source
        </a>
      </header>

      {marks.length ? <DifferencesTable marks={marks} differences={check.differences} version={version} /> : null}

      {check.blocking_reasons.length ? (
        <div className="grid gap-2">
          <h3 className="eyebrow">Why this blocks completion</h3>
          <ul aria-label="Why this blocks completion" className="grid list-disc gap-1 pl-5">
            {check.blocking_reasons.map((reason) => (
              <li key={reason}>{plainReason(reason)}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-ink-muted">This check passed for version {version}. Its evidence stays available here.</p>
      )}

      {needsScanConfirmation ? (
        <section aria-label="Next action" className="grid gap-3 border-t border-rule pt-4">
          <h3 className="eyebrow">Next action</h3>
          <p>A cited document is a scan whose values are not confirmed yet. Confirm them against the original first.</p>
          <Link href={`/claims/${claimId}/import`} className="btn btn-primary justify-self-start no-underline">
            Confirm scanned values
          </Link>
        </section>
      ) : (
        action
      )}
    </div>
  );
}

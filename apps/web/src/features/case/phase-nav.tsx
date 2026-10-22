"use client";

import Link from "next/link";
import { useSelectedLayoutSegment } from "next/navigation";

import { PHASES, type Phase } from "./phase";

const LABELS: Record<Phase, string> = { import: "Import", review: "Review", complete: "Complete" };

export function PhaseNav({ claimId, statuses }: { claimId: string; statuses: Record<Phase, string> }) {
  const segment = useSelectedLayoutSegment();
  return (
    <nav aria-label="Case phases" className="mt-2">
      <ol className="grid grid-cols-3 border-b border-rule">
        {PHASES.map((phase, index) => {
          const current = segment === phase;
          return (
            <li key={phase}>
              <Link
                href={`/claims/${claimId}/${phase}`}
                aria-current={current ? "page" : undefined}
                className={`-mb-px block h-full min-h-11 border-b-2 px-2 py-2 no-underline transition-colors sm:px-4 ${
                  current ? "border-forest bg-surface text-ink" : "border-transparent text-ink-muted hover:border-rule hover:text-ink"
                }`}
              >
                <span className="flex flex-wrap items-baseline gap-x-2">
                  <span className="doc-ref text-xs">0{index + 1}</span>
                  <span className="font-semibold">{LABELS[phase]}</span>
                  <span className="basis-full text-sm md:basis-auto">{statuses[phase]}</span>
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

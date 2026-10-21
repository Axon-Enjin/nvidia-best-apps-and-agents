"use client";

import Link from "next/link";
import { useEffect } from "react";

import { StatusText, type Tone } from "@/components/ui/status-text";
import { READY_STATE, type QueueItem } from "@/lib/api-types";
import { useQueueMemory } from "@/features/session/queue-memory";

export function queueStatus(item: QueueItem): { tone: Tone; text: string } {
  if (item.status === "queued" || item.status === "running") return { tone: "neutral", text: "Processing" };
  if (!item.current_bundle_id) return { tone: "neutral", text: "No sources yet" };
  if (item.state === READY_STATE) return { tone: "passed", text: "Completed" };
  if (item.status === "failed") return { tone: "blocking", text: "Checks failed" };
  if (item.outcome === "needs_review") return { tone: "attention", text: "Needs review" };
  return { tone: "neutral", text: "Checks unavailable" };
}

const imported = new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric" });

export function QueueTable({ items, query }: { items: QueueItem[]; query: string }) {
  const { lastOpenedClaimId, rememberQuery, rememberOpened } = useQueueMemory();

  useEffect(() => {
    rememberQuery(query);
  }, [query, rememberQuery]);

  if (!items.length) {
    return (
      <div className="mt-6 border-y border-rule bg-surface px-4 py-10 text-center">
        <p className="font-semibold">No claims match. Import a claim to start a review.</p>
      </div>
    );
  }

  return (
    <table aria-label="Claims queue" className="mt-6 w-full border-collapse text-left">
      <thead>
        <tr className="border-b border-ink">
          <th scope="col" className="eyebrow py-2 pr-4">Claim</th>
          <th scope="col" className="eyebrow hidden py-2 pr-4 md:table-cell">Patient</th>
          <th scope="col" className="eyebrow py-2 pr-4">Status</th>
          <th scope="col" className="eyebrow hidden py-2 pr-4 lg:table-cell">Stage</th>
          <th scope="col" className="eyebrow hidden py-2 md:table-cell">Imported</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => {
          const status = queueStatus(item);
          const current = item.id === lastOpenedClaimId;
          return (
            <tr
              key={item.id}
              aria-current={current ? "true" : undefined}
              className={`relative border-b border-rule-faint transition-colors hover:bg-teal-tint ${current ? "bg-surface shadow-[inset_3px_0_0_var(--color-teal)]" : ""}`}
            >
              <td className="py-3 pl-3 pr-4 align-top">
                <Link
                  href={`/claims/${item.id}`}
                  onClick={() => rememberOpened(item.id)}
                  className="doc-ref text-[0.9375rem] font-semibold text-forest after:absolute after:inset-0 after:content-['']"
                >
                  {item.reference}
                </Link>
                <span className="mt-0.5 block text-sm text-ink-muted md:hidden">{item.patient_id}</span>
              </td>
              <td className="doc-ref hidden py-3 pr-4 align-top text-ink-muted md:table-cell">{item.patient_id}</td>
              <td className="py-3 pr-4 align-top">
                <StatusText tone={status.tone}>{status.text}</StatusText>
              </td>
              <td className="hidden py-3 pr-4 align-top text-ink-muted lg:table-cell">{item.state}</td>
              <td className="hidden py-3 align-top text-ink-muted md:table-cell">{imported.format(new Date(item.created_at * 1000))}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

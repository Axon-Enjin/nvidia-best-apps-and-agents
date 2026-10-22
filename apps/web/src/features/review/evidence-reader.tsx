"use client";

import Link from "next/link";
import { useId, useRef, useState, type KeyboardEvent } from "react";

import { ExternalLink } from "@/components/ui/icons";
import { documentLabel } from "@/features/case/labels";
import { originalHref } from "@/features/import-phase/documents-table";

import { MarkBadge } from "./differences-table";
import { segmentText, type EvidencePage } from "./evidence";

type DocumentGroup = { id: string; pages: EvidencePage[]; letters: string[] };

function groupByDocument(pages: EvidencePage[]): DocumentGroup[] {
  const groups = new Map<string, DocumentGroup>();
  for (const page of pages) {
    const group = groups.get(page.document.id) ?? { id: page.document.id, pages: [], letters: [] };
    group.pages.push(page);
    for (const highlight of page.highlights) {
      if (highlight.letter && !group.letters.includes(highlight.letter)) group.letters.push(highlight.letter);
    }
    groups.set(page.document.id, group);
  }
  return [...groups.values()];
}

/** Tabbed source reader: one document at a time, its page, version and highlighted values. */
export function EvidenceReader({ pages, version, claimId }: { pages: EvidencePage[]; version: number; claimId: string }) {
  const groups = groupByDocument(pages);
  const [active, setActive] = useState(0);
  const [pageIndex, setPageIndex] = useState(0);
  const [view, setView] = useState<"text" | "original">("text");
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const base = useId();

  const group = groups[Math.min(active, groups.length - 1)];
  const entry = group?.pages[Math.min(pageIndex, group.pages.length - 1)];

  function choose(index: number) {
    setActive(index);
    setPageIndex(0);
    tabs.current[index]?.focus();
  }

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const last = groups.length - 1;
    const moves: Record<string, number> = { ArrowRight: active + 1 > last ? 0 : active + 1, ArrowLeft: active - 1 < 0 ? last : active - 1, Home: 0, End: last };
    const next = moves[event.key];
    if (next === undefined) return;
    event.preventDefault();
    choose(next);
  }

  return (
    <div className="grid content-start gap-3">
      <p className="eyebrow">Source evidence</p>
      {!group || !entry ? (
        <p className="text-ink-muted">No source passage is linked to this check.</p>
      ) : (
        <>
          <div role="tablist" aria-label="Source documents" onKeyDown={onKeyDown} className="flex flex-wrap gap-x-1 border-b border-ink">
            {groups.map((item, index) => {
              const first = item.pages[0];
              const selected = index === active;
              return (
                <button
                  key={item.id}
                  ref={(element) => {
                    tabs.current[index] = element;
                  }}
                  type="button"
                  role="tab"
                  id={`${base}-tab-${index}`}
                  aria-selected={selected}
                  aria-controls={`${base}-panel`}
                  tabIndex={selected ? 0 : -1}
                  onClick={() => choose(index)}
                  className={`-mb-px inline-flex min-h-11 items-center gap-2 border-b-2 px-2.5 text-sm font-semibold transition-colors duration-150 ${
                    selected ? "border-forest text-ink" : "border-transparent text-ink-muted hover:text-ink"
                  }`}
                >
                  {first ? documentLabel(first.document.type, first.document.filename) : item.id}
                  {item.letters.map((letter) => (
                    <MarkBadge key={letter} letter={letter} />
                  ))}
                </button>
              );
            })}
          </div>

          <div role="tabpanel" id={`${base}-panel`} aria-labelledby={`${base}-tab-${active}`} className="grid gap-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="doc-ref uppercase">
                {documentLabel(entry.document.type, entry.document.filename)} · page {entry.page} · version {version}
              </p>
              <div className="flex flex-wrap items-center gap-1">
                {(["text", "original"] as const).map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    aria-pressed={view === mode}
                    onClick={() => setView(mode)}
                    className={`min-h-11 rounded-[var(--radius-control)] border px-3 text-sm font-semibold transition-colors ${
                      view === mode ? "border-forest bg-forest text-white" : "border-rule bg-surface text-forest hover:bg-teal-tint"
                    }`}
                  >
                    {mode === "text" ? "Extracted text" : "Original"}
                  </button>
                ))}
              </div>
            </div>

            {group.pages.length > 1 ? (
              <div role="group" aria-label="Pages" className="flex flex-wrap gap-1">
                {group.pages.map((item, index) => (
                  <button
                    key={item.page}
                    type="button"
                    aria-pressed={index === pageIndex}
                    onClick={() => setPageIndex(index)}
                    className="min-h-11 border border-rule bg-surface px-3 text-sm aria-pressed:border-forest aria-pressed:font-semibold"
                  >
                    Page {item.page}
                  </button>
                ))}
              </div>
            ) : null}

            {entry.needsConfirmation ? (
              <div className="border-l-4 border-attention bg-attention-tint px-4 py-3">
                <p className="font-semibold text-attention">This scan needs confirmation before its values count.</p>
                <p className="mt-1 text-sm">
                  Its OCR readings are not evidence until each one is confirmed against the printed original.{" "}
                  <Link href={`/claims/${claimId}/import`}>Confirm scanned values</Link>
                </p>
              </div>
            ) : view === "text" ? (
              <pre
                aria-label="Source text"
                tabIndex={0}
                className="max-h-[34rem] overflow-auto whitespace-pre-wrap break-words border border-rule bg-surface p-4 font-mono text-[0.8125rem] leading-6"
              >
                {segmentText(entry.document.extraction.pages[entry.page - 1] ?? "", entry.highlights).map((segment, index) =>
                  segment.marked ? (
                    <mark key={index} data-mark={segment.letter ?? undefined} className="evidence-mark">
                      {segment.text}
                    </mark>
                  ) : (
                    <span key={index}>{segment.text}</span>
                  ),
                )}
                {(entry.document.extraction.pages[entry.page - 1] ?? "") ? null : "No readable text. Inspect the original or replace it."}
              </pre>
            ) : entry.document.content_type.startsWith("image/") ? (
              // Authenticated same-origin preview of the stored original.
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={`/api/documents/${entry.document.id}/preview`}
                alt={`Original ${documentLabel(entry.document.type, entry.document.filename)}, page ${entry.page}`}
                className="w-full border border-rule bg-surface object-contain"
              />
            ) : (
              <p className="panel p-4">
                {entry.document.content_type === "application/pdf"
                  ? "This original is a PDF. Open it beside this page to compare."
                  : "This original is a text file; its full content is shown under Extracted text."}
              </p>
            )}

            <a href={originalHref(entry.document)} target="_blank" rel="noopener" className="inline-flex items-center gap-1 justify-self-start text-sm font-semibold">
              Open original
              <ExternalLink aria-hidden="true" className="size-4" />
            </a>
          </div>
        </>
      )}
    </div>
  );
}

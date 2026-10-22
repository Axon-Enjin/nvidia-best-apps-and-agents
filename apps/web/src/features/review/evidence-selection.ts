import type { EvidenceRef } from "../../lib/api-types.ts";

export type EvidenceSelection = Record<string, { checked: boolean; pages: string }>;

export function parsePages(value: string, pageCount: number): number[] | string {
  const trimmed = value.trim();
  if (!/^\d+(\s*,\s*\d+)*$/.test(trimmed)) return "Enter page numbers separated by commas, such as 1, 2.";
  const pages = [...new Set(trimmed.split(",").map((part) => Number(part.trim())))];
  if (pages.some((page) => page < 1 || page > pageCount)) return `Pages must be between 1 and ${pageCount}.`;
  return pages;
}

/** Evidence the reviewer chose: one anchor per selected page of each checked document. */
export function selectionAnchors(
  selection: EvidenceSelection,
  documents: { id: string; page_count: number }[],
): { anchors: EvidenceRef[]; errors: Record<string, string> } {
  const anchors: EvidenceRef[] = [];
  const errors: Record<string, string> = {};
  for (const document of documents) {
    const choice = selection[document.id];
    if (!choice?.checked) continue;
    const pages = parsePages(choice.pages, document.page_count);
    if (typeof pages === "string") errors[document.id] = pages;
    else anchors.push(...pages.map((page) => ({ document_id: document.id, page })));
  }
  return { anchors, errors };
}

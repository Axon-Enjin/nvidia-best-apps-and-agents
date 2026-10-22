import type { Check, ConfirmationRequirement, SourceDocument } from "../../lib/api-types.ts";

// The link between an issue and its evidence. Letters mark distinct values the
// review service reported as differing; the same letter appears in the
// "What differs" table and on the highlighted value in the source text. Only
// connections the service established get a letter.

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

// Checks whose anchors name specific fields (profile.py `names=`). Other checks
// cite whole documents, so highlighting every labelled value there is noise.
const FIELD_SCOPED = new Set(["P01", "P04", "P05", "P08"]);

export type MarkSource = { documentId: string; type: string; page: number | null };
export type DifferenceMark = { letter: string; field: string; value: string; sources: MarkSource[] };
export type Highlight = { value: string; letter: string | null };
export type EvidencePage = { document: SourceDocument; page: number; highlights: Highlight[]; needsConfirmation: boolean };
export type Segment = { text: string; letter: string | null; marked: boolean };

const normalize = (value: string) => value.split(/\s+/).filter(Boolean).join(" ").toLowerCase();

function awaitingConfirmation(confirmations: ConfirmationRequirement[]): Set<string> {
  return new Set(confirmations.filter((item) => item.status === "needs_confirmation").map((item) => item.document_id));
}

export function differenceMarks(check: Check, bundleId: string, confirmations: ConfirmationRequirement[] = []): DifferenceMark[] {
  const unconfirmed = awaitingConfirmation(confirmations);
  const marks = new Map<string, DifferenceMark>();
  for (const difference of check.differences) {
    for (const source of difference.sources) {
      if (source.bundle_id !== bundleId || unconfirmed.has(source.document_id)) continue;
      const key = `${difference.field}\u0000${normalize(source.value)}`;
      let mark = marks.get(key);
      if (!mark) {
        mark = { letter: LETTERS[marks.size] ?? `${marks.size + 1}`, field: difference.field, value: source.value, sources: [] };
        marks.set(key, mark);
      }
      mark.sources.push({ documentId: source.document_id, type: source.type, page: source.page });
    }
  }
  return [...marks.values()];
}

export function evidencePages(
  check: Check,
  documents: SourceDocument[],
  confirmations: ConfirmationRequirement[],
  bundleId: string,
): EvidencePage[] {
  const unconfirmed = awaitingConfirmation(confirmations);
  const pages = new Map<string, EvidencePage>();

  function add(documentId: string, page: number, highlight: Highlight) {
    const document = documents.find((item) => item.id === documentId);
    if (!document) return;
    const key = `${documentId}:${page}`;
    let entry = pages.get(key);
    if (!entry) {
      entry = { document, page, highlights: [], needsConfirmation: unconfirmed.has(documentId) };
      pages.set(key, entry);
    }
    if (entry.needsConfirmation || !highlight.value) return;
    if (!entry.highlights.some((existing) => normalize(existing.value) === normalize(highlight.value))) entry.highlights.push(highlight);
  }

  for (const mark of differenceMarks(check, bundleId, confirmations)) {
    for (const source of mark.sources) {
      if (source.page !== null) add(source.documentId, source.page, { value: mark.value, letter: mark.letter });
    }
  }
  const highlightFields = FIELD_SCOPED.has(check.id);
  for (const anchor of check.anchors) {
    if (anchor.bundle_id === bundleId) add(anchor.document_id, anchor.page, { value: highlightFields ? anchor.value : "", letter: null });
  }
  return [...pages.values()];
}

/** Splits source text so the first occurrence of each highlighted value can be marked. */
export function segmentText(text: string, highlights: Highlight[]): Segment[] {
  const ranges: { start: number; end: number; letter: string | null }[] = [];
  for (const highlight of highlights) {
    if (!highlight.value) continue;
    let from = 0;
    while (from <= text.length) {
      const start = text.indexOf(highlight.value, from);
      if (start < 0) break;
      const end = start + highlight.value.length;
      if (!ranges.some((range) => start < range.end && end > range.start)) {
        ranges.push({ start, end, letter: highlight.letter });
        break;
      }
      from = start + 1;
    }
  }
  ranges.sort((a, b) => a.start - b.start);
  const segments: Segment[] = [];
  let cursor = 0;
  for (const range of ranges) {
    if (range.start > cursor) segments.push({ text: text.slice(cursor, range.start), letter: null, marked: false });
    segments.push({ text: text.slice(range.start, range.end), letter: range.letter, marked: true });
    cursor = range.end;
  }
  if (cursor < text.length || segments.length === 0) segments.push({ text: text.slice(cursor), letter: null, marked: false });
  return segments;
}

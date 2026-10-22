import assert from "node:assert/strict";
import { test } from "node:test";

import type { Check, ConfirmationRequirement, SourceDocument } from "../../lib/api-types.ts";
import { differenceMarks, evidencePages, segmentText } from "./evidence.ts";

const TYPES = ["cf2", "cf4", "cf5", "esoa", "discharge", "csf", "eligibility"];

function document(type: string, discharge: string): SourceDocument {
  const text = `Patient ID: SYN-PATIENT-1\nAdmission Date: 2026-10-10\nDischarge Date: ${discharge}\n`;
  return {
    id: `doc-${type}`, type, filename: `${type}.txt`, sha256: "0", byte_count: text.length, content_type: "text/plain",
    page_count: 1, status: "readable", problems: [],
    extraction: {
      fields: { discharge_date: discharge, admission_date: "2026-10-10" },
      anchors: [
        { field: "admission_date", value: "2026-10-10", page: 1, line: 2 },
        { field: "discharge_date", value: discharge, page: 1, line: 3 },
      ],
      pages: [text], extractor: "local-text/1",
    },
  };
}

const documents = TYPES.map((type) => document(type, type === "discharge" ? "2026-10-15" : "2026-10-14"));

const p05: Check = {
  id: "P05", label: "Dates and disposition", status: "flagged",
  blocking_reasons: ["Conflicting discharge_date values across sources."],
  anchors: documents.flatMap((doc) => doc.extraction.anchors.map((anchor) => ({ ...anchor, bundle_id: "b1", document_id: doc.id }))),
  differences: [{
    field: "discharge_date", expected: null,
    sources: [
      ...documents.map((doc) => ({ document_id: doc.id, type: doc.type, bundle_id: "b1", value: doc.extraction.fields.discharge_date ?? "", page: 1 })),
      { document_id: "old", type: "cf2", bundle_id: "b0", value: "2026-01-01", page: 1 },
    ],
  }],
};

test("differenceMarks letters each distinct value and lists where it appears", () => {
  const marks = differenceMarks(p05, "b1");
  assert.deepEqual(marks.map((mark) => [mark.letter, mark.value, mark.sources.length]), [["A", "2026-10-14", 6], ["B", "2026-10-15", 1]]);
  assert.equal(marks[1]?.sources[0]?.documentId, "doc-discharge");
  assert.ok(marks.every((mark) => mark.field === "discharge_date"));
});

test("evidencePages lists difference pages first and letters their values", () => {
  const pages = evidencePages(p05, documents, [], "b1");
  assert.equal(pages.length, 7);
  const discharge = pages.find((page) => page.document.id === "doc-discharge");
  assert.deepEqual(discharge?.highlights, [
    { value: "2026-10-15", letter: "B" },
    { value: "2026-10-10", letter: null },
  ]);
  assert.equal(pages[0]?.document.id, "doc-cf2");
});

test("a scan awaiting confirmation is cited without highlights", () => {
  const confirmations: ConfirmationRequirement[] = [
    { document_id: "doc-cf2", type: "cf2", status: "needs_confirmation", pending: ["discharge_date"], confirmed: {}, fields: [] },
  ];
  const pages = evidencePages(p05, documents, confirmations, "b1");
  const scan = pages.find((page) => page.document.id === "doc-cf2");
  assert.equal(scan?.needsConfirmation, true);
  assert.deepEqual(scan?.highlights, []);
  assert.ok(!differenceMarks(p05, "b1", confirmations).some((mark) => mark.sources.some((source) => source.documentId === "doc-cf2")));
});

test("segmentText marks only the first occurrence of each value, without overlap", () => {
  const segments = segmentText("A 2026-10-15 then 2026-10-15 and 2026-10-10", [
    { value: "2026-10-15", letter: "B" },
    { value: "2026-10-10", letter: null },
    { value: "", letter: null },
  ]);
  assert.deepEqual(segments, [
    { text: "A ", letter: null, marked: false },
    { text: "2026-10-15", letter: "B", marked: true },
    { text: " then 2026-10-15 and ", letter: null, marked: false },
    { text: "2026-10-10", letter: null, marked: true },
  ]);
  assert.deepEqual(segmentText("nothing here", [{ value: "absent", letter: "A" }]), [{ text: "nothing here", letter: null, marked: false }]);
});

import assert from "node:assert/strict";
import { test } from "node:test";

import { parsePages, selectionAnchors } from "./evidence-selection.ts";

test("page lists are whole numbers within the document", () => {
  assert.deepEqual(parsePages("1, 2", 3), [1, 2]);
  assert.deepEqual(parsePages(" 2,2 ", 3), [2]);
  assert.equal(parsePages("0", 3), "Pages must be between 1 and 3.");
  assert.equal(parsePages("4", 3), "Pages must be between 1 and 3.");
  assert.equal(parsePages("one", 3), "Enter page numbers separated by commas, such as 1, 2.");
  assert.equal(parsePages("", 3), "Enter page numbers separated by commas, such as 1, 2.");
});

test("only checked documents become evidence, one anchor per page", () => {
  const documents = [{ id: "a", page_count: 2 }, { id: "b", page_count: 1 }, { id: "c", page_count: 5 }];
  const result = selectionAnchors(
    { a: { checked: true, pages: "1, 2" }, b: { checked: false, pages: "1" }, c: { checked: true, pages: "9" } },
    documents,
  );
  assert.deepEqual(result.anchors, [{ document_id: "a", page: 1 }, { document_id: "a", page: 2 }]);
  assert.deepEqual(result.errors, { c: "Pages must be between 1 and 5." });
});

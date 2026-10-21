import assert from "node:assert/strict";
import { test } from "node:test";

import { parseQueueParams, queueSearch, type QueueParams } from "./queue-params.ts";

test("unknown views fall back to all", () => {
  assert.equal(parseQueueParams({ view: "everything" }).view, "all");
  assert.equal(parseQueueParams({ view: ["needs_review", "incomplete"] }).view, "needs_review");
  assert.equal(parseQueueParams({}).view, "all");
});

test("pages are positive whole numbers", () => {
  for (const page of ["0", "-1", "abc", "1.5", ""]) {
    assert.equal(parseQueueParams({ page }).page, 1, page);
  }
  assert.equal(parseQueueParams({ page: "3" }).page, 3);
});

test("search is trimmed and capped at 200 characters", () => {
  assert.equal(parseQueueParams({ q: "  SYN  " }).q, "SYN");
  assert.equal(parseQueueParams({ q: "x".repeat(300) }).q.length, 200);
});

test("serialization omits defaults and round-trips", () => {
  assert.equal(queueSearch({ view: "all", q: "", page: 1 }), "");
  const params: QueueParams = { view: "needs_review", q: "SYN CLAIM", page: 2 };
  assert.deepEqual(parseQueueParams(new URLSearchParams(queueSearch(params))), params);
});

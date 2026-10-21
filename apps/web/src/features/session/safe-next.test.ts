import assert from "node:assert/strict";
import { test } from "node:test";

import { safeNextPath } from "./safe-next.ts";

test("keeps in-app page paths", () => {
  assert.equal(safeNextPath("/claims/abc"), "/claims/abc");
  assert.equal(safeNextPath("/claims?view=incomplete"), "/claims?view=incomplete");
  assert.equal(safeNextPath("/claims/abc/review?issue=P05"), "/claims/abc/review?issue=P05");
});

test("sends anything else to the claims queue", () => {
  for (const value of [
    "//evil.example",
    "https://evil.example",
    "/\\evil.example",
    "/api/session",
    "/api",
    "javascript:alert(1)",
    "claims",
    "/claims\nSet-Cookie:x",
    "",
    null,
    undefined,
  ]) {
    assert.equal(safeNextPath(value), "/claims", String(value));
  }
});

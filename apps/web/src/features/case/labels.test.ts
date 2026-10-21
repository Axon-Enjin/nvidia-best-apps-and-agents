import assert from "node:assert/strict";
import { test } from "node:test";

import { documentLabel } from "./labels.ts";

test("document types read as plain names", () => {
  assert.equal(documentLabel("cf2"), "CF2 claim summary");
  assert.equal(documentLabel("discharge"), "Discharge summary");
  assert.equal(documentLabel("esoa"), "Statement of account (eSOA)");
  assert.equal(documentLabel("attachment", "lab-result.pdf"), "Attachment lab-result.pdf");
  assert.equal(documentLabel("unknown_kind"), "UNKNOWN_KIND");
});

import assert from "node:assert/strict";
import { test } from "node:test";

import type { RequestOptions } from "../../lib/api-client.ts";
import type { Manifest } from "./manifest.ts";
import { ImportFailure, submitImport } from "./submit-import.ts";

const manifest: Manifest = {
  facility_id: "F",
  encounter_ref: "E",
  claim_ref: "C",
  patient_id: "P",
  documents: [
    { type: "cf2", filename: "cf2.txt", sha256: "a".repeat(64) },
    { type: "cf4", filename: "cf4.txt", sha256: "b".repeat(64) },
  ],
};
const files = [new File(["four"], "cf4.txt"), new File(["two"], "cf2.txt")];
const receipt = { case_id: "case-1", bundle_id: "b", version: 1, revision: 1, import_job_id: "j", coverage: [] };

type Call = { path: string; options: RequestOptions };

function requester(failUpload = false) {
  const calls: Call[] = [];
  const request = async <T,>(path: string, options: RequestOptions = {}): Promise<T> => {
    calls.push({ path, options });
    if (path === "/api/cases") return { id: "case-1", revision: 0 } as T;
    if (path === "/api/claims/case-1") return { id: "case-1", revision: 0 } as T;
    if (path.endsWith("/bundles")) {
      if (failUpload) throw new Error("connection dropped");
      return receipt as T;
    }
    throw new Error(`unexpected ${path}`);
  };
  return { request, calls };
}

test("creates the case once, then uploads files in manifest order with the key", async () => {
  const { request, calls } = requester();
  const result = await submitImport({ manifest, files, idempotencyKey: "key-1" }, request);
  assert.equal(result.caseId, "case-1");
  assert.deepEqual(calls.map((call) => call.path), ["/api/cases", "/api/claims/case-1/bundles"]);
  const upload = calls[1]?.options;
  assert.equal(upload?.headers?.["Idempotency-Key"], "key-1");
  assert.deepEqual(upload?.form?.getAll("files").map((file) => (file as File).name), ["cf2.txt", "cf4.txt"]);
  assert.equal(upload?.form?.get("expected_revision"), "0");
  assert.deepEqual(JSON.parse(String(upload?.form?.get("manifest"))), manifest);
});

test("a retry with the created case never creates another", async () => {
  const { request, calls } = requester();
  await submitImport({ manifest, files, idempotencyKey: "key-1", createdCaseId: "case-1" }, request);
  assert.deepEqual(calls.map((call) => call.path), ["/api/claims/case-1", "/api/claims/case-1/bundles"]);
});

test("a failed upload reports the created case so the retry can reuse it", async () => {
  const { request } = requester(true);
  await assert.rejects(submitImport({ manifest, files, idempotencyKey: "key-1" }, request), (error: unknown) => {
    assert.ok(error instanceof ImportFailure);
    assert.equal(error.caseId, "case-1");
    return true;
  });
});

test("a corrected version uses the existing claim and revision", async () => {
  const { request, calls } = requester();
  await submitImport({ manifest, files, idempotencyKey: "key-2", existing: { id: "case-1", revision: 7 } }, request);
  assert.deepEqual(calls.map((call) => call.path), ["/api/claims/case-1/bundles"]);
  assert.equal(calls[0]?.options.form?.get("expected_revision"), "7");
});

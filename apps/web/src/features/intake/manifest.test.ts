import assert from "node:assert/strict";
import { test } from "node:test";

import { filesInManifestOrder, identityMismatches, matchFiles, parseManifest, type Manifest } from "./manifest.ts";

const manifest: Manifest = {
  facility_id: "SYN-FACILITY",
  encounter_ref: "SYN-ENCOUNTER-1",
  claim_ref: "SYN-CLAIM-1",
  patient_id: "SYN-PATIENT-1",
  documents: [
    { type: "cf2", filename: "cf2.txt", sha256: "a".repeat(64) },
    { type: "cf4", filename: "cf4.txt", sha256: "b".repeat(64) },
  ],
};

test("parseManifest rejects invalid JSON and missing members", () => {
  assert.ok("error" in parseManifest("{not json"));
  assert.ok("error" in parseManifest(JSON.stringify({ ...manifest, documents: undefined })));
  assert.ok("error" in parseManifest(JSON.stringify({ ...manifest, claim_ref: "" })));
  assert.ok("error" in parseManifest(JSON.stringify({ ...manifest, documents: [{ type: "cf2" }] })));
  const parsed = parseManifest(JSON.stringify(manifest));
  assert.ok("manifest" in parsed && parsed.manifest.documents.length === 2);
});

test("matchFiles reports each manifest row and blocks until every row is selected", () => {
  const none = matchFiles(manifest, []);
  assert.deepEqual(none.rows.map((row) => row.status), ["missing", "missing"]);
  assert.equal(none.ready, false);

  const wrong = matchFiles(manifest, [{ name: "cf2.txt", sha256: "c".repeat(64) }, { name: "cf4.txt", sha256: "b".repeat(64) }]);
  assert.deepEqual(wrong.rows.map((row) => row.status), ["hash_mismatch", "selected"]);
  assert.equal(wrong.ready, false);

  const twice = matchFiles(manifest, [
    { name: "cf2.txt", sha256: "a".repeat(64) },
    { name: "cf2.txt", sha256: "a".repeat(64) },
    { name: "cf4.txt", sha256: "b".repeat(64) },
  ]);
  assert.equal(twice.rows[0]?.status, "duplicate");

  const extra = matchFiles(manifest, [
    { name: "cf2.txt", sha256: "a".repeat(64) },
    { name: "cf4.txt", sha256: "b".repeat(64) },
    { name: "notes.txt", sha256: "d".repeat(64) },
  ]);
  assert.deepEqual(extra.extras, ["notes.txt"]);
  assert.equal(extra.ready, false);

  const exact = matchFiles(manifest, [{ name: "cf4.txt", sha256: "b".repeat(64) }, { name: "cf2.txt", sha256: "A".repeat(64) }]);
  assert.deepEqual(exact.rows.map((row) => row.status), ["selected", "selected"]);
  assert.equal(exact.ready, true);
});

test("identityMismatches names the fields that differ from the claim", () => {
  const claim = { facility_id: "SYN-FACILITY", encounter_ref: "SYN-ENCOUNTER-1", claim_ref: "OTHER", patient_id: "SYN-PATIENT-1" };
  assert.deepEqual(identityMismatches(manifest, claim), ["Claim reference"]);
  assert.deepEqual(identityMismatches(manifest, { ...claim, claim_ref: "SYN-CLAIM-1" }), []);
});

test("filesInManifestOrder follows the manifest", () => {
  const files = [{ name: "cf4.txt" }, { name: "cf2.txt" }];
  assert.deepEqual(filesInManifestOrder(manifest, files).map((file) => file.name), ["cf2.txt", "cf4.txt"]);
});

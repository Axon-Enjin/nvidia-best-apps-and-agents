// The manifest contract is explicit: the reviewer's manifest names each
// original by type, filename and SHA-256. Nothing here guesses a mapping;
// the review service re-verifies every value on import.

export type ManifestDocument = { type: string; filename: string; sha256: string };
export type Manifest = {
  facility_id: string;
  encounter_ref: string;
  claim_ref: string;
  patient_id: string;
  documents: ManifestDocument[];
};

export const IDENTITY_FIELDS = [
  ["facility_id", "Facility ID"],
  ["encounter_ref", "Encounter reference"],
  ["claim_ref", "Claim reference"],
  ["patient_id", "Patient ID"],
] as const;

export type RowStatus = "selected" | "missing" | "hash_mismatch" | "duplicate";
export type ManifestRow = ManifestDocument & { status: RowStatus };
export type FileMatch = { rows: ManifestRow[]; extras: string[]; ready: boolean };

const text = (value: unknown): value is string => typeof value === "string" && value.trim() !== "";

export function parseManifest(source: string): { manifest: Manifest } | { error: string } {
  let value: unknown;
  try {
    value = JSON.parse(source);
  } catch {
    return { error: "This manifest is not valid JSON." };
  }
  if (!value || typeof value !== "object") return { error: "This manifest is not a JSON object." };
  const record = value as Record<string, unknown>;
  const missing = IDENTITY_FIELDS.filter(([key]) => !text(record[key])).map(([, label]) => label);
  if (missing.length) return { error: `The manifest is missing ${missing.join(", ")}.` };
  const documents = record.documents;
  if (!Array.isArray(documents) || documents.length === 0) return { error: "The manifest names no documents." };
  const valid = documents.every(
    (item) => item && typeof item === "object" && text(item.type) && text(item.filename) && text(item.sha256),
  );
  if (!valid) return { error: "Each manifest document needs a type, filename and SHA-256." };
  return { manifest: value as Manifest };
}

export function matchFiles(manifest: Manifest, files: { name: string; sha256: string }[]): FileMatch {
  const rows = manifest.documents.map((member): ManifestRow => {
    const named = files.filter((file) => file.name === member.filename);
    if (named.length === 0) return { ...member, status: "missing" };
    if (named.length > 1) return { ...member, status: "duplicate" };
    const matches = named[0]?.sha256.toLowerCase() === member.sha256.toLowerCase();
    return { ...member, status: matches ? "selected" : "hash_mismatch" };
  });
  const declared = new Set(manifest.documents.map((member) => member.filename));
  const extras = [...new Set(files.map((file) => file.name).filter((name) => !declared.has(name)))];
  return { rows, extras, ready: rows.length > 0 && extras.length === 0 && rows.every((row) => row.status === "selected") };
}

export function identityMismatches(manifest: Manifest, claim: Pick<Manifest, "facility_id" | "encounter_ref" | "claim_ref" | "patient_id">): string[] {
  return IDENTITY_FIELDS.filter(([key]) => manifest[key] !== claim[key]).map(([, label]) => label);
}

export function filesInManifestOrder<T extends { name: string }>(manifest: Manifest, files: T[]): T[] {
  return manifest.documents
    .map((member) => files.find((file) => file.name === member.filename))
    .filter((file): file is T => file !== undefined);
}

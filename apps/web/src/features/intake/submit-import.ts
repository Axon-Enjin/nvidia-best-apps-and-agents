import type { RequestOptions } from "../../lib/api-client.ts";
import type { BundleReceipt, CaseRecord } from "../../lib/api-types.ts";
import { filesInManifestOrder, type Manifest } from "./manifest.ts";

export type Requester = <T>(path: string, options?: RequestOptions) => Promise<T>;

/** An upload failed after the claim record was created; retrying must reuse `caseId`. */
export class ImportFailure extends Error {
  readonly caseId: string;
  readonly reason: unknown;

  constructor(caseId: string, reason: unknown) {
    super(reason instanceof Error ? reason.message : "The upload did not finish.");
    this.name = "ImportFailure";
    this.caseId = caseId;
    this.reason = reason;
  }
}

export async function submitImport(
  input: {
    manifest: Manifest;
    files: File[];
    idempotencyKey: string;
    existing?: { id: string; revision: number };
    createdCaseId?: string;
  },
  request: Requester,
): Promise<{ caseId: string; receipt: BundleReceipt }> {
  const { manifest } = input;
  let caseId: string;
  let revision: number;
  if (input.existing) {
    ({ id: caseId, revision } = input.existing);
  } else if (input.createdCaseId) {
    caseId = input.createdCaseId;
    revision = (await request<CaseRecord>(`/api/claims/${caseId}`)).revision;
  } else {
    const created = await request<CaseRecord>("/api/cases", {
      method: "POST",
      json: {
        facility_id: manifest.facility_id,
        encounter_ref: manifest.encounter_ref,
        claim_ref: manifest.claim_ref,
        patient_id: manifest.patient_id,
      },
    });
    caseId = created.id;
    revision = created.revision;
  }

  const form = new FormData();
  form.append("manifest", JSON.stringify(manifest));
  form.append("expected_revision", String(revision));
  for (const file of filesInManifestOrder(manifest, input.files)) form.append("files", file, file.name);
  try {
    const receipt = await request<BundleReceipt>(`/api/claims/${caseId}/bundles`, {
      method: "POST",
      form,
      headers: { "Idempotency-Key": input.idempotencyKey },
    });
    return { caseId, receipt };
  } catch (error) {
    if (input.existing) throw error;
    throw new ImportFailure(caseId, error);
  }
}

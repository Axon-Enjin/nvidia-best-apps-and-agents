import hashlib
import json

ANCHORS = {"facility_id": "SYN-FACILITY", "encounter_ref": "SYN-ENCOUNTER-1",
           "claim_ref": "SYN-CLAIM-1", "patient_id": "SYN-PATIENT-1"}
TYPES = ("cf2", "cf4", "cf5", "esoa", "discharge", "csf", "eligibility")


def create_case(client):
    response = client.post("/api/cases", json=ANCHORS)
    assert response.status_code == 201, response.text
    return response.json()


def bundle_files():
    identity = "Facility ID: SYN-FACILITY\nEncounter Ref: SYN-ENCOUNTER-1\nClaim Ref: SYN-CLAIM-1\nPatient ID: SYN-PATIENT-1\n"
    return [(f"{kind}.txt", identity.encode()) for kind in TYPES]


def import_files(client, case_id, files=None, revision=0, key="import-test-1", anchors=None, types=None):
    files = bundle_files() if files is None else files
    kinds = types or TYPES
    manifest = {**(anchors or ANCHORS), "documents": [
        {"type": kind, "filename": filename, "sha256": hashlib.sha256(content).hexdigest()}
        for kind, (filename, content) in zip(kinds, files, strict=True)]}
    return client.post(f"/api/claims/{case_id}/bundles", data={"manifest": json.dumps(manifest), "expected_revision": str(revision)},
                       files=[("files", (name, content, "application/octet-stream")) for name, content in files],
                       headers={"Idempotency-Key": key})

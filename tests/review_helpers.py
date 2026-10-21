
from sentinel.samples import development_bundle
from sentinel.worker import process_one
from tests.bundle_helpers import create_case, import_files


def seeded(context, label="complete"):
    client, db, settings = context
    case = create_case(client)
    files, _ = development_bundle(label)
    receipt = import_files(client, case["id"], files).json()
    assert process_one(db, settings)
    bundle = client.get(f"/api/claims/{case['id']}/bundles/1").json()
    return case["id"], bundle, receipt


def action(client, case_id, kind, **payload):
    case = client.get(f"/api/claims/{case_id}").json()
    return client.post(f"/api/claims/{case_id}/review-events", json={
        "expected_revision": case["revision"], "bundle_id": case["current_bundle_id"],
        "rule_version": "SAMPLE-ADULT-MEDICAL-1/1", "action": kind, **payload})


def anchors(bundle, kinds=None):
    return [{"document_id": d["id"], "page": 1} for d in bundle["documents"] if kinds is None or d["type"] in kinds]


def corrected(context, case_id):
    client, db, settings = context
    case = client.get(f"/api/claims/{case_id}").json()
    response = import_files(client, case_id, development_bundle("corrected")[0], revision=case["revision"], key="corrected")
    assert response.status_code == 202
    assert process_one(db, settings)
    return client.get(f"/api/claims/{case_id}/bundles/2").json()

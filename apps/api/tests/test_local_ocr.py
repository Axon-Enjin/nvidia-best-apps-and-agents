
import pytest

from tests.bundle_helpers import create_case, import_files
from tests.fixture_paths import FIXTURES
from tests.review_helpers import action
from tests.test_workflow import context as context

SCANS = FIXTURES / "scans"


@pytest.mark.parametrize("suffix", ["png", "pdf"])
def test_actual_printed_scan_extracts_locally_but_cannot_clear_critical_fields(suffix):
    from sentinel.ocr import extract_document
    result = extract_document((SCANS / f"printed-cf2.{suffix}").read_bytes())
    assert result["status"] == "needs_confirmation"
    assert result["extraction"]["fields"]["patient_id"] == "SYN-PATIENT-1"
    assert result["extraction"]["fields"]["discharge_date"] == "2026-10-14"
    assert result["extraction"]["extractor"].startswith("tesseract/5.5.")
    assert result["extraction"]["anchors"][0]["page"] == 1


def test_failed_binary_and_unreadable_print_remain_incomplete():
    from sentinel.ocr import extract_document
    assert extract_document((SCANS/"unreadable.png").read_bytes())["status"] == "unreadable"
    assert extract_document((SCANS/"printed-cf2.png").read_bytes(), binary="missing-binary")["status"] == "unreadable"


def test_scan_confirmation_keeps_original_ocr_and_confirmed_values_separate(context):
    from sentinel.samples import development_bundle
    from sentinel.worker import process_one
    client, db, settings = context
    case_id = create_case(client)["id"]
    files, _ = development_bundle()
    files[0] = ("printed-cf2.png", (SCANS/"printed-cf2.png").read_bytes())
    assert import_files(client, case_id, files).status_code == 202
    assert process_one(db, settings)
    bundle = client.get(f"/api/claims/{case_id}/bundles/1").json()
    doc = bundle["documents"][0]
    assert doc["status"] == "needs_confirmation"
    raw = doc["extraction"]
    review = client.get(f"/api/claims/{case_id}/review-state").json()
    assert review["checks"][1]["status"] == "incomplete"
    for field, value in raw["fields"].items():
        case = client.get(f"/api/claims/{case_id}").json()
        response = client.post(f"/api/documents/{doc['id']}/confirm", json={"expected_revision":case["revision"],
            "anchor":{"page":1,"field":field}, "value":value, "reason":"Read the legible printed source", "source_kind":"printed"})
        assert response.status_code == 200, response.text
    review = client.get(f"/api/claims/{case_id}/review-state").json()
    assert all(review["checks"][i]["status"] == "passed" for i in range(6))
    assert client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]["extraction"] == raw
    case = client.get(f"/api/claims/{case_id}").json()
    assert client.post(f"/api/documents/{doc['id']}/confirm", json={"expected_revision":case["revision"],
        "anchor":{"page":1,"field":"dob"}, "value":"1980-04-12", "reason":"Unreadable handwriting", "source_kind":"handwritten"}).status_code == 422
    assert action(client, case_id, "manual_p07", reason="Needs evidence", anchors=[]).status_code == 422

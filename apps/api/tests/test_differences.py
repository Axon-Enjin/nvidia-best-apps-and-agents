"""Checks name the source values behind a conflict so reviewers see what differs and where."""
from tests.bundle_helpers import create_case, import_files
from tests.fixture_paths import FIXTURES
from tests.test_profile import checks, profile
from tests.test_workflow import context as context


def test_p05_differences_name_every_source_value_and_page():
    differences = checks(profile("discrepant"))["P05"]["differences"]
    assert len(differences) == 1
    entry = differences[0]
    assert entry["field"] == "discharge_date" and entry["expected"] is None
    assert len(entry["sources"]) == 7
    by_type = {source["type"]: source for source in entry["sources"]}
    assert by_type["discharge"]["value"] == "2026-10-15" and by_type["discharge"]["page"] == 1
    assert all(source["value"] == "2026-10-14" for kind, source in by_type.items() if kind != "discharge")
    assert all(source["bundle_id"] == "bundle-1" and source["document_id"] for source in entry["sources"])


def test_p04_difference_shows_case_value_and_only_differing_source():
    bundle = profile()
    bundle["documents"][4]["extraction"]["fields"]["patient_id"] = "OTHER"
    assert checks(bundle)["P04"]["differences"] == [{
        "field": "patient_id", "expected": "SYN-PATIENT-1",
        "sources": [{"document_id": "4", "type": "discharge", "bundle_id": "bundle-1", "value": "OTHER", "page": None}]}]


def test_checks_without_conflicts_have_empty_differences():
    assert all(check["differences"] == [] for check in checks(profile()).values())


def test_unconfirmed_scan_readings_never_appear_in_differences(context):
    from sentinel.samples import development_bundle
    from sentinel.worker import process_one
    client, db, settings = context
    case_id = create_case(client)["id"]
    files, _ = development_bundle("discrepant")
    files[0] = ("printed-cf2.png", (FIXTURES / "scans" / "printed-cf2.png").read_bytes())
    assert import_files(client, case_id, files).status_code == 202
    assert process_one(db, settings)
    scan_id = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]["id"]
    review = client.get(f"/api/claims/{case_id}/review-state").json()
    p05 = next(check for check in review["checks"] if check["id"] == "P05")
    sources = [source for entry in p05["differences"] for source in entry["sources"]]
    assert sources and all(source["document_id"] != scan_id for source in sources)
    assert any(source["type"] == "discharge" and source["value"] == "2026-10-15" for source in sources)

import hashlib
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from sqlalchemy import select

from sentinel.api import create_app
from sentinel.worker import process_one
from tests.account_helpers import provision_reviewer
from tests.bundle_helpers import ANCHORS, TYPES, bundle_files, create_case, import_files
from tests.test_workflow import context as context


def test_seven_artifacts_keep_original_bytes_and_report_coverage_after_processing(context):
    client, db, settings = context
    case = create_case(client)
    assert case["revision"] == 0
    response = import_files(client, case["id"])
    assert response.status_code == 202, response.text
    receipt = response.json()
    assert receipt["version"] == 1
    assert receipt["revision"] == 1
    assert receipt["import_job_id"]
    assert all(item["status"] == "quarantined" for item in receipt["coverage"])
    assert process_one(db, settings)
    bundle = client.get(f"/api/claims/{case['id']}/bundles/1").json()
    assert all(item["status"] == "readable" for item in bundle["coverage"])
    assert {doc["type"] for doc in bundle["documents"]} == set(TYPES)
    for document, (_, original) in zip(bundle["documents"], bundle_files(), strict=True):
        assert document["status"] == "readable"
        assert document["sha256"] == hashlib.sha256(original).hexdigest()
        assert client.get(f"/api/documents/{document['id']}/content").content == original
    assert client.get(f"/api/jobs/{receipt['import_job_id']}").json()["status"] == "succeeded"


def test_retry_is_idempotent_but_reusing_key_for_other_sources_conflicts(context):
    client, db, _ = context
    case_id = create_case(client)["id"]
    first = import_files(client, case_id)
    assert first.status_code == 202
    assert import_files(client, case_id).json() == first.json()
    altered = bundle_files()
    altered[0] = ("cf2.txt", altered[0][1] + b"Changed: true\n")
    assert import_files(client, case_id, altered).status_code == 409
    from sentinel.db import Bundle
    with db.session() as session:
        assert len(session.scalars(select(Bundle)).all()) == 1


def test_replacement_preserves_old_manifest_and_encrypted_sources(context):
    client, db, settings = context
    case_id = create_case(client)["id"]
    import_files(client, case_id)
    process_one(db, settings)
    old = client.get(f"/api/claims/{case_id}/bundles/1").json()
    files = bundle_files()
    files[0] = ("replacement.txt", files[0][1] + b"Discharge Date: 2026-10-21\n")
    assert import_files(client, case_id, files, revision=1, key="version-2").status_code == 202
    process_one(db, settings)
    assert client.get(f"/api/claims/{case_id}/bundles/1").json() == old
    original = bundle_files()[0][1]
    assert client.get(f"/api/documents/{old['documents'][0]['id']}/content").content == original
    from pathlib import Path
    stored = list(Path(settings.source_storage_root).rglob("*.source"))
    assert len(stored) == 14
    assert all(original not in path.read_bytes() for path in stored)


def test_manifest_conflict_is_rejected_and_source_identity_conflict_is_visible(context):
    client, db, settings = context
    case_id = create_case(client)["id"]
    assert import_files(client, case_id, anchors={**ANCHORS, "encounter_ref": "WRONG"}).status_code == 409
    files = bundle_files()
    files[2] = ("wrong.txt", files[2][1].replace(b"SYN-ENCOUNTER-1", b"SYN-OTHER"))
    assert import_files(client, case_id, files).status_code == 202
    process_one(db, settings)
    documents = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"]
    assert documents[2]["status"] == "unmatched"
    assert "encounter_ref" in documents[2]["problems"]


def test_duplicate_conflicting_extracted_identifiers_never_choose_one(context):
    client, db, settings = context
    case_id = create_case(client)["id"]
    files = bundle_files()
    files[0] = ("cf2.txt", files[0][1] + b"Patient ID: WRONG-PATIENT\n")
    assert import_files(client, case_id, files).status_code == 202
    process_one(db, settings)
    doc = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]
    assert doc["status"] == "ambiguous"
    assert "patient_id" not in doc["extraction"]["fields"]
    assert len([a for a in doc["extraction"]["anchors"] if a["field"] == "patient_id"]) == 2


def test_concurrent_imports_cannot_publish_same_case_revision(context):
    client, db, settings = context
    case_id = create_case(client)["id"]
    cookie = client.cookies.get("sentinel_session")
    csrf = client.headers["X-CSRF-Token"]

    def one_import(number):
        with TestClient(create_app(settings, db)) as other:
            other.cookies.set("sentinel_session", cookie)
            other.headers["X-CSRF-Token"] = csrf
            return import_files(other, case_id, key=f"concurrent-{number}").status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(one_import, range(2))) == [202, 409]


def test_source_and_bundle_urls_recheck_assignment_and_ignore_supplied_paths(context):
    client, db, settings = context
    case_id = create_case(client)["id"]
    files = bundle_files()
    files[0] = ("../../secret\r\nInjected.txt", files[0][1])
    assert import_files(client, case_id, files).status_code == 202
    process_one(db, settings)
    document = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]
    assert "\r" not in document["filename"] and "/" not in document["filename"]
    content = client.get(f"/api/documents/{document['id']}/content")
    assert content.status_code == 200
    assert content.headers["content-type"] == "application/octet-stream"
    provision_reviewer(db, settings.secret_key_file, "other")
    with TestClient(create_app(settings, db)) as other:
        signed = other.post("/api/session", json={"username": "other", "password": "synthetic reviewer passphrase 2026"})
        other.headers["X-CSRF-Token"] = signed.json()["csrf_token"]
        assert other.get(f"/api/documents/{document['id']}/content").status_code == 404
        assert other.get(f"/api/claims/{case_id}/bundles/1").status_code == 404
    assert client.get("/static/../../data/sources").status_code == 404


def test_xml_entities_unsupported_binary_and_blank_pdf_do_not_get_fake_text(context):
    from io import BytesIO

    from pypdf import PdfWriter
    client, db, settings = context
    case_id = create_case(client)["id"]
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    output = BytesIO()
    writer.write(output)
    malicious = b'<!DOCTYPE x [<!ENTITY steal SYSTEM "http://127.0.0.1:9/secret">]><Claim>&steal;</Claim>'
    files = [("entities.xml", malicious), ("not-text.pdf", b"\x00\x89UNSUPPORTED"), ("scan.pdf", output.getvalue())]
    assert import_files(client, case_id, files, types=TYPES[:3]).status_code == 202
    process_one(db, settings)
    documents = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"]
    assert [doc["status"] for doc in documents] == ["unreadable", "unsupported", "unreadable"]
    assert all(not doc["extraction"]["fields"] for doc in documents)
    assert documents[1]["content_type"] == "application/octet-stream"


def test_file_count_bytes_and_aggregate_pages_are_bounded(context):
    from io import BytesIO

    from pypdf import PdfWriter
    client, db, settings = context
    case_id = create_case(client)["id"]
    assert import_files(client, case_id, [(f"{i}.txt", b"source") for i in range(31)], types=["attachment"] * 31).status_code == 413
    assert import_files(client, case_id, [("big.txt", b"x" * (25 * 1024 * 1024 + 1))], types=["cf2"]).status_code == 413
    pdfs = []
    for index in range(2):
        writer, output = PdfWriter(), BytesIO()
        for _ in range(76):
            writer.add_blank_page(width=100, height=100)
        writer.write(output)
        pdfs.append((f"large-{index}.pdf", output.getvalue()))
    assert import_files(client, case_id, pdfs, types=["cf2", "cf4"]).status_code == 202
    process_one(db, settings)
    bundle = client.get(f"/api/claims/{case_id}/bundles/1").json()
    assert bundle["status"] == "limits_exceeded"
    assert sum(doc["page_count"] for doc in bundle["documents"]) == 152


def test_missing_or_changed_source_is_not_served_or_silently_recreated(context):
    from pathlib import Path

    from sentinel.db import Document
    client, db, settings = context
    case_id = create_case(client)["id"]
    import_files(client, case_id)
    with db.session() as session:
        document = session.scalar(select(Document).order_by(Document.position))
        path = Path(settings.source_storage_root) / (document.object_key + ".source")
        path.write_bytes(b"tampered")
        document_id = document.id
    assert client.get(f"/api/documents/{document_id}/content").status_code == 409
    process_one(db, settings)
    bundle = client.get(f"/api/claims/{case_id}/bundles/1").json()
    assert bundle["documents"][0]["status"] == "unreadable"


def test_assignment_changes_advance_revision_and_prevent_stale_import(context):
    from sentinel.accounts import SecretBox, create_local_account
    from sentinel.db import Account
    client, db, settings = context
    case_id = create_case(client)["id"]
    # An existing reviewer is given supervisor permission by the local operator,
    # with MFA enrollment; use a fresh privileged session to perform assignment.
    with db.session() as session:
        supervisor_id = create_local_account(session, "supervisor", "synthetic reviewer passphrase 2026", {"supervisor"},
                                             SecretBox.from_file(settings.secret_key_file),
                                             totp_secret="GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ")
        reviewer = session.scalar(select(Account).where(Account.username == "reviewer"))
        reviewer_id = reviewer.id
    import time

    from sentinel.accounts import totp_code
    with TestClient(create_app(settings, db)) as supervisor:
        logged = supervisor.post("/api/session", json={"username": "supervisor", "password": "synthetic reviewer passphrase 2026",
                                                      "otp": totp_code("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", time.time())})
        supervisor.headers["X-CSRF-Token"] = logged.json()["csrf_token"]
        assert supervisor.put(f"/api/claims/{case_id}/assignment", json={"assignee_id": supervisor_id}).status_code == 200
        assert supervisor.get(f"/api/claims/{case_id}").json()["revision"] == 1
        assert supervisor.put(f"/api/claims/{case_id}/assignment", json={"assignee_id": reviewer_id}).status_code == 200
    assert import_files(client, case_id, revision=0).status_code == 409

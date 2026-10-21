
import pytest

from sentinel.accounts import SecretBox
from sentinel.samples import development_bundle
from sentinel.worker import process_one
from tests.bundle_helpers import TYPES, create_case, import_files
from tests.review_helpers import action, seeded
from tests.test_closeout import finalize, manual_complete
from tests.test_workflow import context as context


def test_unrelated_confirmation_cannot_match_an_extra_attachment(context):
    client,db,settings = context
    case_id = create_case(client)["id"]
    files,_ = development_bundle()
    files.append(("unmatched-attachment.txt",b"Printed Name: Sample Signatory\n"))
    assert import_files(client,case_id,files,types=(*TYPES,"attachment")).status_code == 202
    assert process_one(db,settings)
    bundle = client.get(f"/api/claims/{case_id}/bundles/1").json()
    attachment = bundle["documents"][-1]
    assert attachment["status"] == "unmatched"
    result = action(client,case_id,"extra_expected",reason="Expect matching supplementary record").json()
    expectation_id = result["expectations"][0]["id"]
    revision = client.get(f"/api/claims/{case_id}").json()["revision"]
    assert client.post(f"/api/documents/{attachment['id']}/confirm",json={"expected_revision":revision,
        "anchor":{"field":"printed_name","page":1},"value":"Sample Signatory","reason":"Read printed name only","source_kind":"printed"}).status_code == 200
    response = action(client,case_id,"extra_reviewed",expectation_id=expectation_id,reason="Extra review",
                      anchors=[{"document_id":attachment["id"],"page":1}])
    assert response.status_code == 422
    assert client.get(f"/api/claims/{case_id}/review-state").json()["checks"][8]["status"] == "incomplete"


def test_missing_explicit_retirement_ledger_fails_before_restore(context,tmp_path):
    from sentinel.recovery import create_backup, restore_backup, retire_case
    _,db,settings = context
    case_id,_,_ = seeded(context)
    key=tmp_path/"backup.key"
    SecretBox.from_file(key,create=True)
    checkpoint=tmp_path/"checkpoint.backup"
    create_backup(db,settings,checkpoint,key)
    retire_case(db,settings,case_id,"Expired sample")
    target=tmp_path/"must-not-be-created"
    with pytest.raises(ValueError,match="ledger"):
        restore_backup(checkpoint,target,key,deletion_ledger=tmp_path/"missing-mount")
    assert not target.exists()


def test_current_review_state_drives_queue_filters_and_counts(context):
    client,_,_ = context
    case_id,bundle,_ = seeded(context)
    assert client.get("/api/claims?view=needs_review").json()["total"] == 1
    manual_complete(context,case_id,bundle)
    assert finalize(client,case_id).status_code == 201
    assert client.get("/api/claims?view=needs_review").json()["total"] == 0
    assert client.get("/api/claims?view=incomplete").json()["total"] == 0
    completed=client.get("/api/claims?view=no_findings").json()
    assert completed["total"] == 1 and completed["items"][0]["outcome"] == "no_findings"
    stats=client.get("/api/stats").json()
    assert stats["no_findings"] == 1 and stats["incomplete"] == 0
    create_case(client)
    assert client.get("/api/claims?view=incomplete").json()["total"] == 1

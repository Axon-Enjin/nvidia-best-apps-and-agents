import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database, Job
from sentinel.worker import claim_job, process_one
from tests.account_helpers import provision_reviewer, sign_in_reviewer
from tests.test_audit import CHART, claim_xml


@pytest.fixture
def context(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", embedded_worker=False,
                        auto_migrate=False, secret_key_file=str(tmp_path / "account.key"),
                        source_storage_root=str(tmp_path / "sources"))
    db = Database(settings.database_url)
    db.initialize()
    provision_reviewer(db, settings.secret_key_file)
    with TestClient(create_app(settings, db)) as client:
        sign_in_reviewer(client)
        yield client, db, settings
    db.engine.dispose()


def upload(client, xml=None, chart=CHART, claim_id=None, use_model=False):
    files = {"claim_file": ("claim.xml", (xml or claim_xml()).encode(), "application/xml")}
    if chart is not None:
        files["chart_file"] = ("chart.txt", chart.encode(), "text/plain")
    path = f"/api/claims/{claim_id}/rerun" if claim_id else "/api/claims"
    return client.post(path, files=files, data={"use_model": str(use_model).lower()})


def test_import_is_durable_and_a_worker_computes_the_result(context):
    client, db, settings = context
    response = upload(client, xml=claim_xml(DischargeDate=""))
    assert response.status_code == 202
    claim_id = response.json()["id"]
    assert client.get(f"/api/claims/{claim_id}").json()["latest"]["status"] == "queued"
    assert process_one(db, settings)
    detail = client.get(f"/api/claims/{claim_id}").json()
    assert detail["latest"]["status"] == "succeeded"
    assert detail["latest"]["result"]["outcome"] == "needs_review"
    assert "required_discharge_date" in [f["code"] for f in detail["latest"]["result"]["findings"]]
    # A new engine/process sees the persisted result, not Python process memory.
    second_db = Database(settings.database_url)
    with TestClient(create_app(settings, second_db)) as second_client:
        sign_in_reviewer(second_client)
        assert second_client.get(f"/api/claims/{claim_id}").json()["latest"]["status"] == "succeeded"
    second_db.engine.dispose()


def test_review_and_corrected_rerun_preserve_the_original_audit(context):
    client, db, settings = context
    claim_id = upload(client, xml=claim_xml(DischargeDate="")).json()["id"]
    process_one(db, settings)
    old_job = client.get(f"/api/claims/{claim_id}").json()["latest"]["id"]
    response = client.put(f"/api/jobs/{old_job}/reviews/required_discharge_date",
                          json={"decision": "accepted", "note": "Confirmed missing date; source needs correction."})
    assert response.status_code == 200
    assert upload(client, claim_id=claim_id).status_code == 202
    process_one(db, settings)
    detail = client.get(f"/api/claims/{claim_id}").json()
    assert len(detail["history"]) == 2
    assert detail["latest"]["result"]["outcome"] == "no_findings"
    original = client.get(f"/api/jobs/{old_job}").json()
    assert original["reviews"]["required_discharge_date"]["decision"] == "accepted"
    assert original["result"]["outcome"] == "needs_review"
    assert '<DischargeDate></DischargeDate>' in original["xml_text"]


def test_a_dismissal_requires_a_reason_and_unknown_findings_cannot_be_reviewed(context):
    client, db, settings = context
    claim_id = upload(client).json()["id"]
    process_one(db, settings)
    job = client.get(f"/api/claims/{claim_id}").json()["latest"]["id"]
    assert client.put(f"/api/jobs/{job}/reviews/imaginary", json={"decision": "accepted", "note": ""}).status_code == 404
    assert client.put(f"/api/jobs/{job}/reviews/imaginary", json={"decision": "dismissed", "note": ""}).status_code == 422


def test_incomplete_chart_is_persisted_as_incomplete_not_a_clean_result(context):
    client, db, settings = context
    claim_id = upload(client, chart=None).json()["id"]
    process_one(db, settings)
    result = client.get(f"/api/claims/{claim_id}").json()["latest"]["result"]
    assert result["outcome"] == "incomplete"


def test_requested_ai_without_credentials_is_rejected_before_enqueue(context):
    client, _, _ = context
    assert upload(client, use_model=True).status_code == 409
    assert client.get("/api/claims").json()["total"] == 0


def test_duplicate_rerun_is_rejected_while_a_job_is_pending(context):
    client, _, _ = context
    claim_id = upload(client).json()["id"]
    assert upload(client, claim_id=claim_id).status_code == 409


def test_rerun_cannot_silently_change_the_claim_identity(context):
    client, db, settings = context
    claim_id = upload(client).json()["id"]
    process_one(db, settings)
    assert upload(client, xml=claim_xml(ClaimId="OTHER"), claim_id=claim_id).status_code == 409


def test_workers_cannot_both_claim_the_same_job(context):
    client, db, _ = context
    upload(client)
    with ThreadPoolExecutor(max_workers=2) as pool:
        leases = list(pool.map(lambda _: claim_job(db), range(2)))
    assert sum(lease is not None for lease in leases) == 1


def test_expired_worker_lease_is_recovered(context):
    client, db, settings = context
    claim_id = upload(client).json()["id"]
    lease = claim_job(db)
    assert lease is not None
    with db.session() as session:
        session.execute(update(Job).where(Job.id == lease[0]).values(lease_until=time.time() - 1))
        session.commit()
    assert process_one(db, settings)
    latest = client.get(f"/api/claims/{claim_id}").json()["latest"]
    assert latest["status"] == "succeeded"
    assert latest["attempts"] == 2


def test_sample_loading_is_idempotent_and_downloads_are_available(context):
    client, db, settings = context
    assert client.post("/api/samples").status_code == 202
    assert client.post("/api/samples").status_code == 202
    assert client.get("/api/claims").json()["total"] == 4
    while process_one(db, settings):
        pass
    response = client.get("/api/samples/bundles.zip")
    assert response.status_code == 200
    assert response.content[:2] == b"PK"


def test_workspace_token_protects_data_and_login_works(context):
    _, db, settings = context
    protected = replace(settings, auth_mode="legacy", access_token="a-long-test-workspace-access-token")
    with TestClient(create_app(protected, db)) as client:
        assert client.get("/api/claims").status_code == 401
        assert client.post("/api/session", json={"token": "incorrect"}).status_code == 401
        response = client.post("/api/session", json={"token": protected.access_token})
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert client.get("/api/claims").status_code == 200
        client.delete("/api/session")
        assert client.get("/api/claims").status_code == 401


def test_cross_origin_writes_are_rejected(context):
    client, _, _ = context
    assert client.post("/api/samples", headers={"Origin": "https://unrelated.example"}).status_code == 403


def test_oversized_and_binary_claim_uploads_are_rejected(context):
    client, _, _ = context
    assert client.post("/api/claims", files={"claim_file": ("bad.xml", b"x" * 262145)}).status_code == 413
    assert client.post("/api/claims", files={"claim_file": ("bad.xml", b"\xff\xfe")}).status_code == 400


def test_healthcheck_and_paginated_queue(context):
    client, _, _ = context
    assert client.get("/healthz").json()["status"] == "ok"
    client.post("/api/samples")
    response = client.get("/api/claims?limit=2&offset=2").json()
    assert response["total"] == 4
    assert len(response["items"]) == 2
    assert client.get("/api/claims?limit=10001").status_code == 422

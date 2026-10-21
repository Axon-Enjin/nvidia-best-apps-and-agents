import csv
import io

import pytest

from sentinel.accounts import resolve_actor
from tests.review_helpers import action, anchors, corrected, seeded
from tests.test_corrections import supervisor
from tests.test_workflow import context as context


def manual_complete(context, case_id, bundle):
    from sentinel.review import record_review
    client, db, settings = context
    assert action(client, case_id, "manual_p07", reason="Compared admission, diagnosis, treatment, course and outcome", anchors=anchors(bundle)).status_code == 200
    assert action(client, case_id, "manual_p08", reason="Fictional marks, printed names and dates present", anchors=anchors(bundle)).status_code == 200
    case = client.get(f"/api/claims/{case_id}").json()
    record_review(db, supervisor(db, settings), case_id, case["revision"], {"action":"supervisor_ack", "bundle_id":bundle["bundle_id"], "rule_version":"SAMPLE-ADULT-MEDICAL-1/1", "reason":"Supervisor source comparison acknowledged"})


def finalize(client, case_id, **overrides):
    case = client.get(f"/api/claims/{case_id}").json()
    return client.post(f"/api/claims/{case_id}/finalize", json={"expected_revision":case["revision"],
        "bundle_id":case["current_bundle_id"], "rule_version":"SAMPLE-ADULT-MEDICAL-1/1", **overrides})


@pytest.mark.parametrize("label", ["complete", "discrepant", "incomplete"])
def test_unresolved_profile_never_finalizes(context, label):
    client, _, _ = context
    case_id, _, _ = seeded(context, label)
    result = finalize(client, case_id)
    assert result.status_code == 409, result.text
    assert "blockers" in result.json()["detail"]


def test_manual_resolution_snapshot_exports_staleness_and_guarded_legacy_route(context):
    client, _, _ = context
    case_id, bundle, receipt = seeded(context)
    assert client.get(f"/api/jobs/{receipt['import_job_id']}/report").status_code == 409
    manual_complete(context, case_id, bundle)
    response = finalize(client, case_id)
    assert response.status_code == 201, response.text
    report = response.json()
    assert not report["stale"]
    assert report["snapshot"]["provenance"] == "Synthetic patient records; internal sample profile; no payer approval."
    assert report["snapshot"]["model_status"] == "not_run_offline"
    assert report["snapshot"]["checks"][9]["status"] == "passed"
    assert client.get(f"/api/claims/{case_id}/review-state").json()["checks"][9]["status"] == "passed"
    export = client.get(f"/api/reports/{report['id']}/export?format=csv")
    assert export.status_code == 200
    assert "SAMPLE-ADULT-MEDICAL-1/1" in export.text and bundle["bundle_id"] in export.text
    assert client.get(f"/api/reports/{report['id']}/export?format=html").status_code == 200
    corrected(context, case_id)
    stale = client.get(f"/api/reports/{report['id']}").json()
    assert stale["stale"] and stale["snapshot"] == report["snapshot"]
    assert client.get(f"/api/reports/{report['id']}/export?format=csv").status_code == 409


def test_open_task_stale_revision_and_wrong_role_block_closeout(context):
    from sentinel.accounts import Actor
    from sentinel.reports import finalize_review
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    manual_complete(context, case_id, bundle)
    assert action(client, case_id, "correction_created", check_id="P07", reason="Needs source revision", department="Records", person="Clerk", anchors=anchors(bundle)).status_code == 200
    assert finalize(client, case_id).status_code == 409
    assert finalize(client, case_id, expected_revision=0).status_code == 409
    assert finalize(client, case_id, bundle_id="old-version").status_code == 409
    case = client.get(f"/api/claims/{case_id}").json()
    actor = resolve_actor(db, settings, client.cookies.get("sentinel_session"))
    with pytest.raises(Exception) as denied:
        finalize_review(db, Actor(actor.id, actor.username, frozenset({"admin"}), True), case_id, bundle["bundle_id"], "SAMPLE-ADULT-MEDICAL-1/1", case["revision"])
    assert denied.value.status_code == 403


def test_exports_escape_formula_and_html_and_metrics_have_denominators(context):
    client, db, _ = context
    case_id, bundle, _ = seeded(context)
    assert action(client, case_id, "dismissed", check_id="P07", reason='=HYPERLINK("bad")<script>alert(1)</script>', anchors=anchors(bundle)).status_code == 200
    manual_complete(context, case_id, bundle)
    result = finalize(client, case_id).json()
    csv_text = client.get(f"/api/reports/{result['id']}/export?format=csv").text
    for row in csv.reader(io.StringIO(csv_text)):
        assert all(not cell.lstrip().startswith(("=", "+", "-", "@")) for cell in row)
    html = client.get(f"/api/reports/{result['id']}/export?format=html").text
    assert "<script>" not in html and "&lt;script&gt;" in html
    metrics = client.get("/api/metrics").json()
    assert metrics["completed_cases"] == 1
    assert metrics["case_denominator"] == 1
    assert metrics["correction_denominator"] == 0


def test_concurrent_replacement_and_finalization_cannot_both_publish(context):
    from concurrent.futures import ThreadPoolExecutor

    from sentinel.bundles import import_bundle
    from sentinel.reports import finalize_review
    from sentinel.samples import development_bundle
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    manual_complete(context, case_id, bundle)
    actor = resolve_actor(db, settings, client.cookies.get("sentinel_session"))
    revision = client.get(f"/api/claims/{case_id}").json()["revision"]
    files, manifest = development_bundle("corrected")
    def attempt(kind):
        try:
            if kind == "finalize":
                finalize_review(db, actor, case_id, bundle["bundle_id"], "SAMPLE-ADULT-MEDICAL-1/1", revision, settings=settings)
            else:
                import_bundle(db, settings, actor, case_id, files, manifest, revision, "competing-import")
            return 200
        except Exception as exc:
            return getattr(exc, "status_code", 500)
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(attempt, ["finalize", "replace"])) == [200, 409]


def test_missing_original_blocks_closeout_even_after_successful_extraction(context):
    from pathlib import Path

    from sentinel.db import Document
    client, db, settings = context
    case_id,bundle,_ = seeded(context)
    manual_complete(context,case_id,bundle)
    with db.session() as session:
        key=session.get(Document,bundle["documents"][0]["id"]).object_key
    Path(settings.source_storage_root,key+".source").unlink()
    assert finalize(client,case_id).status_code == 409


def test_reassignment_marks_previous_record_stale_and_reopens_closeout(context):
    import time

    from fastapi.testclient import TestClient

    from sentinel.accounts import totp_code
    from sentinel.api import create_app
    client,db,settings = context
    case_id,bundle,_ = seeded(context)
    manual_complete(context,case_id,bundle)
    report = finalize(client,case_id).json()
    actor = resolve_actor(db,settings,client.cookies.get("sentinel_session"))
    with TestClient(create_app(settings,db)) as privileged:
        login = privileged.post("/api/session",json={"username":"supervisor","password":"synthetic reviewer passphrase 2026",
            "otp":totp_code("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",time.time())})
        privileged.headers["X-CSRF-Token"] = login.json()["csrf_token"]
        assert privileged.put(f"/api/claims/{case_id}/assignment",json={"assignee_id":actor.id}).status_code == 200
    assert client.get(f"/api/reports/{report['id']}").json()["stale"]
    assert client.get(f"/api/claims/{case_id}").json()["state"] == "In review"
    assert finalize(client,case_id).status_code == 201

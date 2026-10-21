from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from sentinel.accounts import Actor, SecretBox, create_local_account
from sentinel.api import create_app
from sentinel.db import Account
from tests.account_helpers import PASSWORD
from tests.review_helpers import action, anchors, corrected, seeded
from tests.test_workflow import context as context


def supervisor(db, settings):
    with db.session() as session:
        account_id = create_local_account(session, "supervisor", PASSWORD, {"supervisor"}, SecretBox.from_file(settings.secret_key_file), totp_secret="GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ")
        account = session.get(Account, account_id)
    return Actor(account.id, account.username, frozenset(account.roles), True)


def test_correction_handoff_recheck_and_append_only_history(context):
    client, db, settings = context
    case_id, bundle, _ = seeded(context, "discrepant")
    response = action(client, case_id, "correction_created", check_id="P05", reason="Discharge date differs", department="Records", person="Sample Clerk", anchors=anchors(bundle))
    assert response.status_code == 200, response.text
    task_id = response.json()["tasks"][0]["id"]
    assert action(client, case_id, "correction_resolved", task_id=task_id, reason="fixed").status_code == 409
    assert action(client, case_id, "correction_handoff", task_id=task_id, reason="Local handoff recorded").status_code == 200
    assert action(client, case_id, "correction_acknowledged", task_id=task_id, reason="Clerk acknowledged offline").status_code == 200
    corrected(context, case_id)
    response = action(client, case_id, "correction_resolved", task_id=task_id, reason="Rechecked corrected discharge source")
    assert response.status_code == 200, response.text
    assert response.json()["tasks"][0]["status"] == "resolved"
    old = client.get(f"/api/claims/{case_id}/bundles/1").json()
    assert old == bundle
    with TestClient(create_app(settings, db)) as restarted:
        restarted.cookies.update(client.cookies)
        history = restarted.get(f"/api/claims/{case_id}/review-state").json()["events"]
        assert [e["action"] for e in history] == ["correction_created", "correction_handoff", "correction_acknowledged", "correction_resolved"]
        assert history[0]["bundle_id"] == bundle["bundle_id"]


def test_manual_narrative_requires_evidence_separate_supervisor_and_version(context):
    from sentinel.review import record_review
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    assert action(client, case_id, "manual_p07", reason="Compared", anchors=[]).status_code == 422
    assert action(client, case_id, "manual_p07", reason="Compared all narratives against the source", anchors=anchors(bundle)).status_code == 200
    assert action(client, case_id, "supervisor_ack", reason="Agree").status_code == 403
    actor = supervisor(db, settings)
    case = client.get(f"/api/claims/{case_id}").json()
    result = record_review(db, actor, case_id, case["revision"], {"action":"supervisor_ack", "bundle_id":bundle["bundle_id"], "rule_version":"SAMPLE-ADULT-MEDICAL-1/1", "reason":"Reviewed manual comparison"})
    assert result["checks"][6]["status"] == "passed"
    assert result["model_status"] == "not_run_offline"
    corrected(context, case_id)
    result = client.get(f"/api/claims/{case_id}/review-state").json()
    assert result["checks"][6]["status"] == "incomplete"
    assert len(result["events"]) == 2


def test_dismissal_does_not_waive_deterministic_source_conflicts(context):
    client, _, _ = context
    case_id, bundle, _ = seeded(context, "discrepant")
    assert action(client, case_id, "dismissed", check_id="P05", reason="Probably fine", anchors=anchors(bundle)).status_code == 422
    assert action(client, case_id, "dismissed", check_id="P07", reason="No discrepancy on comparison", anchors=[]).status_code == 422
    assert action(client, case_id, "dismissed", check_id="P07", reason="Source-backed false alarm", anchors=anchors(bundle)).status_code == 200
    result = client.get(f"/api/claims/{case_id}/review-state").json()
    assert result["checks"][6]["status"] == "incomplete"


def test_stale_concurrent_review_returns_conflict_and_preserves_first_event(context):
    from sentinel.accounts import resolve_actor
    from sentinel.review import record_review
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    actor = resolve_actor(db, settings, client.cookies.get("sentinel_session"))
    payload = {"action":"manual_p08", "bundle_id":bundle["bundle_id"], "rule_version":"SAMPLE-ADULT-MEDICAL-1/1", "reason":"Marks, printed names and dates present", "anchors":anchors(bundle)}
    def save():
        try:
            record_review(db, actor, case_id, 1, payload)
            return 200
        except Exception as exc:
            return getattr(exc, "status_code", 500)
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(lambda _:save(), range(2))) == [200, 409]
    assert len(client.get(f"/api/claims/{case_id}/review-state").json()["events"]) == 1


def test_extra_requirement_is_persistent_and_only_supervisor_may_withdraw(context):
    from sentinel.review import record_review
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    result = action(client, case_id, "extra_expected", reason="Expect sample lab attachment").json()
    expectation_id = result["expectations"][0]["id"]
    assert result["checks"][8]["status"] == "incomplete"
    assert action(client, case_id, "extra_withdrawn", expectation_id=expectation_id, reason="Mistaken expectation").status_code == 403
    case = client.get(f"/api/claims/{case_id}").json()
    result = record_review(db, supervisor(db, settings), case_id, case["revision"], {"action":"extra_withdrawn", "expectation_id":expectation_id, "reason":"Mistaken extra requirement; not applicable", "bundle_id":bundle["bundle_id"], "rule_version":"SAMPLE-ADULT-MEDICAL-1/1"})
    assert result["checks"][8]["status"] == "passed"


def test_old_evidence_and_old_rules_cannot_authorize_new_manual_review(context):
    client, _, _ = context
    case_id, old, _ = seeded(context)
    corrected(context, case_id)
    assert action(client, case_id, "manual_p07", reason="Compared old pages", anchors=anchors(old)).status_code == 422
    case = client.get(f"/api/claims/{case_id}").json()
    assert client.post(f"/api/claims/{case_id}/review-events", json={"expected_revision":case["revision"],
        "bundle_id":case["current_bundle_id"], "rule_version":"old-rule", "action":"manual_p07", "reason":"old rules"}).status_code == 409
    assert client.get(f"/api/claims/{case_id}/review-state").json()["events"] == []

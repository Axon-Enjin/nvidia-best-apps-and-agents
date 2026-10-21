import time
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from sentinel.api import create_app
from sentinel.db import Claim, Document, Job, LocalSession
from sentinel.worker import claim_job
from tests.account_helpers import sign_in_reviewer
from tests.review_helpers import action, anchors, seeded
from tests.test_workflow import context as context


def test_interrupted_worker_reclaimed_and_old_lease_cannot_publish(context):
    from sentinel.bundle_worker import process_bundle_job
    client, db, settings = context
    case_id, bundle, receipt = seeded(context)
    response = action(client, case_id, "recheck", reason="Test lease recovery")
    assert response.status_code == 200
    job_id, old_token = claim_job(db)
    with db.session() as session:
        session.execute(update(Job).where(Job.id == job_id).values(lease_until=time.time()-1))
        session.commit()
    new_id, new_token = claim_job(db)
    assert new_id == job_id and new_token != old_token
    process_bundle_job(db, settings, job_id, old_token)
    with db.session() as session:
        assert session.get(Job, job_id).result is None
    process_bundle_job(db, settings, job_id, new_token)
    process_bundle_job(db, settings, job_id, old_token)
    with db.session() as session:
        assert session.get(Job, job_id).attempts == 2
        assert session.get(Job, job_id).status == "succeeded"


def test_coordinated_encrypted_backup_isolated_restore_hash_history_and_authorization(context, tmp_path):
    from sentinel.accounts import SecretBox
    from sentinel.recovery import create_backup, restore_backup, verify_workspace
    client, db, settings = context
    case_id, bundle, _ = seeded(context)
    assert action(client, case_id, "manual_p07", reason="Saved comparison before backup", anchors=anchors(bundle)).status_code == 200
    backup_key = tmp_path/"separate-recovery.key"
    SecretBox.from_file(backup_key, create=True)
    target = tmp_path/"workspace.backup"
    create_backup(db, settings, target, backup_key)
    assert b"Saved comparison" not in target.read_bytes()
    restored_settings = restore_backup(target, tmp_path/"isolated", backup_key)
    restored_db = __import__('sentinel.db',fromlist=['Database']).Database(restored_settings.database_url)
    verified = verify_workspace(restored_db, restored_settings)
    assert verified["verified_sources"] == 7
    with TestClient(create_app(replace(restored_settings,embedded_worker=False,auto_migrate=False),restored_db)) as restored:
        sign_in_reviewer(restored)
        assert restored.get(f"/api/claims/{case_id}/review-state").json()["events"][0]["payload"]["reason"] == "Saved comparison before backup"
        assert restored.get(f"/api/documents/{bundle['documents'][0]['id']}/content").status_code == 200
        assert restored.get("/api/claims/unknown").status_code == 404
    restored_db.engine.dispose()


def test_damaged_missing_sources_and_unknown_staging_are_reported_not_removed(context):
    from sentinel.recovery import verify_workspace
    client, db, settings = context
    _, bundle, _ = seeded(context)
    with db.session() as session:
        doc = session.get(Document, bundle["documents"][0]["id"])
    Path(settings.source_storage_root, doc.object_key+".source").unlink()
    receipt = Path(settings.source_storage_root,"f"*32+".staging.json")
    receipt.write_text('{"object_key":"'+"f"*32+'"}')
    result = verify_workspace(db, settings)
    assert not result["ok"] and result["missing_or_damaged"] == [doc.id]
    assert "f"*32 in result["orphan_staging"] and receipt.exists()


def test_restored_sessions_are_revoked_and_newer_deletion_ledger_is_applied(context, tmp_path):
    from sentinel.accounts import SecretBox
    from sentinel.recovery import create_backup, restore_backup, retire_case
    client, db, settings = context
    case_id, _, _ = seeded(context)
    key = tmp_path/"backup.key"
    SecretBox.from_file(key,create=True)
    backup = tmp_path/"before-deletion.backup"
    create_backup(db,settings,backup,key)
    retire_case(db,settings,case_id,"Expired synthetic evaluation")
    restored = restore_backup(backup,tmp_path/"isolated-deleted",key,deletion_ledger=Path(settings.source_storage_root)/"deletions")
    from sentinel.db import Database
    restored_db = Database(restored.database_url)
    with restored_db.session() as session:
        assert session.get(Claim,case_id).deleted_at
        assert all(s.revoked for s in session.scalars(select(LocalSession)))
    with TestClient(create_app(replace(restored,embedded_worker=False,auto_migrate=False),restored_db)) as recovered:
        sign_in_reviewer(recovered)
        assert recovered.get(f"/api/claims/{case_id}").status_code == 404
    restored_db.engine.dispose()


def test_expired_lease_stops_after_bounded_attempts(context):
    client, db, _ = context
    case_id, _, _ = seeded(context)
    assert action(client,case_id,"recheck",reason="Bound retries").status_code == 200
    job_id, _ = claim_job(db)
    with db.session() as session:
        session.execute(update(Job).where(Job.id == job_id).values(attempts=3,lease_until=time.time()-1))
        session.commit()
    assert claim_job(db) is None
    with db.session() as session:
        assert session.get(Job,job_id).status == "failed"

"""Executed by CI against a real local PostgreSQL service; never substitute SQLite."""
import os

import pytest
from fastapi.testclient import TestClient

from sentinel.api import create_app
from sentinel.config import Settings, migrate
from sentinel.db import Database
from tests.account_helpers import provision_reviewer, sign_in_reviewer
from tests.review_helpers import action, anchors, corrected, seeded
from tests.test_closeout import finalize, manual_complete


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="Actual PostgreSQL runtime not configured")
def test_postgresql_migrations_correction_loop_and_reports(tmp_path):
    settings = Settings(database_url=os.environ["TEST_DATABASE_URL"],auto_migrate=False,embedded_worker=False,
                        secret_key_file=str(tmp_path/"key"),source_storage_root=str(tmp_path/"sources"))
    migrate(settings.database_url)
    db = Database(settings.database_url)
    try:
        provision_reviewer(db,settings.secret_key_file)
        with TestClient(create_app(settings,db)) as client:
            sign_in_reviewer(client)
            context = client,db,settings
            case_id,bundle,_ = seeded(context,"discrepant")
            result = action(client,case_id,"correction_created",check_id="P05",department="Records",person="Clerk",reason="Date conflict",anchors=anchors(bundle)).json()
            task_id = result["tasks"][0]["id"]
            assert action(client,case_id,"correction_handoff",task_id=task_id,reason="Handed off").status_code == 200
            assert action(client,case_id,"correction_acknowledged",task_id=task_id,reason="Acknowledged").status_code == 200
            current = corrected(context,case_id)
            assert action(client,case_id,"correction_resolved",task_id=task_id,reason="Source corrected and rechecked").status_code == 200
            manual_complete(context,case_id,current)
            report = finalize(client,case_id)
            assert report.status_code == 201,report.text
            assert client.get(f"/api/reports/{report.json()['id']}/export?format=csv").status_code == 200
    finally:
        db.engine.dispose()

"""A bounded local metadata exercise, not a clinical or production capacity benchmark."""
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient

from sentinel.api import create_app
from sentinel.db import Claim
from tests.account_helpers import PASSWORD, provision_reviewer
from tests.test_workflow import context as context


def test_ten_thousand_metadata_rows_remain_assigned_and_paginated_for_five_named_readers(context):
    _,db,settings = context
    owners = [provision_reviewer(db,settings.secret_key_file,username=f"load-{i}") for i in range(5)]
    with db.session() as session:
        session.add_all([Claim(reference=f"SYN-LOAD-{i:05}",patient_id=f"FICTION-LOAD-{i:05}",assignee_id=owners[i%5]) for i in range(10000)])
        session.commit()
    app = create_app(settings,db)
    def read(i):
        with TestClient(app) as client:
            response = client.post("/api/session",json={"username":f"load-{i}","password":PASSWORD})
            assert response.status_code == 200
            started = time.perf_counter()
            response = client.get("/api/claims?limit=100")
            elapsed = time.perf_counter()-started
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2000 and len(data["items"]) == 100
            assert all(row["assignee_id"] == owners[i] for row in data["items"])
            assert client.get("/api/claims?limit=101").status_code == 422
            return elapsed
    with ThreadPoolExecutor(5) as pool:
        elapsed = list(pool.map(read,range(5)))
    directory = Path("test-results")
    directory.mkdir(exist_ok=True)
    (directory/"workload.json").write_text(json.dumps({"database":"SQLite development","metadata_rows":10000,
        "named_concurrent_readers":5,"returned_rows_per_request":100,"sample_requests":5,
        "median_request_seconds":statistics.median(elapsed),"max_request_seconds":max(elapsed)},indent=2))

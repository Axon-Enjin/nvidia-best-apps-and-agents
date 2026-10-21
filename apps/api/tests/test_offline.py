from dataclasses import replace

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Job
from sentinel.inference import review_with_nebius
from sentinel.worker import process_one
from tests.account_helpers import sign_in_reviewer
from tests.test_audit import CHART, claim_xml
from tests.test_workflow import context as context
from tests.test_workflow import upload


def test_offline_is_default_and_unknown_network_modes_are_rejected():
    assert Settings().network_mode == "offline"
    with pytest.raises(ValueError, match="NETWORK_MODE"):
        Settings(network_mode="automatic").validate()


def test_environment_can_explicitly_select_online_mode(monkeypatch):
    monkeypatch.setattr("sentinel.config.load_dotenv", lambda: None)
    monkeypatch.setenv("NETWORK_MODE", "online")
    assert Settings.from_env().network_mode == "online"


def test_offline_import_cannot_request_remote_ai_even_with_credentials(context):
    _, db, settings = context
    offline = replace(settings, network_mode="offline", nebius_api_key="test-only-credential")
    with TestClient(create_app(offline, db)) as client:
        sign_in_reviewer(client)
        config = client.get("/api/config").json()
        assert config["network_mode"] == "offline"
        assert config["model_configured"] is False
        assert upload(client, use_model=True).status_code == 409
        assert client.get("/api/claims").json()["total"] == 0
        assert upload(client, use_model=False).status_code == 202


def test_provider_adapter_blocks_offline_before_sending_any_request():
    requests = []

    def remote(request):
        requests.append(request)
        return httpx.Response(200, json={})

    settings = Settings(network_mode="offline", nebius_api_key="test-only-credential")
    with pytest.raises(ValueError, match="offline"):
        review_with_nebius(claim_xml(), CHART, settings, transport=httpx.MockTransport(remote))
    assert requests == []


def test_offline_worker_preserves_local_results_for_queued_remote_job(context, monkeypatch):
    client, db, settings = context
    claim_id = upload(client).json()["id"]
    job_id = client.get(f"/api/claims/{claim_id}").json()["latest"]["id"]
    with db.session() as session:
        session.execute(update(Job).where(Job.id == job_id).values(use_model=True))
        session.commit()
    remote_calls = []

    def remote(*args, **kwargs):
        remote_calls.append(True)
        return [], {"model": "test", "usage": {}}

    monkeypatch.setattr("sentinel.worker.review_with_nebius", remote)
    assert process_one(db, settings)
    result = client.get(f"/api/claims/{claim_id}").json()["latest"]["result"]
    assert result["model_status"] == "not_run_offline"
    assert result["outcome"] == "incomplete"
    assert result["fields"]["claim_id"]
    assert remote_calls == []


def test_online_inference_requires_explicit_opt_in_and_still_validates_evidence():
    requests = []

    def remote(request):
        requests.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"findings": []}'}}]})

    settings = Settings(network_mode="online", nebius_api_key="test-only-credential")
    findings, metadata = review_with_nebius(claim_xml(), CHART, settings, transport=httpx.MockTransport(remote))
    assert findings == []
    assert metadata["model"] == settings.nebius_model
    assert len(requests) == 1

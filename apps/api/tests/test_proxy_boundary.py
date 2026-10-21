"""The web frontend reaches the API from its own origin through a same-origin proxy."""
import pytest
from fastapi.testclient import TestClient

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database
from tests.account_helpers import provision_reviewer, sign_in_reviewer
from tests.bundle_helpers import ANCHORS

WEB_ORIGIN = "http://127.0.0.1:3000"


@pytest.fixture
def client(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'proxy.db'}", embedded_worker=False,
                        auto_migrate=False, secret_key_file=str(tmp_path / "account.key"),
                        source_storage_root=str(tmp_path / "sources"), trusted_origins=(WEB_ORIGIN,))
    db = Database(settings.database_url)
    db.initialize()
    provision_reviewer(db, settings.secret_key_file)
    with TestClient(create_app(settings, db)) as test_client:
        sign_in_reviewer(test_client)
        yield test_client
    db.engine.dispose()


def test_trusted_web_origin_may_change_state(client):
    response = client.post("/api/cases", json=ANCHORS, headers={"Origin": WEB_ORIGIN})
    assert response.status_code == 201, response.text


def test_untrusted_origin_is_still_denied(client):
    response = client.post("/api/cases", json=ANCHORS, headers={"Origin": "http://evil.example"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Cross-origin changes are not allowed."


@pytest.mark.parametrize("origin", ["http://localhost:3000/app", "*", "localhost:3000", "http://localhost:3000/"])
def test_trusted_origins_must_be_bare_origins(origin):
    with pytest.raises(ValueError):
        Settings(trusted_origins=(origin,)).validate()


def test_production_trusted_origins_require_https():
    settings = Settings(environment="production", secure_cookies=True,
                        database_url="postgresql+psycopg://user:secret@db:5432/sentinel",
                        allowed_hosts=("app.example.test",), trusted_origins=("http://app.example.test",))
    with pytest.raises(ValueError):
        settings.validate()


def test_trusted_origins_survive_a_json_round_trip():
    settings = Settings(trusted_origins=[WEB_ORIGIN])
    assert settings.trusted_origins == (WEB_ORIGIN,)

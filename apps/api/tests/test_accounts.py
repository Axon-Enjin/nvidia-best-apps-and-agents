"""Exercise real sessions and assigned case boundaries, including child URLs."""

import time
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database
from tests.test_workflow import upload

PASSWORD = "synthetic reviewer passphrase 2026"
MFA_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


def sign_in(client, username="reviewer", password=PASSWORD, **extra):
    response = client.post("/api/session", json={"username": username, "password": password, **extra})
    if response.status_code == 200:
        client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return response


def test_new_installation_denies_anonymous_and_shared_token_access(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'closed.db'}", embedded_worker=False,
                        auto_migrate=False, access_token="old-shared-token-must-not-unlock")
    db = Database(settings.database_url)
    db.initialize()
    try:
        with TestClient(create_app(settings, db)) as client:
            assert client.get("/api/claims").status_code == 401
            assert client.get("/api/claims", headers={"Authorization": f"Bearer {settings.access_token}"}).status_code == 401
            assert client.post("/api/session", json={"token": settings.access_token}).status_code == 422
    finally:
        db.engine.dispose()


@pytest.fixture
def accounts(tmp_path):
    from sentinel.accounts import SecretBox, create_local_account
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'accounts.db'}", embedded_worker=False,
                        auto_migrate=False, secret_key_file=str(tmp_path / "account.key"))
    db = Database(settings.database_url)
    db.initialize()
    box = SecretBox.from_file(settings.secret_key_file, create=True)
    ids = {}
    with db.session() as session:
        for username, roles in [("reviewer", {"reviewer"}), ("other", {"reviewer"}),
                                ("supervisor", {"supervisor"}), ("admin", {"admin"})]:
            ids[username] = create_local_account(session, username, PASSWORD, roles, box,
                                                 totp_secret=MFA_SECRET if username in {"supervisor", "admin"} else None)
    with TestClient(create_app(settings, db)) as client:
        yield client, db, settings, ids
    db.engine.dispose()


def test_passwords_are_salted_mfa_is_encrypted_and_identifiers_are_normalized(accounts):
    from sentinel.accounts import SecretBox, create_local_account
    from sentinel.db import Account
    client, db, settings, ids = accounts
    with db.session() as session:
        reviewer = session.get(Account, ids["reviewer"])
        other = session.get(Account, ids["other"])
        supervisor = session.get(Account, ids["supervisor"])
        assert reviewer.password_hash.startswith("$argon2id$")
        assert reviewer.password_hash != other.password_hash
        assert MFA_SECRET not in supervisor.totp_encrypted
        with pytest.raises(ValueError):
            create_local_account(session, " Reviewer ", PASSWORD, {"reviewer"}, SecretBox.from_file(settings.secret_key_file))
    assert sign_in(client, " REVIEWER ").status_code == 200
    assert PASSWORD not in client.get("/api/session").text


def test_valid_login_sets_random_httponly_session_and_invalid_login_is_generic(accounts):
    from sentinel.db import LocalSession
    client, db, _, ids = accounts
    assert sign_in(client, password="incorrect").status_code == 401
    result = sign_in(client)
    assert result.status_code == 200
    assert result.json()["actor"]["id"] == ids["reviewer"]
    assert "HttpOnly" in result.headers["set-cookie"]
    assert "SameSite=strict" in result.headers["set-cookie"]
    cookie = client.cookies.get("sentinel_session")
    with db.session() as session:
        row = session.scalar(select(LocalSession))
        assert cookie != row.token_digest
    assert sign_in(client).status_code == 200
    assert client.cookies.get("sentinel_session") != cookie
    assert sign_in(client, "absent", "incorrect").json() == {"detail": "Sign-in failed."}


def test_supervisor_mfa_requires_current_code_and_rejects_replay(accounts):
    from sentinel.accounts import totp_code
    client, _, _, _ = accounts
    assert totp_code(MFA_SECRET, 59, digits=8) == "94287082"  # RFC 6238 SHA-1 vector
    assert sign_in(client, "supervisor").status_code == 401
    assert sign_in(client, "supervisor", otp="abcdef").status_code == 401
    assert sign_in(client, "supervisor", otp=totp_code(MFA_SECRET, time.time() - 120)).status_code == 401
    code = totp_code(MFA_SECRET, time.time())
    assert sign_in(client, "supervisor", otp=code).status_code == 200
    assert sign_in(client, "supervisor", otp=code).status_code == 401


@pytest.mark.parametrize("change", ["expired", "idle", "revoked", "disabled"])
def test_session_expiry_revocation_and_disabled_accounts(accounts, change):
    from sentinel.db import Account, LocalSession
    client, db, _, ids = accounts
    assert sign_in(client).status_code == 200
    with db.session() as session:
        if change == "disabled":
            session.execute(update(Account).where(Account.id == ids["reviewer"]).values(enabled=False))
        else:
            values = {"expired": {"expires_at": time.time() - 1},
                      "idle": {"last_seen_at": time.time() - 3600}, "revoked": {"revoked": True}}[change]
            session.execute(update(LocalSession).values(**values))
        session.commit()
    assert client.get("/api/claims").status_code == 401
    assert client.get("/api/session").json()["authenticated"] is False


def test_logout_revokes_stolen_cookie_and_session_survives_restart(accounts):
    client, db, settings, _ = accounts
    sign_in(client)
    cookie = client.cookies.get("sentinel_session")
    with TestClient(create_app(settings, db)) as second:
        second.cookies.set("sentinel_session", cookie)
        assert second.get("/api/claims").status_code == 200
        assert client.delete("/api/session").status_code == 200
        assert second.get("/api/claims").status_code == 401


def test_every_case_child_and_aggregate_requires_assignment(accounts):
    client, db, settings, ids = accounts
    sign_in(client)
    created = upload(client).json()
    claim_id, job_id = created["id"], created["job_id"]
    with TestClient(create_app(settings, db)) as other:
        sign_in(other, "other")
        assert other.get("/api/claims").json()["total"] == 0
        assert other.get("/api/stats").json()["all"] == 0
        for path in [f"/api/claims/{claim_id}", f"/api/jobs/{job_id}",
                     f"/api/jobs/{job_id}/source/claim", f"/api/jobs/{job_id}/source/chart",
                     f"/api/jobs/{job_id}/report"]:
            assert other.get(path).status_code == 404, path
        assert upload(other, claim_id=claim_id).status_code == 404
        assert other.put(f"/api/jobs/{job_id}/reviews/imaginary", json={"decision": "accepted"}).status_code == 404
        assert other.put(f"/api/claims/{claim_id}/assignment", json={"assignee_id": ids["other"]}).status_code == 403


def test_supervisor_assignment_is_effective_and_admin_has_no_clinical_access(accounts):
    from sentinel.accounts import totp_code
    client, db, settings, ids = accounts
    sign_in(client)
    created = upload(client).json()
    claim_id = created["id"]
    with TestClient(create_app(settings, db)) as supervisor:
        sign_in(supervisor, "supervisor", otp=totp_code(MFA_SECRET, time.time()))
        assert supervisor.get(f"/api/claims/{claim_id}").status_code == 200
        assert supervisor.put(f"/api/claims/{claim_id}/assignment", json={"assignee_id": ids["admin"]}).status_code == 422
        assert supervisor.put(f"/api/claims/{claim_id}/assignment", json={"assignee_id": ids["other"]}).status_code == 200
    assert client.get(f"/api/claims/{claim_id}").status_code == 404
    with TestClient(create_app(settings, db)) as admin:
        sign_in(admin, "admin", otp=totp_code(MFA_SECRET, time.time()))
        assert admin.get("/api/claims").status_code == 403
        assert admin.get(f"/api/jobs/{created['job_id']}/source/claim").status_code == 403
        assert upload(admin).status_code == 403
        assert admin.post("/api/samples").status_code == 403


def test_csrf_is_required_even_when_origin_is_absent(accounts):
    client, _, _, _ = accounts
    sign_in(client)
    csrf = client.headers.pop("X-CSRF-Token")
    assert client.post("/api/samples").status_code == 403
    assert client.delete("/api/session").status_code == 403
    assert client.post("/api/samples", headers={"X-CSRF-Token": "wrong"}).status_code == 403
    client.headers["X-CSRF-Token"] = csrf
    assert client.post("/api/samples", headers={"Origin": "https://unrelated.example"}).status_code == 403
    assert client.post("/api/samples", headers={"Origin": "null"}).status_code == 403
    assert client.post("/api/samples", headers={"Origin": "http://testserver"}).status_code == 202


def test_repeated_bad_passwords_are_throttled_persistently(accounts):
    client, db, settings, _ = accounts
    for _ in range(5):
        assert sign_in(client, password="incorrect").status_code == 401
    with TestClient(create_app(settings, db)) as second:
        assert sign_in(second).status_code == 429


def test_privileged_cookie_is_secure_over_https(accounts):
    client, db, settings, _ = accounts
    with TestClient(create_app(replace(settings, secure_cookies=True), db), base_url="https://testserver") as secure:
        result = sign_in(secure)
        assert "Secure" in result.headers["set-cookie"]
        assert secure.get("/api/claims").status_code == 200


def test_account_cli_provisions_disables_and_resets_without_password_arguments(tmp_path, monkeypatch, capsys):
    from sentinel.__main__ import main
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("SECRET_KEY_FILE", str(tmp_path / "cli.key"))
    monkeypatch.setenv("AUTH_MODE", "named")
    monkeypatch.setattr("getpass.getpass", lambda prompt: PASSWORD)
    main(["account-create", "Reviewer", "--roles", "reviewer"])
    settings = Settings(database_url=url, embedded_worker=False, auto_migrate=False,
                        secret_key_file=str(tmp_path / "cli.key"))
    db = Database(url)
    try:
        with TestClient(create_app(settings, db)) as client:
            assert sign_in(client).status_code == 200
            main(["account-disable", "reviewer"])
            assert client.get("/api/claims").status_code == 401
            assert sign_in(client).status_code == 401
            main(["account-enable", "reviewer"])
            main(["account-reset", "reviewer"])
            assert sign_in(client).status_code == 200
    finally:
        db.engine.dispose()
    assert PASSWORD not in capsys.readouterr().out


def test_cli_refuses_privileged_provisioning_until_local_mfa_is_confirmed(tmp_path, monkeypatch):
    from sentinel.__main__ import main
    from sentinel.db import Account
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'mfa-cli.db'}")
    monkeypatch.setenv("SECRET_KEY_FILE", str(tmp_path / "mfa-cli.key"))
    monkeypatch.setattr("getpass.getpass", lambda prompt: PASSWORD if "assword" in prompt else "invalid")
    with pytest.raises(SystemExit):
        main(["account-create", "supervisor", "--roles", "supervisor"])
    db = Database(f"sqlite:///{tmp_path / 'mfa-cli.db'}")
    try:
        with db.session() as session:
            assert session.scalar(select(Account)) is None
    finally:
        db.engine.dispose()


def test_additive_account_migration_keeps_existing_records_and_sources(tmp_path):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    from sentinel.config import alembic_resources, migrate
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    ini, scripts = alembic_resources()
    config = Config(str(ini))
    config.set_main_option("script_location", str(scripts))
    config.attributes["database_url"] = url
    command.upgrade(config, "0001")
    db = Database(url)
    try:
        with db.engine.begin() as connection:
            connection.execute(text("INSERT INTO claims (id,reference,patient_id,created_at) VALUES ('old','SYN-OLD','P-OLD',1)"))
        migrate(url)
        with db.engine.connect() as connection:
            row = connection.execute(text("SELECT reference,patient_id,assignee_id FROM claims WHERE id='old'")).one()
            assert tuple(row) == ("SYN-OLD", "P-OLD", None)
    finally:
        db.engine.dispose()


def test_named_login_is_available_as_a_local_page(accounts):
    client, _, _, _ = accounts
    page = client.get("/login")
    assert page.status_code == 200
    assert "current-password" in page.text
    assert client.get("/static/login.js").status_code == 200
    assert client.get("/static/login.css").status_code == 200


def test_login_validation_does_not_echo_credentials(accounts):
    client, _, _, _ = accounts
    oversized_password = "private-password-" * 20
    response = client.post("/api/session", json={"username": "reviewer", "password": oversized_password})
    assert response.status_code == 422
    assert oversized_password not in response.text


def test_one_totp_code_cannot_create_two_concurrent_sessions(accounts):
    from concurrent.futures import ThreadPoolExecutor

    from sentinel.accounts import totp_code
    _, db, settings, _ = accounts
    code = totp_code(MFA_SECRET, time.time())

    def login_once(_):
        with TestClient(create_app(settings, db)) as client:
            return sign_in(client, "supervisor", otp=code).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(login_once, range(2)))
    assert sorted(statuses) == [200, 401]

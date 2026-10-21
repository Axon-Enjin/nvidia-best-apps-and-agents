"""Capture real review-service responses that the web client's TypeScript types are checked against."""
import hashlib
import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from e2e.account_setup import PASSWORD, provision_reviewer
from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import SUPERVISOR_TOTP
from sentinel.accounts import SecretBox, create_local_account, totp_code
from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database
from sentinel.profile import RULE_VERSION
from sentinel.samples import development_bundle
from sentinel.worker import process_one

SAMPLES = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "lib" / "contract-samples"
IDENTITY = ("facility_id", "encounter_ref", "claim_ref", "patient_id")


def _sign_in(client, username, otp=""):
    response = client.post("/api/session", json={"username": username, "password": PASSWORD, "otp": otp})
    assert response.status_code == 200, response.text
    client.headers["X-CSRF-Token"] = response.json()["csrf_token"]


def _import(client, files, manifest, key):
    case = client.post("/api/cases", json={k: manifest[k] for k in IDENTITY})
    assert case.status_code == 201, case.text
    receipt = client.post(f"/api/claims/{case.json()['id']}/bundles", headers={"Idempotency-Key": key},
                          data={"manifest": json.dumps(manifest), "expected_revision": str(case.json()["revision"])},
                          files=[("files", (name, content, "application/octet-stream")) for name, content in files])
    assert receipt.status_code == 202, receipt.text
    return case.json(), receipt.json()


def _action(client, case_id, kind, **payload):
    case = client.get(f"/api/claims/{case_id}").json()
    response = client.post(f"/api/claims/{case_id}/review-events", json={
        "expected_revision": case["revision"], "bundle_id": case["current_bundle_id"],
        "rule_version": RULE_VERSION, "action": kind, **payload})
    assert response.status_code == 200, response.text
    return response.json()


def _anchors(bundle, kinds):
    return [{"document_id": d["id"], "page": 1} for d in bundle["documents"] if d["type"] in kinds]


def capture_samples(tmp_path: Path) -> dict[str, object]:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'contract.db'}", embedded_worker=False, auto_migrate=False,
                        secret_key_file=str(tmp_path / "key"), source_storage_root=str(tmp_path / "sources"))
    db = Database(settings.database_url)
    db.initialize()
    provision_reviewer(db, settings.secret_key_file)
    with db.session() as session:
        create_local_account(session, "supervisor", PASSWORD, {"supervisor"},
                             SecretBox.from_file(settings.secret_key_file), totp_secret=SUPERVISOR_TOTP)
    samples: dict[str, object] = {}
    app = create_app(settings, db)
    try:
        with TestClient(app) as client:
            _sign_in(client, "reviewer")
            samples["session"] = client.get("/api/session").json()
            samples["config"] = client.get("/api/config").json()

            # A discrepant claim whose CF2 is a printed scan awaiting confirmation.
            files, manifest = development_bundle("discrepant")
            scan = (FIXTURES / "scans" / "printed-cf2.png").read_bytes()
            files[0] = ("printed-cf2.png", scan)
            manifest["documents"][0].update(filename="printed-cf2.png", sha256=hashlib.sha256(scan).hexdigest())
            case, receipt = _import(client, files, manifest, "contract-discrepant")
            samples["case"], samples["bundle-receipt"] = case, receipt
            assert process_one(db, settings)
            samples["claim"] = client.get(f"/api/claims/{case['id']}").json()
            bundle = client.get(f"/api/claims/{case['id']}/bundles/1").json()
            samples["bundle"] = bundle
            scan_doc = bundle["documents"][0]
            field, value = next(iter(sorted(scan_doc["extraction"]["fields"].items())))
            confirmation = client.post(f"/api/documents/{scan_doc['id']}/confirm", json={
                "expected_revision": client.get(f"/api/claims/{case['id']}").json()["revision"],
                "anchor": {"page": 1, "field": field}, "value": value,
                "reason": "Read the legible printed source", "source_kind": "printed"})
            assert confirmation.status_code == 200, confirmation.text
            samples["confirmation"] = confirmation.json()
            _action(client, case["id"], "correction_created", reason="Discharge date differs", check_id="P05",
                    department="Records", person="Sample Clerk", anchors=_anchors(bundle, {"discharge"}))
            samples["review-state"] = _action(client, case["id"], "extra_expected", reason="Laboratory result named in the course")
            samples["queue"] = client.get("/api/claims").json()
            samples["stats"] = client.get("/api/stats").json()

            # A complete claim taken through manual review, a different supervisor and completion.
            files, manifest = development_bundle("complete")
            done, _ = _import(client, files, manifest, "contract-complete")
            assert process_one(db, settings)
            complete = client.get(f"/api/claims/{done['id']}/bundles/1").json()
            _action(client, done["id"], "manual_p07", reason="Compared narratives", anchors=_anchors(complete, {"cf2", "cf4", "cf5", "discharge"}))
            _action(client, done["id"], "manual_p08", reason="Marks present", anchors=_anchors(complete, {"cf2", "cf4", "cf5", "csf"}))
            with TestClient(app) as supervisor:
                _sign_in(supervisor, "supervisor", totp_code(SUPERVISOR_TOTP, time.time()))
                _action(supervisor, done["id"], "supervisor_ack", reason="Acknowledged the named comparison")
            claim = client.get(f"/api/claims/{done['id']}").json()
            report = client.post(f"/api/claims/{done['id']}/finalize", json={
                "expected_revision": claim["revision"], "bundle_id": claim["current_bundle_id"], "rule_version": RULE_VERSION})
            assert report.status_code == 201, report.text
            samples["report"] = report.json()
            samples["reports"] = client.get(f"/api/claims/{done['id']}/reports").json()
    finally:
        db.engine.dispose()
    return samples


def trim(value):
    """Keep one example of each distinct item shape per list; the structure (and its shape) is unchanged."""
    if isinstance(value, dict):
        return {key: trim(item) for key, item in value.items()}
    if isinstance(value, list):
        kept, seen = [], set()
        for item in value:
            key = json.dumps(shape(item), sort_keys=True)
            if key not in seen:
                seen.add(key)
                kept.append(trim(item))
        return kept
    return value


def shape(value):
    """JSON structure without values: keys and primitive types; list items as a sorted set of shapes."""
    if isinstance(value, dict):
        return {key: shape(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return ["list", sorted({json.dumps(shape(item), sort_keys=True) for item in value})]
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "null" if value is None else "string"

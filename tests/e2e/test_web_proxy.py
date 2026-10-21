"""The Next.js same-origin proxy keeps the review service's security boundary intact."""
import hashlib
import json

import httpx

from e2e.account_setup import PASSWORD
from e2e.web_helpers import api_client
from sentinel.samples import development_bundle


def test_sign_in_through_the_proxy_sets_a_strict_httponly_cookie(web_stack):
    response = httpx.post(web_stack.base + "/api/session", headers={"Origin": web_stack.base},
                          json={"username": "reviewer", "password": PASSWORD})
    assert response.status_code == 200, response.text
    cookie = response.headers["set-cookie"]
    assert "sentinel_session=" in cookie
    assert "httponly" in cookie.lower() and "samesite=strict" in cookie.lower() and "path=/" in cookie.lower()
    assert response.headers["cache-control"] == "no-store"
    assert web_stack.network_log.read_text() == ""


def test_mutation_from_a_foreign_origin_is_denied(web_stack):
    client = api_client(web_stack)
    response = client.post("/api/cases", headers={"Origin": "http://evil.example"},
                           json={"facility_id": "F", "encounter_ref": "E", "claim_ref": "C", "patient_id": "P"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Cross-origin changes are not allowed."


def test_mutation_without_csrf_is_denied(web_stack):
    client = api_client(web_stack)
    del client.headers["x-csrf-token"]
    response = client.post("/api/cases", json={"facility_id": "F", "encounter_ref": "E", "claim_ref": "C", "patient_id": "P"})
    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]


def test_private_api_responses_are_never_cacheable(web_stack):
    client = api_client(web_stack)
    for path in ("/api/session", "/api/claims", "/api/stats"):
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["cache-control"] == "no-store", path
    assert web_stack.network_log.read_text() == ""


def test_large_original_passes_through_the_proxy_intact(web_stack):
    files, manifest = development_bundle()
    name, content = files[6]
    filler = b"Synthetic filler line for the proxy body-size test.\n"
    padded = content + filler * ((12 * 1024 * 1024) // len(filler) + 1)
    files[6] = (name, padded)
    manifest["documents"][6]["sha256"] = hashlib.sha256(padded).hexdigest()
    client = api_client(web_stack)
    identity = {key: manifest[key] for key in ("facility_id", "encounter_ref", "claim_ref", "patient_id")}
    case = client.post("/api/cases", json=identity)
    assert case.status_code == 201, case.text
    upload = client.post(f"/api/claims/{case.json()['id']}/bundles",
                         data={"manifest": json.dumps(manifest), "expected_revision": str(case.json()["revision"])},
                         files=[("files", (filename, data, "application/octet-stream")) for filename, data in files],
                         headers={"Idempotency-Key": "large-original-1"})
    assert upload.status_code == 202, upload.text
    bundle = client.get(f"/api/claims/{case.json()['id']}/bundles/1").json()
    assert bundle["documents"][6]["byte_count"] == len(padded) > 12 * 1024 * 1024
    assert web_stack.network_log.read_text() == ""

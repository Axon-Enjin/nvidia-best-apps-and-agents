"""Shared helpers for browser tests of the Next.js frontend."""
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from e2e.account_setup import PASSWORD
from sentinel.accounts import totp_code

SUPERVISOR_TOTP = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
PRIVILEGED = {"supervisor", "admin"}


@dataclass
class WebStack:
    base: str
    api_base: str
    browser: object
    db: object
    settings: object
    network_log: Path


_last_step: dict[tuple[str, str], int] = {}


def otp_for(stack: WebStack, username: str) -> str:
    """A fresh code per sign-in. The server refuses a reused time step but accepts the next one."""
    if username not in PRIVILEGED:
        return ""
    key = (stack.api_base, username)
    while True:
        now = int(time.time()) // 30
        step = max(now, _last_step.get(key, -1) + 1)
        if step <= now + 1:
            _last_step[key] = step
            return totp_code(SUPERVISOR_TOTP, step * 30)
        time.sleep(1)


def sign_in(page, stack: WebStack, username: str = "reviewer", landing: str = "/claims") -> None:
    """Sign in through the real login page and wait for the landing page."""
    page.goto(stack.base + "/login")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password", exact=True).fill(PASSWORD)
    if username in PRIVILEGED:
        page.get_by_label("Authenticator code").fill(otp_for(stack, username))
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.wait_for_url(stack.base + landing)


SCREENSHOTS = Path(__file__).resolve().parents[2] / "test-results" / "web"


def snap(page, name: str) -> None:
    """Full-page screenshot for the visual review record (test-results/ is ignored by git)."""
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOTS / f"{name}.png"), full_page=True)


def no_horizontal_overflow(page) -> bool:
    return page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def wait_for_checks(client: httpx.Client, case_id: str, timeout: float = 60) -> dict:
    """Wait until the latest local check run for a claim has finished; return the claim."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        claim = client.get(f"/api/claims/{case_id}").json()
        if claim["latest"] and claim["latest"]["status"] in {"succeeded", "failed"}:
            return claim
        time.sleep(0.2)
    raise AssertionError(f"Checks for {case_id} did not finish")


def seed_case(stack: WebStack, label: str = "discrepant", username: str = "reviewer",
              claim_ref: str | None = None, files=None, manifest=None) -> str:
    """Create and import a synthetic bundle through the web origin, then wait for its checks."""
    import hashlib
    import json

    from sentinel.samples import development_bundle
    if files is None:
        files, manifest = development_bundle(label)
    manifest = {**manifest, "documents": [
        {**member, "filename": name, "sha256": hashlib.sha256(content).hexdigest()}
        for member, (name, content) in zip(manifest["documents"], files, strict=True)]}
    if claim_ref:
        manifest["claim_ref"] = claim_ref
    client = api_client(stack, username)
    identity = {key: manifest[key] for key in ("facility_id", "encounter_ref", "claim_ref", "patient_id")}
    case = client.post("/api/cases", json=identity)
    assert case.status_code == 201, case.text
    case_id = case.json()["id"]
    upload = client.post(f"/api/claims/{case_id}/bundles", headers={"Idempotency-Key": f"seed-{case_id}"},
                         data={"manifest": json.dumps(manifest), "expected_revision": str(case.json()["revision"])},
                         files=[("files", (name, content, "application/octet-stream")) for name, content in files])
    assert upload.status_code == 202, upload.text
    wait_for_checks(client, case_id)
    return case_id


def api_client(stack: WebStack, username: str = "reviewer") -> httpx.Client:
    """An HTTP client signed in through the web origin, as the browser would be."""
    client = httpx.Client(base_url=stack.base, headers={"Origin": stack.base}, timeout=30)
    response = client.post("/api/session", json={"username": username, "password": PASSWORD,
                                                 "otp": otp_for(stack, username)})
    assert response.status_code == 200, response.text
    client.headers["x-csrf-token"] = response.json()["csrf_token"]
    return client

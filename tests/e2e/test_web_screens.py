"""Captures the visual review set (test-results/web/screens/) and checks each screen fits its viewport."""
import time

from playwright.sync_api import expect

from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import SCREENSHOTS, api_client, no_horizontal_overflow, otp_for, seed_case, sign_in
from sentinel.profile import RULE_VERSION
from sentinel.samples import development_bundle

VIEWPORTS = {"desktop": {"width": 1366, "height": 768}, "mobile": {"width": 375, "height": 812}}
EVALUATION = FIXTURES / "evaluation"


def held_out(name):
    import json
    folder = EVALUATION / name
    manifest = json.loads((folder / "manifest.json").read_text())
    return [(member["filename"], (folder / member["filename"]).read_bytes()) for member in manifest["documents"]], manifest


def action(client, case_id, kind, **payload):
    claim = client.get(f"/api/claims/{case_id}").json()
    response = client.post(f"/api/claims/{case_id}/review-events", json={
        "expected_revision": claim["revision"], "bundle_id": claim["current_bundle_id"], "rule_version": RULE_VERSION,
        "action": kind, **payload})
    assert response.status_code == 200, response.text


def anchors(client, case_id, kinds):
    documents = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"]
    return [{"document_id": d["id"], "page": 1} for d in documents if d["type"] in kinds]


def completed_case(web_stack):
    files, manifest = held_out("heldout-21")
    case_id = seed_case(web_stack, files=files, manifest=manifest)
    reviewer = api_client(web_stack)
    action(reviewer, case_id, "manual_p07", reason="Compared narratives", anchors=anchors(reviewer, case_id, {"cf2", "cf4", "cf5", "discharge"}))
    action(reviewer, case_id, "manual_p08", reason="Marks present", anchors=anchors(reviewer, case_id, {"cf2", "cf4", "cf5", "csf"}))
    action(api_client(web_stack, "supervisor"), case_id, "supervisor_ack", reason="Acknowledged")
    claim = reviewer.get(f"/api/claims/{case_id}").json()
    assert reviewer.post(f"/api/claims/{case_id}/finalize", json={"expected_revision": claim["revision"],
        "bundle_id": claim["current_bundle_id"], "rule_version": RULE_VERSION}).status_code == 201
    return case_id


def test_capture_visual_review_set(web_stack):
    files, manifest = held_out("heldout-01")
    discrepant = seed_case(web_stack, files=files, manifest=manifest)
    files, manifest = development_bundle("discrepant")
    files[0] = ("printed-cf2.png", (FIXTURES / "scans" / "printed-cf2.png").read_bytes())
    scanned = seed_case(web_stack, files=files, manifest=manifest)
    files, manifest = held_out("heldout-31")
    seed_case(web_stack, files=files, manifest=manifest)
    done = completed_case(web_stack)
    files, manifest = held_out("heldout-02")
    corrected = seed_case(web_stack, files=files, manifest=manifest)
    client = api_client(web_stack)
    failing = next(c["id"] for c in client.get(f"/api/claims/{corrected}/review-state").json()["checks"] if c["status"] != "passed")
    action(client, corrected, "correction_created", check_id=failing, reason="Sources disagree; request a corrected original",
           department="Records", person="Sample Clerk", anchors=anchors(client, corrected, {"discharge", "cf2"}))
    task = client.get(f"/api/claims/{corrected}/review-state").json()["tasks"][0]["id"]
    action(client, corrected, "correction_handoff", task_id=task, reason="Handed over at the records desk")
    folder = SCREENSHOTS / "screens"
    folder.mkdir(parents=True, exist_ok=True)

    screens = [
        ("queue", "/claims"),
        ("intake", "/claims/new"),
        ("import-scan", f"/claims/{scanned}/import"),
        ("review-discrepancy", f"/claims/{discrepant}/review?issue=P05"),
        ("review-narrative", f"/claims/{discrepant}/review?issue=P07"),
        ("correction-progress", f"/claims/{corrected}/review?issue={failing}"),
        ("complete-blocked", f"/claims/{discrepant}/complete"),
        ("complete-done", f"/claims/{done}/complete"),
    ]
    for name, viewport in VIEWPORTS.items():
        context = web_stack.browser.new_context(viewport=viewport)
        page = context.new_page()
        page.goto(web_stack.base + "/login")
        page.screenshot(path=str(folder / f"login-{name}.png"))
        sign_in(page, web_stack)
        for screen, path in screens:
            page.goto(web_stack.base + path)
            expect(page.locator("main")).to_be_visible()
            if screen == "intake":
                page.get_by_label("Manifest (JSON)").set_input_files(str(FIXTURES / "development" / "discrepant" / "manifest.json"))
                page.get_by_label("Original documents").set_input_files(
                    [str(p) for p in (FIXTURES / "development" / "discrepant").iterdir() if p.name != "manifest.json"])
                expect(page.get_by_text("Selected", exact=True)).to_have_count(7)
            if screen == "import-scan":
                page.wait_for_function("() => [...document.images].every(image => image.complete)")
            time.sleep(0.2)
            assert no_horizontal_overflow(page), (screen, name)
            page.screenshot(path=str(folder / f"{screen}-{name}.png"), full_page=(name == "mobile"))
        context.close()
    supervisor = web_stack.browser.new_context(viewport=VIEWPORTS["desktop"])
    page = supervisor.new_page()
    page.goto(web_stack.base + "/login")
    page.get_by_label("Username").fill("supervisor")
    page.get_by_label("Password", exact=True).fill("synthetic reviewer passphrase 2026")
    page.get_by_label("Authenticator code").fill(otp_for(web_stack, "supervisor"))
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.wait_for_url(web_stack.base + "/claims")
    action(client, discrepant, "manual_p07", reason="Compared narratives against the four summaries",
           anchors=anchors(client, discrepant, {"cf2", "cf4", "cf5", "discharge"}))
    page.goto(f"{web_stack.base}/claims/{discrepant}/review?issue=P07")
    page.screenshot(path=str(folder / "supervisor-acknowledge-desktop.png"))
    assert web_stack.network_log.read_text() == ""

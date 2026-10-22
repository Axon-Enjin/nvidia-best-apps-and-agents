"""Corrections and manual reviews are real, attributable events; drafts survive expiry and conflicts."""
import hashlib
import json
import re

from playwright.sync_api import expect
from sqlalchemy import text

from e2e.account_setup import PASSWORD
from e2e.web_helpers import api_client, seed_case, sign_in, snap
from sentinel.profile import RULE_VERSION
from sentinel.samples import development_bundle


def events(client, case_id):
    return client.get(f"/api/claims/{case_id}/review-state").json()["events"]


def open_issue(web_stack, case_id, issue="P05", page=None):
    if page is None:
        page = web_stack.browser.new_page(viewport={"width": 1366, "height": 900})
        sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/review?issue={issue}")
    return page


def fill_correction(page, reason="Discharge date differs; request corrected source"):
    action = page.get_by_role("region", name="Next action")
    action.get_by_role("button", name="Request correction").click()
    action.get_by_label("Reason", exact=True).fill(reason)
    action.get_by_label("Responsible department").fill("Records")
    action.get_by_label("Responsible person").fill("Sample Clerk")
    action.get_by_role("checkbox", name="Discharge summary").check()
    return action


def test_correction_request_handoff_and_acknowledgement_persist(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    action = fill_correction(page)
    expect(action).to_contain_text("Selected evidence: Discharge summary page 1")
    action.get_by_role("button", name="Save correction request").click()
    progress = page.get_by_role("region", name="Correction progress")
    expect(progress).to_contain_text("Sample Clerk")
    expect(progress).to_contain_text("Records")
    progress.get_by_label("Note for this step").fill("Handed over locally to records desk")
    progress.get_by_role("button", name="Record handoff").click()
    expect(progress.get_by_role("button", name="Record acknowledgement")).to_be_visible()
    page.reload()
    progress = page.get_by_role("region", name="Correction progress")
    expect(progress.get_by_role("button", name="Record acknowledgement")).to_be_visible()
    expect(page.get_by_label("Review history")).to_contain_text("Handoff recorded")
    expect(page.get_by_label("Review history")).to_contain_text("Handed over locally")
    snap(page, "correction-progress-1366")
    progress.get_by_label("Note for this step").fill("Clerk acknowledged receipt locally")
    progress.get_by_role("button", name="Record acknowledgement").click()
    expect(progress.get_by_role("link", name="Import corrected version")).to_have_attribute("href", f"/claims/{case_id}/import")
    actions = [event["action"] for event in events(api_client(web_stack), case_id)]
    assert actions == ["correction_created", "correction_handoff", "correction_acknowledged"]


def test_stale_revision_keeps_the_draft_and_saves_after_loading_latest(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    action = fill_correction(page, reason="Draft written before the case changed")
    client = api_client(web_stack)
    claim = client.get(f"/api/claims/{case_id}").json()
    discharge = next(d for d in client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"] if d["type"] == "discharge")
    changed = client.post(f"/api/claims/{case_id}/review-events", json={
        "expected_revision": claim["revision"], "bundle_id": claim["current_bundle_id"], "rule_version": RULE_VERSION,
        "action": "correction_created", "check_id": "P05", "reason": "Someone else saved first", "department": "Records",
        "person": "Other Clerk", "anchors": [{"document_id": discharge["id"], "page": 1}]})
    assert changed.status_code == 200, changed.text
    before = len(events(client, case_id))
    action.get_by_role("button", name="Save correction request").click()
    expect(page.get_by_role("alert").filter(has_text="This case changed since you opened it.")).to_be_visible()
    assert action.get_by_label("Reason", exact=True).input_value() == "Draft written before the case changed"
    assert len(events(client, case_id)) == before
    action.get_by_role("button", name="Load latest").click()
    expect(page.get_by_role("alert").filter(has_text="This case changed")).to_have_count(0)
    assert action.get_by_label("Responsible person").input_value() == "Sample Clerk"
    action.get_by_role("button", name="Save correction request").click()
    expect(page.get_by_role("region", name="Correction progress")).to_be_visible()
    saved = events(client, case_id)
    assert len(saved) == before + 1 and saved[-1]["payload"]["reason"] == "Draft written before the case changed"


def test_expired_session_keeps_the_draft_without_replaying(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    action = fill_correction(page, reason="Draft that must survive sign-in")
    client = api_client(web_stack)
    before = len(events(client, case_id))
    with web_stack.db.session() as session:
        session.execute(text("UPDATE local_sessions SET revoked = 1"))
        session.commit()
    action.get_by_role("button", name="Save correction request").click()
    dialog = page.get_by_role("dialog", name="Sign in again to continue")
    expect(dialog).to_be_visible()
    expect(dialog).to_contain_text("Your session ended. Your unsaved work on this page is kept.")
    client = api_client(web_stack)
    assert len(events(client, case_id)) == before
    dialog.get_by_label("Password", exact=True).fill(PASSWORD)
    dialog.get_by_role("button", name="Sign in").click()
    expect(dialog).to_be_hidden()
    expect(page.get_by_text("Signed in again. Review your draft, then save.")).to_be_visible()
    assert action.get_by_label("Reason", exact=True).input_value() == "Draft that must survive sign-in"
    assert len(events(client, case_id)) == before
    action.get_by_role("button", name="Save correction request").click()
    expect(page.get_by_role("region", name="Correction progress")).to_be_visible()
    assert len(events(client, case_id)) == before + 1


def test_double_click_save_records_one_event(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    action = fill_correction(page)
    client = api_client(web_stack)
    before = len(events(client, case_id))
    action.get_by_role("button", name="Save correction request").dblclick()
    expect(page.get_by_role("region", name="Correction progress")).to_be_visible()
    page.wait_for_timeout(1000)
    assert len(events(client, case_id)) == before + 1
    expect(page.get_by_role("alert").filter(has_text="This case changed")).to_have_count(0)


def test_unsaved_input_warns_before_leaving(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    fill_correction(page, reason="Unsaved thought")
    dialogs = []

    def answer(dialog):
        dialogs.append((dialog.type, dialog.message))
        dialog.dismiss()

    page.on("dialog", answer)
    page.get_by_role("list", name="Issues needing attention").get_by_role("button", name=re.compile("Narrative agreement")).click()
    assert dialogs and dialogs[-1] == ("confirm", "Discard your unsaved draft?")
    expect(page).to_have_url(re.compile(r".*issue=P05$"))
    assert page.get_by_label("Reason", exact=True).input_value() == "Unsaved thought"
    # Headless Chromium never shows the native leave prompt, so check that the guard cancels the event.
    cancels = "() => { const event = new Event('beforeunload', { cancelable: true }); window.dispatchEvent(event); return event.defaultPrevented; }"
    assert page.evaluate(cancels) is True
    page.get_by_role("region", name="Next action").get_by_role("button", name="Save correction request").click()
    expect(page.get_by_role("region", name="Correction progress")).to_be_visible()
    assert page.evaluate(cancels) is False


def test_deterministic_checks_offer_no_dismissal(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_issue(web_stack, case_id)
    expect(page.get_by_text("Dismiss this narrative question")).to_have_count(0)
    open_issue(web_stack, case_id, "P07", page)
    expect(page.get_by_text("Dismiss this narrative question")).to_be_visible()


def test_manual_comparison_records_a_second_page_anchor(web_stack):
    files, manifest = development_bundle()
    name, content = files[1]
    files[1] = (name, content + b"\fSupplement: Fictional second-page course continuation.\n")
    manifest["documents"][1]["sha256"] = hashlib.sha256(files[1][1]).hexdigest()
    case_id = seed_case(web_stack, files=files, manifest=json.loads(json.dumps(manifest)))
    page = open_issue(web_stack, case_id, "P07")
    action = page.get_by_role("region", name="Next action")
    action.get_by_role("button", name="Record manual comparison").click()
    action.get_by_label("Comparison notes").fill("Compared narratives including the second-page continuation")
    for label in ("CF2 claim summary", "CF4 clinical summary", "CF5 supplementary summary", "Discharge summary"):
        action.get_by_role("checkbox", name=label).check()
    action.get_by_role("textbox", name="Pages for CF4 clinical summary").fill("2")
    action.get_by_role("button", name="Save manual comparison").click()
    expect(page.get_by_label("Review history")).to_contain_text("second-page continuation")
    saved = events(api_client(web_stack), case_id)[-1]
    assert saved["action"] == "manual_p07"
    assert any(anchor["page"] == 2 for anchor in saved["payload"]["anchors"])

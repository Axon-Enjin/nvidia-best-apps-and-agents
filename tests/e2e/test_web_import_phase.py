"""Case phases: resume where action is needed, real processing states, and scan confirmation beside the original."""
import re
import time

from playwright.sync_api import expect

from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import api_client, seed_case, sign_in, snap
from sentinel.samples import development_bundle

SCANS = FIXTURES / "scans"


def scan_bundle():
    files, manifest = development_bundle("discrepant")
    files[0] = ("printed-cf2.png", (SCANS / "printed-cf2.png").read_bytes())
    return files, manifest


def pending(client, case_id):
    review = client.get(f"/api/claims/{case_id}/review-state").json()
    return sum(len(requirement["pending"]) for requirement in review["confirmations"])


def test_returning_reviewer_resumes_where_action_is_needed(web_stack):
    discrepant = seed_case(web_stack, "discrepant")
    files, manifest = scan_bundle()
    scanned = seed_case(web_stack, files=files, manifest=manifest)
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{discrepant}")
    page.wait_for_url(f"{web_stack.base}/claims/{discrepant}/review")
    page.goto(f"{web_stack.base}/claims/{scanned}")
    page.wait_for_url(f"{web_stack.base}/claims/{scanned}/import")
    phases = page.get_by_role("navigation", name="Case phases")
    expect(phases.get_by_role("link", name=re.compile("Import"))).to_have_attribute("aria-current", "page")
    expect(phases).to_contain_text("scan values to confirm")


def test_scan_values_are_confirmed_beside_the_original(web_stack):
    files, manifest = scan_bundle()
    case_id = seed_case(web_stack, files=files, manifest=manifest)
    client = api_client(web_stack)
    raw = client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]["extraction"]
    page = web_stack.browser.new_page(viewport={"width": 1366, "height": 900})
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/import")
    section = page.get_by_role("region", name="Confirm scanned values")
    original = section.get_by_role("img", name=re.compile("Original CF2 claim summary, page 1"))
    expect(original).to_be_visible()
    page.wait_for_function("image => image.complete && image.naturalWidth > 0", arg=original.element_handle())
    snap(page, "scan-confirmation-1366")
    remaining = pending(client, case_id)
    assert remaining > 0
    reason = section.get_by_label("Confirmation reason")
    while remaining:
        expect(section.get_by_label("Confirmed value")).not_to_have_value("")
        section.get_by_label("I can read this printed source").check()
        if not reason.input_value():
            reason.fill("Read the legible printed source")
        section.get_by_role("button", name="Confirm value").click()
        deadline = time.monotonic() + 15
        while pending(client, case_id) == remaining and time.monotonic() < deadline:
            time.sleep(0.1)
        assert pending(client, case_id) == remaining - 1
        remaining -= 1
        if remaining:
            expect(section.get_by_label("I can read this printed source")).not_to_be_checked()
    phases = page.get_by_role("navigation", name="Case phases")
    expect(phases).not_to_contain_text("scan value")
    expect(page.get_by_role("link", name="Continue to review")).to_be_visible()
    assert client.get(f"/api/claims/{case_id}/bundles/1").json()["documents"][0]["extraction"] == raw


def test_processing_status_is_real_and_polling_stops(web_stack):
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.goto(web_stack.base + "/claims/new")
    folder = FIXTURES / "development" / "discrepant"
    page.get_by_label("Manifest (JSON)").set_input_files(str(folder / "manifest.json"))
    page.get_by_label("Original documents").set_input_files([str(p) for p in folder.iterdir() if p.name != "manifest.json"])
    page.get_by_role("button", name="Import and check").click()
    page.wait_for_url(re.compile(r".*/claims/[0-9a-f]{32}/import$"))
    case_id = re.search(r"/claims/([0-9a-f]{32})/", page.url).group(1)
    expect(page.get_by_text(re.compile("^(Queued for local checks|Checks are running|Checks complete)"))).to_be_visible()
    expect(page.get_by_text(re.compile("^Checks complete"))).to_be_visible(timeout=30000)
    polls = []
    page.on("request", lambda request: polls.append(request.url) if request.url.endswith(f"/api/claims/{case_id}") else None)
    page.wait_for_timeout(3000)
    assert len(polls) <= 1


def test_unreadable_and_unsupported_documents_are_distinguished(web_stack):
    files, manifest = development_bundle("discrepant")
    files[0] = ("unreadable.png", (SCANS / "unreadable.png").read_bytes())
    files.append(("attachment.bin", b"\x00\xff" * 1024))
    manifest["documents"].append({"type": "attachment", "filename": "attachment.bin", "sha256": ""})
    case_id = seed_case(web_stack, files=files, manifest=manifest)
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/import")
    table = page.get_by_role("table", name="Documents in version 1")
    expect(table.get_by_role("row", name=re.compile("CF2 claim summary"))).to_contain_text("Unreadable")
    expect(table.get_by_role("row", name=re.compile("Attachment attachment.bin"))).to_contain_text("Unsupported format")


def test_double_activation_confirms_one_value(web_stack):
    files, manifest = scan_bundle()
    case_id = seed_case(web_stack, files=files, manifest=manifest)
    client = api_client(web_stack)
    before = pending(client, case_id)
    page = web_stack.browser.new_page(viewport={"width": 1366, "height": 900})
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/import")
    section = page.get_by_role("region", name="Confirm scanned values")
    section.get_by_label("I can read this printed source").check()
    section.get_by_label("Confirmation reason").fill("Read the legible printed source")
    section.get_by_role("button", name="Confirm value").dblclick()
    deadline = time.monotonic() + 15
    while pending(client, case_id) == before and time.monotonic() < deadline:
        time.sleep(0.1)
    page.wait_for_timeout(1000)
    assert pending(client, case_id) == before - 1
    expect(page.get_by_role("alert").filter(has_text="Case changed")).to_have_count(0)

"""One clear intake: the manifest names each original, and import stays unavailable until they all match."""
import json
import re

from playwright.sync_api import expect

from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import api_client, sign_in, snap

FIXTURE = FIXTURES / "development" / "discrepant"


def originals(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    return [folder / member["filename"] for member in manifest["documents"]]


def open_intake(web_stack):
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.get_by_role("link", name="Import a claim").click()
    page.wait_for_url(web_stack.base + "/claims/new")
    return page


def test_intake_lists_manifest_documents_and_blocks_until_matched(web_stack, tmp_path):
    page = open_intake(web_stack)
    page.get_by_label("Manifest (JSON)").set_input_files(str(FIXTURE / "manifest.json"))
    rows = page.get_by_role("list", name="Documents named in the manifest")
    expect(rows.get_by_role("listitem")).to_have_count(7)
    expect(rows.get_by_text("Missing", exact=True)).to_have_count(7)
    submit = page.get_by_role("button", name="Import and check")
    expect(submit).to_have_attribute("aria-disabled", "true")
    expect(page.get_by_text("Select every document named in the manifest to continue.")).to_be_visible()

    wrong = tmp_path / "cf2.txt"
    wrong.write_text("Claim Ref: A DIFFERENT DOCUMENT\n")
    extra = tmp_path / "notes.txt"
    extra.write_text("Unrelated note\n")
    others = [str(path) for path in originals(FIXTURE) if path.name != "cf2.txt"]
    page.get_by_label("Original documents").set_input_files([*others, str(wrong), str(extra)])
    expect(rows.get_by_text("Does not match the manifest's SHA-256")).to_be_visible()
    expect(rows.get_by_text("Not named in the manifest")).to_be_visible()
    expect(submit).to_have_attribute("aria-disabled", "true")
    snap(page, "intake-mismatch-1280")

    page.get_by_label("Original documents").set_input_files([str(path) for path in originals(FIXTURE)])
    expect(rows.get_by_text("Selected", exact=True)).to_have_count(7)
    expect(submit).not_to_have_attribute("aria-disabled", "true")
    submit.click()
    page.wait_for_url(re.compile(r".*/claims/[0-9a-f]{32}/import$"))
    case_id = re.search(r"/claims/([0-9a-f]{32})/", page.url).group(1)
    claim = api_client(web_stack).get(f"/api/claims/{case_id}").json()
    assert claim["reference"] == "SYN-CLAIM-1" and len(claim["bundles"]) == 1
    assert web_stack.network_log.read_text() == ""


def test_file_inputs_are_reachable_by_keyboard(web_stack):
    page = open_intake(web_stack)
    page.get_by_label("Manifest (JSON)").focus()
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.type") == "file"
    assert page.evaluate("document.activeElement.id") == page.get_by_label("Original documents").get_attribute("id")


def test_retry_after_failed_upload_reuses_case_and_key(web_stack):
    page = open_intake(web_stack)
    keys = []

    def drop_first_upload(route):
        keys.append(route.request.headers.get("idempotency-key"))
        if len(keys) == 1:
            route.abort()
        else:
            route.continue_()

    page.route("**/api/claims/*/bundles", drop_first_upload)
    page.get_by_label("Manifest (JSON)").set_input_files(str(FIXTURE / "manifest.json"))
    page.get_by_label("Original documents").set_input_files([str(path) for path in originals(FIXTURE)])
    rows = page.get_by_role("list", name="Documents named in the manifest")
    expect(rows.get_by_text("Selected", exact=True)).to_have_count(7)
    page.get_by_role("button", name="Import and check").click()
    expect(page.get_by_role("alert").filter(has_text="Cannot reach the review service")).to_be_visible()
    expect(rows.get_by_text("Selected", exact=True)).to_have_count(7)
    page.get_by_role("button", name="Import and check").click()
    page.wait_for_url(re.compile(r".*/claims/[0-9a-f]{32}/import$"))
    assert len(keys) == 2 and keys[0] == keys[1] and keys[0]
    client = api_client(web_stack)
    queue = client.get("/api/claims").json()
    assert queue["total"] == 1
    assert len(client.get(f"/api/claims/{queue['items'][0]['id']}").json()["bundles"]) == 1

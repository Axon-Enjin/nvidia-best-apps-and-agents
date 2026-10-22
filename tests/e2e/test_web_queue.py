"""The claims queue keeps its filters in the URL and remembers the claim a reviewer opened."""
import re

from playwright.sync_api import expect

from e2e.web_helpers import seed_case, sign_in, snap


def test_filters_live_in_the_url_and_survive_opening_a_claim(web_stack):
    ids = {ref: seed_case(web_stack, label, claim_ref=ref)
           for ref, label in [("SYN-QUEUE-1", "discrepant"), ("SYN-QUEUE-2", "complete"), ("OTHER-9", "incomplete")]}
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    expect(page.get_by_role("heading", name="Claims", level=1)).to_be_visible()
    queue = page.get_by_role("table", name="Claims queue")
    expect(queue.get_by_role("link")).to_have_count(3)
    page.get_by_label("Search claims").fill("QUEUE")
    page.wait_for_url(re.compile(r".*/claims\?q=QUEUE$"))
    expect(queue.get_by_role("link")).to_have_count(2)
    filters = page.get_by_role("navigation", name="Queue filter")
    filters.get_by_role("link", name=re.compile("^Needs review")).click()
    page.wait_for_url(re.compile(r".*/claims\?view=needs_review&q=QUEUE$"))
    expect(filters.get_by_role("link", name=re.compile("^Needs review"))).to_have_attribute("aria-current", "page")
    expect(page.get_by_label("Search claims")).to_have_value("QUEUE")
    queue.get_by_role("link", name="SYN-QUEUE-2").click()
    page.wait_for_url(re.compile(rf".*/claims/{ids['SYN-QUEUE-2']}(/.*)?$"))
    page.get_by_role("link", name="Sentinel Claims").click()
    page.wait_for_url(re.compile(r".*/claims\?view=needs_review&q=QUEUE$"))
    expect(queue.get_by_role("row", name=re.compile("SYN-QUEUE-2"))).to_have_attribute("aria-current", "true")
    page.set_viewport_size({"width": 1366, "height": 768})
    snap(page, "queue-1366")
    page.go_back()
    page.wait_for_url(re.compile(rf".*/claims/{ids['SYN-QUEUE-2']}(/.*)?$"))
    assert web_stack.network_log.read_text() == ""


def test_legacy_case_link_opens_the_claim(web_stack):
    case_id = seed_case(web_stack)
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/#case={case_id}")
    page.wait_for_url(re.compile(rf".*/claims/{case_id}(/.*)?$"))


def test_empty_queue_explains_the_next_action(web_stack):
    seed_case(web_stack)  # assigned to the reviewer, never visible to the outsider
    page = web_stack.browser.new_page()
    sign_in(page, web_stack, "outsider")
    expect(page.get_by_text("No claims match. Import a claim to start a review.")).to_be_visible()
    expect(page.get_by_role("link", name="Import a claim")).to_have_attribute("href", "/claims/new")


def test_account_without_clinical_role_sees_an_explanation(web_stack):
    page = web_stack.browser.new_page()
    sign_in(page, web_stack, "admin")
    expect(page.get_by_text("Your account has no reviewer or supervisor role. Ask your operator to update it.")).to_be_visible()
    expect(page.get_by_role("table", name="Claims queue")).to_have_count(0)


def test_queue_does_not_render_every_claim_in_advance(web_stack):
    for ref in ("SYN-PREFETCH-1", "SYN-PREFETCH-2", "SYN-PREFETCH-3"):
        seed_case(web_stack, "discrepant", claim_ref=ref)
    page = web_stack.browser.new_page()
    claim_renders = []
    page.on("request", lambda r: claim_renders.append(r.url) if re.search(r"/claims/[0-9a-f]{32}(/[a-z]+)?\?_rsc=", r.url) else None)
    sign_in(page, web_stack)
    expect(page.get_by_role("table", name="Claims queue").get_by_role("link")).to_have_count(3)
    page.wait_for_timeout(2000)
    assert claim_renders == []

"""Review: each unresolved issue beside the exact source values and pages that establish it."""
import re

from playwright.sync_api import expect

from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import api_client, no_horizontal_overflow, seed_case, sign_in, snap
from sentinel.samples import development_bundle


def open_review(web_stack, case_id, viewport=None, scale=1):
    context = web_stack.browser.new_context(viewport=viewport or {"width": 1366, "height": 768}, device_scale_factor=scale)
    page = context.new_page()
    sign_in(page, web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/review")
    return page


def test_date_discrepancy_shows_both_values_with_exact_sources(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_review(web_stack, case_id)
    issues = page.get_by_role("list", name="Issues needing attention")
    issues.get_by_role("button", name=re.compile("Dates and discharge status")).click()
    expect(page).to_have_url(re.compile(r".*/review\?issue=P05$"))
    selected = page.get_by_role("region", name="Selected issue")
    expect(selected).to_contain_text("P05")
    differs = page.get_by_role("table", name="What differs")
    expect(differs).to_contain_text("Discharge date")
    first = differs.get_by_role("row", name=re.compile("2026-10-14"))
    second = differs.get_by_role("row", name=re.compile("2026-10-15"))
    expect(differs).to_contain_text("Source in version 1")
    expect(first).to_contain_text("CF2 claim summary · page 1")
    expect(second).to_contain_text("Discharge summary · page 1")
    letter = second.locator("[data-mark]").first.get_attribute("data-mark")
    evidence = page.get_by_role("region", name="Source evidence")
    evidence.get_by_role("tab", name=re.compile("Discharge summary")).click()
    mark = evidence.get_by_label("Source text").locator(f'mark[data-mark="{letter}"]')
    expect(mark).to_have_text(re.compile("2026-10-15"))
    expect(selected.get_by_role("list", name="Why this blocks completion")).to_contain_text("Discharge date differs between documents.")
    snap(page, "discrepancy-evidence-1366")
    assert web_stack.network_log.read_text() == ""


def test_passed_checks_are_disclosed_not_hidden(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = open_review(web_stack, case_id)
    disclosure = page.locator("details").filter(has=page.get_by_text(re.compile(r"^Passed checks \(\d+\)$")))
    expect(disclosure).not_to_have_attribute("open", "")
    expect(disclosure.get_by_text("Statement of account arithmetic")).to_be_hidden()
    disclosure.get_by_text(re.compile(r"^Passed checks")).click()
    expect(disclosure.get_by_role("button", name=re.compile("Statement of account arithmetic"))).to_be_visible()
    expect(disclosure).to_contain_text("P06")


def test_review_is_keyboard_operable_and_responsive(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    for viewport, scale in (({"width": 1366, "height": 768}, 1), ({"width": 375, "height": 812}, 1), ({"width": 683, "height": 384}, 2)):
        page = open_review(web_stack, case_id, viewport, scale)
        target = page.get_by_role("list", name="Issues needing attention").get_by_role("button", name=re.compile("Dates and discharge status"))
        page.get_by_role("link", name="Skip to main content").focus()
        for _ in range(60):
            page.keyboard.press("Tab")
            if target.evaluate("element => element === document.activeElement"):
                break
        assert target.evaluate("element => element === document.activeElement")
        outline = target.evaluate("element => parseFloat(getComputedStyle(element).outlineWidth)")
        assert outline >= 2
        covered = target.evaluate("""element => {
            const box = element.getBoundingClientRect();
            const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
            return !(hit && (hit === element || element.contains(hit)));
        }""")
        assert not covered
        page.keyboard.press("Enter")
        expect(page).to_have_url(re.compile(r".*issue=P05$"))
        assert no_horizontal_overflow(page)
        if viewport["width"] == 375:
            page.get_by_role("link", name="View source").click()
            assert page.evaluate("document.activeElement.closest('[aria-label=\"Source evidence\"]') !== null")
            snap(page, "discrepancy-evidence-375")
        page.context.close()


def test_scan_readings_are_not_shown_as_evidence(web_stack):
    files, manifest = development_bundle("discrepant")
    files[0] = ("printed-cf2.png", (FIXTURES / "scans" / "printed-cf2.png").read_bytes())
    case_id = seed_case(web_stack, files=files, manifest=manifest)
    page = open_review(web_stack, case_id)
    page.get_by_role("list", name="Issues needing attention").get_by_role("button", name=re.compile("Required documents")).click()
    evidence = page.get_by_role("region", name="Source evidence")
    evidence.get_by_role("tab", name=re.compile("CF2 claim summary")).click()
    panel = evidence.get_by_role("tabpanel")
    expect(panel).to_contain_text("This scan needs confirmation before its values count.")
    expect(panel.locator("mark")).to_have_count(0)
    action = page.get_by_role("region", name="Next action")
    expect(action.get_by_role("link", name="Confirm scanned values")).to_have_attribute("href", f"/claims/{case_id}/import")


def test_opening_sources_records_no_review_event(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    client = api_client(web_stack)
    before = len(client.get(f"/api/claims/{case_id}/review-state").json()["events"])
    page = open_review(web_stack, case_id)
    issues = page.get_by_role("list", name="Issues needing attention")
    for name in ("Dates and discharge status", "Narrative agreement"):
        issues.get_by_role("button", name=re.compile(name)).click()
        evidence = page.get_by_role("region", name="Source evidence")
        for tab in evidence.get_by_role("tab").all()[:3]:
            tab.click()
            evidence.get_by_role("button", name="Original").click()
            evidence.get_by_role("button", name="Extracted text").click()
    assert len(client.get(f"/api/claims/{case_id}/review-state").json()["events"]) == before

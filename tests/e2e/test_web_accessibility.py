"""Keyboard, focus, zoom, reduced motion, contrast and status semantics across the new frontend."""
import re

from playwright.sync_api import expect

from e2e.web_helpers import no_horizontal_overflow, seed_case, sign_in

FOCUS_VISIBLE = """element => {
    const style = getComputedStyle(element);
    const box = element.getBoundingClientRect();
    const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    return {
        outline: style.outlineStyle !== 'none' ? parseFloat(style.outlineWidth) : 0,
        covered: !(hit && (hit === element || element.contains(hit) || hit.contains(element))),
        tag: element.tagName, label: (element.getAttribute('aria-label') || element.textContent || '').trim().slice(0, 40),
    };
}"""

CONTRAST = """element => {
    const parse = value => value.match(/[\\d.]+/g).slice(0, 4).map(Number);
    const background = node => {
        for (let current = node; current; current = current.parentElement) {
            const [r, g, b, a = 1] = parse(getComputedStyle(current).backgroundColor);
            if (a > 0.99) return [r, g, b];
        }
        return [255, 255, 255];
    };
    const luminance = ([r, g, b]) => [r, g, b].map(v => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
        .reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
    const [fg, bg] = [parse(getComputedStyle(element).color).slice(0, 3), background(element)].map(luminance);
    return (Math.max(fg, bg) + 0.05) / (Math.min(fg, bg) + 0.05);
}"""


def new_page(web_stack, width=1366, height=768, scale=1, reduced=None):
    context = web_stack.browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=scale,
                                            reduced_motion=reduced or "no-preference")
    page = context.new_page()
    sign_in(page, web_stack)
    return page


def tab_to(page, locator, limit=120):
    for _ in range(limit):
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement !== document.body"), "focus fell back to the page body"
        if locator.evaluate("element => element === document.activeElement"):
            return
    raise AssertionError("Could not reach the element by keyboard")


def test_keyboard_reaches_every_phase_action(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = new_page(web_stack)
    tab_to(page, page.get_by_role("table", name="Claims queue").get_by_role("link").first)
    page.keyboard.press("Enter")
    page.wait_for_url(f"{web_stack.base}/claims/{case_id}/review")
    tab_to(page, page.get_by_role("navigation", name="Issues").get_by_role("button", name=re.compile("Dates and discharge status")))
    page.keyboard.press("Enter")
    action = page.get_by_role("region", name="Next action")
    tab_to(page, action.get_by_role("button", name="Request correction"))
    page.keyboard.press("Enter")
    expect(action.get_by_label("Reason", exact=True)).to_be_focused()
    page.keyboard.type("Keyboard-only correction request")
    page.keyboard.press("Tab")
    page.keyboard.type("Records")
    page.keyboard.press("Tab")
    page.keyboard.type("Sample Clerk")
    tab_to(page, action.get_by_role("checkbox", name="Discharge summary"))
    page.keyboard.press("Space")
    tab_to(page, action.get_by_role("button", name="Save correction request"))
    page.keyboard.press("Enter")
    expect(page.get_by_role("region", name="Correction progress")).to_be_visible()
    page.get_by_role("link", name="Skip to main content").focus()
    tab_to(page, page.get_by_role("navigation", name="Case phases").get_by_role("link", name=re.compile("Complete")))
    page.keyboard.press("Enter")
    page.wait_for_url(f"{web_stack.base}/claims/{case_id}/complete")
    tab_to(page, page.get_by_role("button", name="Complete review"))


def test_focus_is_never_obscured(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    for width, height in ((1366, 768), (375, 812)):
        page = new_page(web_stack, width, height)
        for path in ("/claims", f"/claims/{case_id}/review", f"/claims/{case_id}/complete", f"/claims/{case_id}/import"):
            page.goto(web_stack.base + path)
            page.keyboard.press("Tab")
            seen = set()
            for _ in range(70):
                handle = page.evaluate_handle("document.activeElement")
                result = handle.evaluate(FOCUS_VISIBLE)
                key = (result["tag"], result["label"])
                if key in seen and result["tag"] == "A" and result["label"].startswith("Skip"):
                    break
                seen.add(key)
                if result["tag"] != "BODY":
                    assert result["outline"] >= 2, (path, width, result)
                    assert not result["covered"], (path, width, result)
                page.keyboard.press("Tab")
        page.context.close()


def test_layout_holds_at_375_1366_and_200_percent_zoom(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    for width, height, scale in ((375, 812, 1), (1366, 768, 1), (683, 384, 2)):
        page = new_page(web_stack, width, height, scale)
        for path in ("/claims", "/claims/new", f"/claims/{case_id}/import", f"/claims/{case_id}/review", f"/claims/{case_id}/complete"):
            page.goto(web_stack.base + path)
            assert no_horizontal_overflow(page), (path, width, scale)
        clipped = page.evaluate("""() => [...document.querySelectorAll('nav[aria-label="Issues"] button span, h1, h2')]
            .filter(element => element.scrollWidth > element.clientWidth + 1).map(element => element.textContent)""")
        assert clipped == [], (width, clipped)
        page.context.close()


def test_reduced_motion_removes_transitions(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = new_page(web_stack, reduced="reduce")
    page.goto(f"{web_stack.base}/claims/{case_id}/review")
    selected = page.get_by_role("navigation", name="Issues").locator("button[aria-current=true]")
    assert selected.evaluate("element => getComputedStyle(element).transitionDuration") == "0s"


def test_status_is_text_not_only_color_and_contrast_holds(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = new_page(web_stack)
    page.goto(f"{web_stack.base}/claims/{case_id}/review")
    for button in page.get_by_role("navigation", name="Issues").get_by_role("button").all():
        assert re.search(r"(Discrepancy|Incomplete|Unsupported|Needs manual review|Passed|Correction to resolve)", button.inner_text())
    samples = {
        "body": page.locator("main p").first,
        "muted": page.locator("main .text-ink-muted").first,
        "blocking status": page.locator("main .text-blocking").first,
        "attention status": page.locator("main .text-attention").first,
        "primary button": page.locator("main .btn-primary").first,
        "document reference": page.locator("main .doc-ref").first,
    }
    for name, locator in samples.items():
        ratio = locator.evaluate(CONTRAST)
        assert ratio >= 4.5, (name, ratio)
    page.goto(f"{web_stack.base}/claims")
    for row in page.get_by_role("table", name="Claims queue").get_by_role("row").all()[1:]:
        assert re.search(r"(Processing|Needs review|Checks unavailable|No sources yet|Completed|Checks failed)", row.inner_text())


def test_live_status_announces_saves_once(web_stack):
    case_id = seed_case(web_stack, "discrepant")
    page = new_page(web_stack)
    for path in ("/claims", f"/claims/{case_id}/review", f"/claims/{case_id}/complete", f"/claims/{case_id}/import"):
        page.goto(web_stack.base + path)
        assert page.locator("[role=status]").count() == 1, path
    page.goto(web_stack.base + "/claims")
    calls = []
    page.on("request", lambda request: calls.append(request.url) if "/api/" in request.url else None)
    page.wait_for_timeout(5000)
    assert calls == []

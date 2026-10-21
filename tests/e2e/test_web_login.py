"""Named sign-in, privileged MFA and sign-out through the Next.js frontend."""
import re

from playwright.sync_api import expect, sync_playwright

from e2e.account_setup import PASSWORD
from e2e.web_helpers import no_horizontal_overflow, otp_for, sign_in
from e2e.web_server import free_port, start_web, stop_web


def test_sign_in_is_responsive_keyboard_operable_and_local(web_stack):
    base = web_stack.base
    for viewport in ({"width": 1366, "height": 768}, {"width": 375, "height": 812}):
        context = web_stack.browser.new_context(viewport=viewport)
        page = context.new_page()
        external, errors = [], []
        page.on("request", lambda r, external=external: external.append(r.url) if not r.url.startswith(base + "/") else None)
        page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
        page.goto(base + "/claims")
        assert page.url == base + "/login?next=%2Fclaims"
        page.get_by_label("Username").fill("reviewer")
        page.get_by_label("Password", exact=True).fill("incorrect")
        page.get_by_role("button", name="Sign in", exact=True).click()
        expect(page.get_by_role("alert").filter(has_text="Sign-in failed.")).to_be_visible()
        assert page.get_by_label("Password", exact=True).input_value() == "incorrect"
        assert page.locator("#login-error").evaluate("element => document.activeElement === element")
        assert no_horizontal_overflow(page)
        page.get_by_label("Password", exact=True).fill(PASSWORD)
        page.get_by_label("Password", exact=True).press("Enter")
        page.wait_for_url(base + "/claims")
        assert page.request.get(base + "/api/session").json()["actor"]["username"] == "reviewer"
        expect(page.get_by_text("Evaluation workspace: sample patient records")).to_be_visible()
        assert no_horizontal_overflow(page)
        assert external == [] and errors == []
        context.close()
    assert web_stack.network_log.read_text() == ""


def test_privileged_sign_in_requires_an_authenticator_code(web_stack):
    page = web_stack.browser.new_page()
    page.goto(web_stack.base + "/login")
    page.get_by_label("Username").fill("supervisor")
    page.get_by_label("Password", exact=True).fill(PASSWORD)
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_role("alert").filter(has_text="Sign-in failed.")).to_be_visible()
    page.get_by_label("Authenticator code").fill(otp_for(web_stack, "supervisor"))
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.wait_for_url(web_stack.base + "/claims")
    expect(page.get_by_role("banner")).to_contain_text("supervisor")


def test_sign_out_ends_the_session(web_stack):
    page = web_stack.browser.new_page()
    sign_in(page, web_stack)
    page.get_by_role("button", name="Sign out").click()
    page.wait_for_url(re.compile(r".*/login$"))
    assert page.request.get(web_stack.base + "/api/session").json()["authenticated"] is False
    page.goto(web_stack.base + "/claims")
    assert page.url.startswith(web_stack.base + "/login")


def test_unsafe_next_falls_back_to_claims(web_stack):
    page = web_stack.browser.new_page()
    page.goto(web_stack.base + "/login?next=//evil.example")
    page.get_by_label("Username").fill("reviewer")
    page.get_by_label("Password", exact=True).fill(PASSWORD)
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.wait_for_url(web_stack.base + "/claims")


def test_pages_carry_strict_security_headers(web_stack):
    page = web_stack.browser.new_page()
    response = page.goto(web_stack.base + "/login")
    headers = response.headers
    assert "nonce-" in headers["content-security-policy"]
    assert "frame-ancestors 'none'" in headers["content-security-policy"]
    assert headers["x-frame-options"] == "DENY"
    sign_in(page, web_stack)
    claims = page.request.get(web_stack.base + "/claims")
    assert "no-store" in claims.headers["cache-control"]


def test_unreachable_review_service_is_explained(tmp_path):
    port = free_port()
    closed = f"http://127.0.0.1:{free_port()}"
    web = start_web(closed, port, tmp_path / "network.log")
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}/login")
            page.get_by_label("Username").fill("reviewer")
            page.get_by_label("Password", exact=True).fill(PASSWORD)
            page.get_by_role("button", name="Sign in", exact=True).click()
            expect(page.get_by_role("alert").filter(has_text="Cannot reach the review service")).to_be_visible()
            browser.close()
    finally:
        stop_web(web)

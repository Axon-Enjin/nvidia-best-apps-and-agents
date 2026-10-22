"""Full review through the Next.js frontend: import to export, restart, a denied second account,
and loopback-only networking for the browser, the Next.js server and the review service."""
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

from e2e.account_setup import PASSWORD, provision_reviewer
from e2e.fixture_paths import FIXTURES
from e2e.web_helpers import SUPERVISOR_TOTP, WebStack, sign_in, snap
from e2e.web_server import free_port, start_web, stop_web
from sentinel.accounts import SecretBox, create_local_account
from sentinel.config import Settings, migrate
from sentinel.db import Database

ROOT = FIXTURES / "evaluation" / "heldout-01"


def originals(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    return [str(folder / member["filename"]) for member in manifest["documents"]]


def choose_bundle(scope, folder):
    scope.get_by_label("Manifest (JSON)").set_input_files(str(folder / "manifest.json"))
    scope.get_by_label("Original documents").set_input_files(originals(folder))
    expect(scope.get_by_role("list", name="Documents named in the manifest").get_by_text("Selected", exact=True)).to_have_count(7)
    scope.get_by_role("button", name="Import and check").click()


def issue(page, name):
    page.get_by_role("navigation", name="Issues").get_by_role("button", name=re.compile(name)).click()


def record(page, reveal, notes_label, notes, evidence, submit):
    action = page.get_by_role("region", name="Next action")
    action.get_by_role("button", name=reveal).click()
    action.get_by_label(notes_label).fill(notes)
    for label in evidence:
        action.get_by_role("checkbox", name=label).check()
    action.get_by_role("button", name=submit).click()


def phase(page, name):
    page.get_by_role("navigation", name="Case phases").get_by_role("link", name=re.compile(name)).click()


def test_full_review_through_the_web_frontend_with_restart_and_network_guards(tmp_path):
    web_port, api_port = free_port(), free_port()
    base, api_base = f"http://127.0.0.1:{web_port}", f"http://127.0.0.1:{api_port}"
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'acceptance.db'}", secret_key_file=str(tmp_path / "key"),
                        source_storage_root=str(tmp_path / "sources"), embedded_worker=True, auto_migrate=False,
                        trusted_origins=(base,))
    migrate(settings.database_url)
    db = Database(settings.database_url)
    provision_reviewer(db, settings.secret_key_file)
    provision_reviewer(db, settings.secret_key_file, username="outsider")
    with db.session() as session:
        create_local_account(session, "supervisor", PASSWORD, {"supervisor"}, SecretBox.from_file(settings.secret_key_file),
                             totp_secret=SUPERVISOR_TOTP)
    db.engine.dispose()
    config = tmp_path / "settings.json"
    config.write_text(json.dumps(asdict(settings)))
    api_network, web_network, server_log = tmp_path / "api-network.log", tmp_path / "web-network.log", tmp_path / "server.log"

    def start_api():
        log = server_log.open("ab")
        process = subprocess.Popen([sys.executable, "-I", str(Path(__file__).with_name("offline_server.py")), str(config),
                                    str(api_port), str(api_network)], stdout=log, stderr=log)
        log.close()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError(server_log.read_text())
            try:
                if httpx.get(api_base + "/healthz", timeout=0.5).status_code == 200:
                    return process
            except httpx.TransportError:
                time.sleep(0.05)
        process.terminate()
        raise AssertionError("Review service did not start")

    api = start_api()
    web = start_web(api_base, web_port, web_network)
    blocked, errors = [], []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            stack = WebStack(base, api_base, browser, None, settings, web_network)
            reviewer = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
            supervisor, outsider = browser.new_context(), browser.new_context()

            def guard(route):
                if route.request.url.startswith(base + "/"):
                    route.continue_()
                else:
                    blocked.append(route.request.url)
                    route.abort()

            for context in (reviewer, supervisor, outsider):
                context.route("**/*", guard)
            page = reviewer.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            sign_in(page, stack)

            # Import: one entry point, real processing state, then on to review.
            page.get_by_role("link", name="Import a claim").click()
            choose_bundle(page, ROOT)
            page.wait_for_url(re.compile(r".*/claims/[0-9a-f]{32}/import$"))
            case_id = re.search(r"/claims/([0-9a-f]{32})/", page.url).group(1)
            expect(page.get_by_text(re.compile("^Checks complete for version 1"))).to_be_visible(timeout=30000)
            page.get_by_role("link", name="Continue to review").click()
            original_bundle = reviewer.request.get(f"{base}/api/claims/{case_id}/bundles/1").json()
            original_document = original_bundle["documents"][0]["id"]

            # Review: the date discrepancy with its exact sources.
            issue(page, "Dates and discharge status")
            evidence = page.get_by_role("region", name="Source evidence")
            evidence.get_by_role("tab", name=re.compile("Discharge summary")).click()
            expect(evidence.get_by_label("Source text")).to_contain_text("2026-08-18")
            expect(page.get_by_role("table", name="What differs")).to_contain_text("2026-08-17")
            page.evaluate("window.scrollTo(0, 0)")
            snap(page, "discrepancy-evidence-acceptance-1366")

            # Correction: request, handoff and acknowledgement are separate events.
            action = page.get_by_role("region", name="Next action")
            action.get_by_role("button", name="Request correction").click()
            action.get_by_label("Reason", exact=True).fill("Discharge date conflicts with claim; corrected source required")
            action.get_by_label("Responsible department").fill("Records")
            action.get_by_label("Responsible person").fill("Synthetic Clerk")
            action.get_by_role("checkbox", name="Discharge summary").check()
            action.get_by_role("button", name="Save correction request").click()
            progress = page.get_by_role("region", name="Correction progress")
            expect(progress).to_contain_text("Synthetic Clerk")
            progress.get_by_label("Note for this step").fill("Handed over at records desk")
            progress.get_by_role("button", name="Record handoff").click()
            expect(progress.get_by_role("button", name="Record acknowledgement")).to_be_visible()
            progress.get_by_label("Note for this step").fill("Clerk acknowledged receipt locally")
            progress.get_by_role("button", name="Record acknowledgement").click()
            page.evaluate("window.scrollTo(0, 0)")
            snap(page, "correction-progress-acceptance-1366")
            progress.get_by_role("link", name="Import corrected version").click()

            # Corrected version: imported as version 2, then the correction is resolved after recheck.
            page.wait_for_url(f"{base}/claims/{case_id}/import")
            choose_bundle(page.get_by_role("region", name="Import a corrected version"), ROOT / "corrected")
            expect(page.get_by_label("Source version")).to_contain_text("Version 2", timeout=30000)
            expect(page.get_by_text(re.compile("^Checks complete for version 2"))).to_be_visible(timeout=30000)
            phase(page, "Review")
            issue(page, "Dates and discharge status")
            progress = page.get_by_role("region", name="Correction progress")
            progress.get_by_label("Note for this step").fill("Compared corrected discharge against original and rechecked")
            progress.get_by_role("button", name="Resolve after recheck").click()
            expect(page.get_by_label("Review history")).to_contain_text("Correction resolved")

            # Manual reviews by the reviewer.
            issue(page, "Narrative agreement")
            record(page, "Record manual comparison", "Comparison notes", "Compared all current narratives with source evidence",
                   ["CF2 claim summary", "CF4 clinical summary", "CF5 supplementary summary", "Discharge summary"], "Save manual comparison")
            expect(page.get_by_label("Review history")).to_contain_text("manual_p07")
            issue(page, "Signature marks, printed names and dates")
            record(page, "Record presence review", "Presence review notes", "All fictional marks, printed names and dates are present",
                   ["CF2 claim summary", "CF4 clinical summary", "CF5 supplementary summary", "CSF signature form"], "Save presence review")
            expect(page.get_by_label("Review history")).to_contain_text("manual_p08")

            # Completion is guarded until a different supervisor acknowledges the comparison.
            phase(page, "Complete")
            complete = page.get_by_role("button", name="Complete review")
            expect(complete).to_have_attribute("aria-disabled", "true")
            expect(page.get_by_role("list", name="Remaining blockers")).to_contain_text("Narrative agreement")
            second = supervisor.new_page()
            sign_in(second, stack, "supervisor")
            second.goto(f"{base}/claims/{case_id}/review?issue=P07")
            record(second, "Acknowledge comparison", "Acknowledgement note", "Compared and acknowledged the named manual review", [],
                   "Save acknowledgement")
            expect(second.get_by_label("Review history")).to_contain_text("Supervisor acknowledgement")
            page.reload()
            complete = page.get_by_role("button", name="Complete review")
            expect(complete).not_to_have_attribute("aria-disabled", "true")
            complete.click()
            expect(page.get_by_role("region", name="Claim summary")).to_contain_text("Ready for final submission review")

            # Exports of the immutable record.
            with page.expect_download() as download_info:
                page.get_by_role("list", name="Review records").get_by_role("link", name="Download CSV").click()
            exported = Path(download_info.value.path()).read_text(encoding="utf-8-sig")
            assert "Synthetic patient records" in exported and "SAMPLE-ADULT-MEDICAL-1/1" in exported
            with page.expect_popup() as popup_info:
                page.get_by_role("list", name="Review records").get_by_role("link", name="Open printable record").click()
            printable = popup_info.value
            expect(printable.get_by_role("heading", name="Internal review record", exact=True)).to_be_visible()
            printable.close()
            page.evaluate("window.scrollTo(0, 0)")
            snap(page, "completed-record-acceptance-1366")

            # A second reviewer sees nothing of this claim, through the page or the proxy.
            denied = outsider.new_page()
            sign_in(denied, stack, "outsider")
            denied.goto(f"{base}/claims/{case_id}")
            expect(denied.get_by_role("heading", name="Claim not found")).to_be_visible()
            report_id = reviewer.request.get(f"{base}/api/claims/{case_id}/reports").json()["items"][0]["id"]
            assert outsider.request.get(f"{base}/api/claims/{case_id}").status == 404
            assert outsider.request.get(f"{base}/api/documents/{original_document}/content").status == 404
            assert outsider.request.get(f"{base}/api/reports/{report_id}/export?format=csv").status == 404
            assert outsider.request.get(f"{base}/api/claims").json()["total"] == 0
            assert api_network.read_text() == "" and web_network.read_text() == ""

            # Restart the review service: everything persists.
            api.terminate()
            api.wait(timeout=10)
            api = start_api()
            page.reload()
            expect(page.get_by_role("region", name="Claim summary")).to_contain_text("Ready for final submission review")
            assert reviewer.request.get(f"{base}/api/claims/{case_id}/bundles/1").json() == original_bundle
            assert reviewer.request.get(f"{base}/api/documents/{original_document}/content").status == 200
            reports = reviewer.request.get(f"{base}/api/claims/{case_id}/reports").json()["items"]
            assert reports[0]["snapshot"]["model_status"] == "not_run_offline" and not reports[0]["stale"]
            events = reviewer.request.get(f"{base}/api/claims/{case_id}/review-state").json()["events"]
            assert "supervisor_ack" in [event["action"] for event in events]

            # A later re-run reopens review and marks the earlier record stale, still inspectable.
            phase(page, "Review")
            tools = page.get_by_role("region", name="Case tools")
            tools.get_by_text("Re-run checks on version 2").click()
            tools.get_by_label("Re-run reason").fill("Confirm the record against a fresh local run")
            tools.get_by_role("button", name="Re-run checks").click()
            page.wait_for_url(f"{base}/claims/{case_id}/import")
            expect(page.get_by_text(re.compile("^Checks complete for version 2"))).to_be_visible(timeout=30000)
            phase(page, "Complete")
            records = page.get_by_role("list", name="Review records")
            expect(records).to_contain_text("Stale after later changes")
            records.get_by_text("Inspect this record").click()
            expect(records).to_contain_text("Completed by reviewer")
            expect(page.get_by_role("button", name="Complete review")).to_have_attribute("aria-disabled", "true")

            for width in (375,):
                page.set_viewport_size({"width": width, "height": 812})
                page.goto(f"{base}/claims")
                snap(page, f"queue-{width}")
                page.goto(f"{base}/claims/{case_id}/complete")
                snap(page, f"completed-record-{width}")
            assert api_network.read_text() == "" and web_network.read_text() == ""
            assert not blocked and not errors, (blocked, errors)
            browser.close()
    finally:
        stop_web(web)
        api.terminate()
        api.wait(timeout=10)

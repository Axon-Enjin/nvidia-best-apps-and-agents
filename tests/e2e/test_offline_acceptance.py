import json
import socket
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

from e2e.account_setup import PASSWORD, provision_reviewer
from e2e.fixture_paths import FIXTURES
from sentinel.accounts import SecretBox, create_local_account, totp_code
from sentinel.config import Settings, migrate
from sentinel.db import Database

ROOT = FIXTURES/"evaluation"/"heldout-01"
TOTP = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


def signin(page,base,username="reviewer"):
    page.goto(base+"/login")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(PASSWORD)
    if username == "supervisor":
        page.get_by_label("Authenticator code").fill(totp_code(TOTP,time.time()))
    page.get_by_role("button",name="Sign in",exact=True).click()
    page.wait_for_url(base+"/")


def import_ui(page,path,replacement=False):
    page.get_by_role("button",name="Import corrected version" if replacement else "Import bundle",exact=True).click()
    page.get_by_label("Bundle manifest").set_input_files(str(path/"manifest.json"))
    manifest = json.loads((path/"manifest.json").read_text())
    page.get_by_label("Original documents").set_input_files([str(path/d["filename"]) for d in manifest["documents"]])
    page.get_by_role("button",name="Import and check").click()
    page.get_by_role("button",name="P05 Dates and disposition").wait_for(timeout=25000)


def manual_ui(page,check,action,reason):
    page.get_by_role("button",name=check,exact=True).click()
    page.get_by_label("Review action").select_option(action)
    page.get_by_label("Review reason").fill(reason)
    if action.startswith("manual_"):
        for kind in ("cf2","cf4","cf5","discharge","csf","esoa","eligibility"):
            page.get_by_label(f"Evidence {kind} page 1",exact=True).check()
    page.get_by_role("button",name="Save review action").click()


def test_local_correction_manual_supervision_exports_and_process_restart_with_network_guards(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path/'acceptance.db'}",secret_key_file=str(tmp_path/'key'),
                        source_storage_root=str(tmp_path/'sources'),embedded_worker=True,auto_migrate=False)
    migrate(settings.database_url)
    db = Database(settings.database_url)
    provision_reviewer(db,settings.secret_key_file)
    provision_reviewer(db,settings.secret_key_file,username="outsider")
    with db.session() as session:
        create_local_account(session,"supervisor",PASSWORD,{"supervisor"},SecretBox.from_file(settings.secret_key_file),totp_secret=TOTP)
    db.engine.dispose()
    config = tmp_path/"settings.json"
    config.write_text(json.dumps(asdict(settings)))
    network_log,server_log = tmp_path/"network.log",tmp_path/"server.log"
    with socket.socket() as listener:
        listener.bind(("127.0.0.1",0))
        port = listener.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    def start():
        log = server_log.open("ab")
        process = subprocess.Popen([sys.executable,"-I",str(Path(__file__).with_name("offline_server.py")),str(config),str(port),str(network_log)],stdout=log,stderr=log)
        log.close()
        deadline = time.monotonic()+15
        while time.monotonic()<deadline:
            if process.poll() is not None:
                raise AssertionError(server_log.read_text())
            try:
                if httpx.get(base+"/healthz",timeout=.5).status_code == 200:
                    return process
            except httpx.TransportError:
                time.sleep(.05)
        process.terminate()
        raise AssertionError("Local server did not start")
    process = start()
    blocked,errors = [],[]
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            reviewer = browser.new_context(viewport={"width":1366,"height":768})
            supervisor = browser.new_context()
            outsider = browser.new_context()
            def route(request_route):
                if not request_route.request.url.startswith(base+"/"):
                    blocked.append(request_route.request.url)
                    request_route.abort()
                else:
                    request_route.continue_()
            for context in (reviewer,supervisor,outsider):
                context.route("**/*",route)
            page = reviewer.new_page()
            page.on("pageerror",lambda e:errors.append(str(e)))
            signin(page,base)
            import_ui(page,ROOT)
            case_id = page.url.split("case=")[1]
            raw = reviewer.request.get(base+f"/api/claims/{case_id}/bundles/1").json()
            original_document = raw["documents"][0]["id"]
            page.get_by_role("button",name="P05 Dates and disposition").click()
            page.get_by_role("button",name="View discharge page 1").click()
            expect(page.get_by_label("Source text")).to_contain_text("2026-08-18")
            page.get_by_label("Review reason").fill("Discharge date conflicts with claim; corrected source required")
            page.get_by_label("Responsible department").fill("Records")
            page.get_by_label("Responsible person").fill("Synthetic Clerk")
            page.get_by_label("Evidence discharge page 1",exact=True).check()
            page.get_by_role("button",name="Save review action").click()
            expect(page.get_by_label("Correction tasks")).to_contain_text("Synthetic Clerk")
            page.get_by_label("Correction reason").fill("Handed over at records desk")
            page.get_by_role("button",name="Record handoff").click()
            expect(page.get_by_label("Correction tasks")).to_contain_text("handed_off")
            page.get_by_label("Correction reason").fill("Clerk acknowledged receipt locally")
            page.get_by_role("button",name="Record acknowledgement").click()
            expect(page.get_by_label("Correction tasks")).to_contain_text("acknowledged")
            import_ui(page,ROOT/"corrected",replacement=True)
            expect(page.get_by_label("Source version")).to_contain_text("Version 2")
            page.get_by_label("Correction reason").fill("Compared corrected discharge against original and rechecked")
            page.get_by_role("button",name="Resolve after recheck").click()
            expect(page.get_by_label("Correction tasks")).to_contain_text("resolved")
            manual_ui(page,"P07 Narrative agreement","manual_p07","Compared all current narratives with source evidence")
            expect(page.get_by_label("Review history")).to_contain_text("manual_p07")
            manual_ui(page,"P08 Marks, printed signatory and date","manual_p08","All fictional marks, printed names and dates are present")
            expect(page.get_by_role("button",name="Complete current review")).to_be_disabled()
            second = supervisor.new_page()
            signin(second,base,"supervisor")
            second.goto(base+f"/#case={case_id}")
            second.get_by_role("button",name="P07 Narrative agreement").wait_for()
            manual_ui(second,"P07 Narrative agreement","supervisor_ack","Compared and acknowledged the named manual review")
            expect(second.get_by_label("Review history")).to_contain_text("supervisor_ack")
            page.reload()
            expect(page.get_by_role("button",name="Complete current review")).to_be_enabled()
            page.get_by_role("button",name="Complete current review").click()
            expect(page.get_by_label("Selected claim")).to_contain_text("Ready for final submission review")
            with page.expect_download() as download_info:
                page.get_by_role("link",name="Download CSV").click()
            download = download_info.value
            exported = Path(download.path()).read_text(encoding="utf-8-sig")
            assert "Synthetic patient records" in exported and "SAMPLE-ADULT-MEDICAL-1/1" in exported
            with page.expect_popup() as popup_info:
                page.get_by_role("link",name="Open printable record").click()
            printable = popup_info.value
            expect(printable.get_by_role("heading",name="Internal review record",exact=True)).to_be_visible()
            printable.close()
            denied = outsider.new_page()
            signin(denied,base,"outsider")
            assert outsider.request.get(base+f"/api/claims/{case_id}").status == 404
            assert outsider.request.get(base+f"/api/documents/{original_document}/content").status == 404
            assert outsider.request.get(base+"/api/claims").json()["total"] == 0
            saved_reports = reviewer.request.get(base+f"/api/claims/{case_id}/reports").json()["items"]
            assert outsider.request.get(base+f"/api/reports/{saved_reports[0]['id']}/export?format=csv").status == 404
            assert network_log.read_text() == ""
            process.terminate()
            process.wait(timeout=10)
            process = start()
            page.reload()
            expect(page.get_by_label("Selected claim")).to_contain_text("Ready for final submission review")
            expect(page.get_by_label("Review history")).to_contain_text("supervisor_ack")
            assert reviewer.request.get(base+f"/api/claims/{case_id}/bundles/1").json() == raw
            assert reviewer.request.get(base+f"/api/documents/{original_document}/content").status == 200
            reports = reviewer.request.get(base+f"/api/claims/{case_id}/reports").json()["items"]
            assert reports[0]["snapshot"]["model_status"] == "not_run_offline"
            assert not reports[0]["stale"]
            result_dir=Path("test-results")
            result_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(result_dir/"offline-acceptance.png"),full_page=True)
            assert network_log.read_text() == "" and not blocked and not errors
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)

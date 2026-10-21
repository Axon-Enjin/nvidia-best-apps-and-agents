import socket
import threading
import time

import uvicorn
from playwright.sync_api import sync_playwright

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database
from tests.account_helpers import PASSWORD, provision_reviewer


def test_local_login_is_responsive_and_creates_a_named_session(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'browser.db'}", embedded_worker=False,
                        auto_migrate=False, secret_key_file=str(tmp_path / "browser.key"))
    db = Database(settings.database_url)
    db.initialize()
    provision_reviewer(db, settings.secret_key_file)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(settings, db), log_level="error"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(.02)
        assert server.started
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for viewport in [{"width": 1366, "height": 768}, {"width": 375, "height": 812}]:
                context = browser.new_context(viewport=viewport)
                page = context.new_page()
                external = []
                page.on("request", lambda request, external=external: external.append(request.url) if not request.url.startswith(f"http://127.0.0.1:{port}/") else None)
                page.goto(f"http://127.0.0.1:{port}/")
                assert page.url.endswith("/login")
                page.get_by_label("Username").fill("reviewer")
                page.get_by_label("Password").fill("incorrect")
                page.get_by_role("button", name="Sign in", exact=True).click()
                page.get_by_role("alert").wait_for(state="visible")
                assert page.get_by_label("Password").input_value() == "incorrect"
                assert page.locator("#login-error").evaluate("element => document.activeElement === element")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.get_by_label("Password").fill(PASSWORD)
                page.get_by_role("button", name="Sign in", exact=True).click()
                page.wait_for_url(f"http://127.0.0.1:{port}/")
                assert page.request.get(f"http://127.0.0.1:{port}/api/session").json()["actor"]["username"] == "reviewer"
                assert external == []
                context.close()
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()
        db.engine.dispose()

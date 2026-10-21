import socket
import threading
import time

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database
from tests.account_helpers import provision_reviewer


@pytest.fixture
def live_workspace(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'browser.db'}", embedded_worker=True,
                        auto_migrate=False, secret_key_file=str(tmp_path / 'key'),
                        source_storage_root=str(tmp_path / 'sources'))
    db = Database(settings.database_url)
    db.initialize()
    provision_reviewer(db, settings.secret_key_file)
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    base = f"http://127.0.0.1:{listener.getsockname()[1]}"
    server = uvicorn.Server(uvicorn.Config(create_app(settings, db), log_level='error'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(.02)
        assert server.started
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            yield base, browser, db, settings
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()
        db.engine.dispose()

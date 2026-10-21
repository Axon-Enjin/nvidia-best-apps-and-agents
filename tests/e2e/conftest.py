import socket
import threading
import time
from contextlib import contextmanager

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from e2e.account_setup import PASSWORD, provision_reviewer
from e2e.web_helpers import SUPERVISOR_TOTP, WebStack
from e2e.web_server import free_port, start_web, stop_web
from sentinel.accounts import SecretBox, create_local_account
from sentinel.api import create_app
from sentinel.config import Settings
from sentinel.db import Database


@contextmanager
def api_server(settings, db):
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
        yield base
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()


def provision_web_accounts(db, key_file):
    provision_reviewer(db, key_file)
    provision_reviewer(db, key_file, username='outsider')
    with db.session() as session:
        box = SecretBox.from_file(key_file)
        create_local_account(session, 'supervisor', PASSWORD, {'supervisor'}, box, totp_secret=SUPERVISOR_TOTP)
    with db.session() as session:
        create_local_account(session, 'admin', PASSWORD, {'admin'}, SecretBox.from_file(key_file), totp_secret=SUPERVISOR_TOTP)


@pytest.fixture
def web_stack(tmp_path):
    """FastAPI on one loopback port, the built Next.js app on another, and a browser."""
    port = free_port()
    web_base = f"http://127.0.0.1:{port}"
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'web.db'}", embedded_worker=True,
                        auto_migrate=False, secret_key_file=str(tmp_path / 'key'),
                        source_storage_root=str(tmp_path / 'sources'), trusted_origins=(web_base,))
    db = Database(settings.database_url)
    db.initialize()
    provision_web_accounts(db, settings.secret_key_file)
    network_log = tmp_path / 'web-network.log'
    with api_server(settings, db) as api_base:
        web = start_web(api_base, port, network_log)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                yield WebStack(web_base, api_base, browser, db, settings, network_log)
                browser.close()
        finally:
            stop_web(web)
    db.engine.dispose()


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

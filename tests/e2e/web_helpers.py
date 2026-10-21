"""Shared helpers for browser tests of the Next.js frontend."""
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from e2e.account_setup import PASSWORD
from sentinel.accounts import totp_code

SUPERVISOR_TOTP = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
PRIVILEGED = {"supervisor", "admin"}


@dataclass
class WebStack:
    base: str
    api_base: str
    browser: object
    db: object
    settings: object
    network_log: Path


_last_step: dict[tuple[str, str], int] = {}


def otp_for(stack: WebStack, username: str) -> str:
    """A fresh code per sign-in. The server refuses a reused time step but accepts the next one."""
    if username not in PRIVILEGED:
        return ""
    key = (stack.api_base, username)
    while True:
        now = int(time.time()) // 30
        step = max(now, _last_step.get(key, -1) + 1)
        if step <= now + 1:
            _last_step[key] = step
            return totp_code(SUPERVISOR_TOTP, step * 30)
        time.sleep(1)


def api_client(stack: WebStack, username: str = "reviewer") -> httpx.Client:
    """An HTTP client signed in through the web origin, as the browser would be."""
    client = httpx.Client(base_url=stack.base, headers={"Origin": stack.base}, timeout=30)
    response = client.post("/api/session", json={"username": username, "password": PASSWORD,
                                                 "otp": otp_for(stack, username)})
    assert response.status_code == 200, response.text
    client.headers["x-csrf-token"] = response.json()["csrf_token"]
    return client

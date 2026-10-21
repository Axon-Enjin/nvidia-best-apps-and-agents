"""Start the built Next.js frontend for browser tests, guarded to loopback-only networking."""
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import httpx

WEB_ROOT = Path(__file__).resolve().parents[2] / "apps" / "web"
GUARD = Path(__file__).with_name("web_network_guard.cjs")


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def start_web(api_base: str, port: int, network_log: Path, log_path: Path | None = None) -> subprocess.Popen:
    if not (WEB_ROOT / ".next" / "BUILD_ID").is_file():
        raise RuntimeError("Build the web app first: pnpm --dir apps/web build")
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for the web frontend tests.")
    env = {**os.environ, "BACKEND_URL": api_base, "NEXT_TELEMETRY_DISABLED": "1",
           "NODE_OPTIONS": f"--require {GUARD.as_posix()}", "SENTINEL_NETWORK_LOG": str(network_log),
           "NODE_ENV": "production"}
    log = (log_path or network_log.with_name(f"web-{port}.log")).open("ab")
    process = subprocess.Popen([node, str(WEB_ROOT / "node_modules" / "next" / "dist" / "bin" / "next"),
                                "start", "-H", "127.0.0.1", "-p", str(port)],
                               cwd=WEB_ROOT, env=env, stdout=log, stderr=log)
    log.close()
    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Web server exited with {process.returncode}")
        try:
            httpx.get(base + "/api/session", timeout=1)
            return process
        except httpx.TransportError:
            time.sleep(0.1)
    process.terminate()
    raise RuntimeError("Web server did not start within 30 seconds")


def stop_web(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()

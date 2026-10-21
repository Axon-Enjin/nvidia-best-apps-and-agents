"""Real test server with a socket audit boundary independent of NETWORK_MODE."""
import ipaddress
import json
import socket
import sys
from pathlib import Path


def install_guard(log_path):
    state = {"probe":True}
    def allowed(host):
        if host == "localhost":
            return True
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False

    def audit(event,args):
        host = args[1][0] if event == "socket.connect" and isinstance(args[1],tuple) else args[0] if event == "socket.getaddrinfo" else None
        if host is not None and not allowed(host):
            if not state["probe"]:
                with log_path.open("a") as handle:
                    handle.write(event+" "+str(host)+"\n")
            raise PermissionError("Acceptance server permits loopback only.")
    sys.addaudithook(audit)
    return state


if __name__ == "__main__":
    log_path = Path(sys.argv[3])
    guard = install_guard(log_path)
    try:
        socket.create_connection(("198.51.100.1",443),timeout=.5)
        raise RuntimeError("Network acceptance guard failed its startup probe.")
    except PermissionError:
        guard["probe"] = False
        log_path.touch(exist_ok=True)  # Preserve any application traffic recorded before a restart.
    import uvicorn

    from sentinel.api import create_app
    from sentinel.config import Settings
    settings = Settings(**json.loads(Path(sys.argv[1]).read_text()))
    uvicorn.run(create_app(settings),host="127.0.0.1",port=int(sys.argv[2]),log_level="error")

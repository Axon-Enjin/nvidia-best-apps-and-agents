import os
import sys

import uvicorn

from sentinel.config import Settings, migrate


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "serve"
    settings = Settings.from_env()
    if action == "migrate":
        migrate(settings.database_url)
    elif action == "worker":
        from sentinel.worker import main as worker_main
        worker_main()
    elif action == "serve":
        uvicorn.run("sentinel.api:app_factory", factory=True, host=os.getenv("HOST", "127.0.0.1"),
                    port=int(os.getenv("PORT", "8000")), limit_concurrency=32)
    else:
        raise SystemExit("Usage: python -m sentinel [serve|worker|migrate]")


if __name__ == "__main__":
    main()

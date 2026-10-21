import argparse
import base64
import getpass
import os
import secrets
import time

import uvicorn

from sentinel.config import Settings, migrate


def account_command(args, settings):
    from sqlalchemy import select, update

    from sentinel.accounts import (
        PASSWORDS,
        PRIVILEGED_ROLES,
        SecretBox,
        create_local_account,
        normalized_username,
        totp_code,
    )
    from sentinel.db import AccessEvent, Account, Database, LocalSession

    migrate(settings.database_url)
    db = Database(settings.database_url)
    try:
        username = normalized_username(args.username)
        with db.session() as session:
            account = session.scalar(select(Account).where(Account.username == username))
            if args.action == "account-create" and account:
                raise ValueError("That username already exists.")
            if args.action != "account-create" and not account:
                raise ValueError("Account not found.")
            roles = set(args.roles.split(",")) if args.action == "account-create" else set(account.roles)
            if args.action in {"account-create", "account-reset"}:
                password = getpass.getpass("Password (15-128 characters): ")
                if password != getpass.getpass("Confirm password: "):
                    raise ValueError("Passwords did not match.")
                if not 15 <= len(password) <= 128:
                    raise ValueError("Password must contain 15-128 characters.")
                box = SecretBox.from_file(settings.secret_key_file, create=args.action == "account-create")
                secret = None
                if roles & PRIVILEGED_ROLES or (account and account.totp_encrypted):
                    secret = base64.b32encode(secrets.token_bytes(20)).decode()
                    print("Enroll this secret in your local authenticator. Keep it private:")
                    print(secret)
                    code = getpass.getpass("Authenticator code: ")
                    if code != totp_code(secret, time.time()):
                        raise ValueError("Authenticator code did not match; no account change saved.")
                if args.action == "account-create":
                    create_local_account(session, username, password, roles, box, totp_secret=secret)
                else:
                    account.password_hash = PASSWORDS.hash(password)
                    account.totp_encrypted = box.encrypt(secret) if secret else None
                    account.totp_last_step = -1
            elif args.action == "account-disable":
                account.enabled = False
            elif args.action == "account-enable":
                account.enabled = True
            if account:
                # Password resets, enabling, disabling and explicit revocation invalidate ALL sessions.
                session.execute(update(LocalSession).where(LocalSession.account_id == account.id).values(revoked=True))
                session.add(AccessEvent(actor_id=None, action=args.action.replace("-", "_"), resource_id=account.id,
                                        detail={"channel": "local_cli"}))
                session.commit()
            print(f"{args.action}: {username}")
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from exc
    finally:
        db.engine.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sentinel Claims local workspace")
    commands = parser.add_subparsers(dest="action")
    for command in ("serve", "worker", "migrate"):
        commands.add_parser(command)
    for command in ("account-create", "account-disable", "account-enable", "account-reset", "account-revoke"):
        child = commands.add_parser(command)
        child.add_argument("username")
        if command == "account-create":
            child.add_argument("--roles", required=True, help="Comma-separated reviewer,supervisor,admin")
    args = parser.parse_args(argv)
    action = args.action or "serve"
    settings = Settings.from_env()
    if action.startswith("account-"):
        account_command(args, settings)
    elif action == "migrate":
        migrate(settings.database_url)
    elif action == "worker":
        from sentinel.worker import main as worker_main
        worker_main()
    elif action == "serve":
        uvicorn.run("sentinel.api:app_factory", factory=True, host=os.getenv("HOST", "127.0.0.1"),
                    port=int(os.getenv("PORT", "8000")), limit_concurrency=32)


if __name__ == "__main__":
    main()

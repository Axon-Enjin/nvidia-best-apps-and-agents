"""Local identities, revocable sessions and case authorization.

Passwords use argon2-cffi's Argon2id defaults. MFA follows RFC 6238 using
stdlib HMAC; its recoverable secrets are encrypted with Fernet outside the DB.
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
import struct
import time
from dataclasses import dataclass
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from sentinel.db import AccessEvent, Account, LocalSession, LoginThrottle

PASSWORDS = PasswordHasher()
# Unknown accounts incur the same password verification cost.
DUMMY_HASH = PASSWORDS.hash(secrets.token_urlsafe(32))
CLINICAL_ROLES = frozenset({"reviewer", "supervisor"})
PRIVILEGED_ROLES = frozenset({"supervisor", "admin"})
COOKIE_NAME = "sentinel_session"


@dataclass(frozen=True)
class Actor:
    id: str | None
    username: str
    roles: frozenset[str]
    enabled: bool

    def public(self):
        return {"id": self.id, "username": self.username, "roles": sorted(self.roles)}


class SecretBox:
    def __init__(self, key):
        self.fernet = Fernet(key)

    @classmethod
    def from_file(cls, filename, *, create=False):
        path = Path(filename)
        if create:
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass
            else:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(Fernet.generate_key())
        return cls(path.read_bytes().strip())

    def encrypt(self, value):
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value):
        return self.fernet.decrypt(value.encode()).decode()


def normalized_username(username):
    username = username.strip().casefold()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,79}", username):
        raise ValueError("Use 3-80 letters, digits, periods, underscores or hyphens for the username.")
    return username


def create_local_account(session, username, password, roles, secret_box, *, totp_secret=None):
    username = normalized_username(username)
    roles = frozenset(roles)
    if not roles or not roles <= {"reviewer", "supervisor", "admin"}:
        raise ValueError("Choose reviewer, supervisor and/or admin roles.")
    if not 15 <= len(password) <= 128:
        raise ValueError("Password must contain 15-128 characters.")
    if session.scalar(select(Account.id).where(Account.username == username)):
        raise ValueError("That username already exists.")
    if roles & PRIVILEGED_ROLES and not totp_secret:
        raise ValueError("Supervisor/admin accounts require local TOTP enrollment.")
    if totp_secret:
        totp_code(totp_secret, time.time())  # validate before persisting
    account = Account(username=username, password_hash=PASSWORDS.hash(password), roles=sorted(roles),
                      totp_encrypted=secret_box.encrypt(totp_secret) if totp_secret else None)
    session.add(account)
    session.flush()
    session.add(AccessEvent(actor_id=account.id, action="account_provisioned", resource_id=account.id,
                            detail={"roles": sorted(roles), "channel": "local_cli"}))
    session.commit()
    return account.id


def totp_code(secret, timestamp, *, digits=6):
    """RFC 6238, 30-second SHA-1 TOTP, including RFC dynamic truncation."""
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    if len(key) < 20:
        raise ValueError("TOTP secret must contain at least 160 bits.")
    digest = hmac.new(key, struct.pack(">Q", int(timestamp) // 30), hashlib.sha1).digest()
    offset = digest[-1] & 15
    number = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff
    return str(number % (10 ** digits)).zfill(digits)


def token_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def csrf_token(token):
    return hmac.new(token.encode(), b"sentinel-csrf-v1", hashlib.sha256).hexdigest()


def reserve_attempt(session, username, address, now):
    """Persistently bound guesses across processes, including unknown usernames."""
    for scope, value, limit in [("user", username, 5), ("address", address, 30)]:
        key = token_digest(f"{scope}:{value}")
        if not session.get(LoginThrottle, key):
            try:
                with session.begin_nested():
                    session.add(LoginThrottle(key=key, window_start=now, attempts=0))
                    session.flush()
            except IntegrityError:
                pass
        session.execute(update(LoginThrottle).where(LoginThrottle.key == key,
                        LoginThrottle.window_start <= now - 300).values(window_start=now, attempts=0))
        changed = session.execute(update(LoginThrottle).where(LoginThrottle.key == key,
                                  LoginThrottle.attempts < limit).values(attempts=LoginThrottle.attempts + 1))
        if changed.rowcount != 1:
            session.commit()
            raise HTTPException(429, "Too many sign-in attempts. Try again later.", headers={"Retry-After": "300"})
    session.commit()


def authenticate(db, settings, username, password, otp, address, previous_token=""):
    username = username.strip().casefold()
    now = time.time()
    with db.session() as session:
        reserve_attempt(session, username, address, now)
        account = session.scalar(select(Account).where(Account.username == username))
        try:
            valid = PASSWORDS.verify(account.password_hash if account else DUMMY_HASH, password)
        except (VerificationError, InvalidHashError):
            valid = False
        if not valid or not account or not account.enabled:
            raise HTTPException(401, "Sign-in failed.")
        if frozenset(account.roles) & PRIVILEGED_ROLES or account.totp_encrypted:
            matched_step = None
            try:
                secret = SecretBox.from_file(settings.secret_key_file).decrypt(account.totp_encrypted)
                if re.fullmatch(r"[0-9]{6}", otp):
                    for offset in (-1, 0, 1):
                        step = int(now) // 30 + offset
                        if step > account.totp_last_step and hmac.compare_digest(totp_code(secret, step * 30), otp):
                            matched_step = step
                            break
            except (OSError, ValueError, InvalidToken, TypeError) as exc:
                raise HTTPException(503, "Local authentication key is unavailable. Contact the operator.") from exc
            if matched_step is None:
                raise HTTPException(401, "Sign-in failed.")
            changed = session.execute(update(Account).where(Account.id == account.id, Account.enabled.is_(True),
                                      Account.totp_last_step < matched_step).values(totp_last_step=matched_step))
            if changed.rowcount != 1:
                raise HTTPException(401, "Sign-in failed.")
        if PASSWORDS.check_needs_rehash(account.password_hash):
            account.password_hash = PASSWORDS.hash(password)
        if previous_token:
            session.execute(update(LocalSession).where(LocalSession.token_digest == token_digest(previous_token))
                            .values(revoked=True))
        raw = secrets.token_urlsafe(32)
        session.add(LocalSession(token_digest=token_digest(raw), account_id=account.id,
                                  expires_at=now + settings.session_hours * 3600, last_seen_at=now))
        session.execute(update(LoginThrottle).where(LoginThrottle.key == token_digest(f"user:{username}")).values(attempts=0))
        session.add(AccessEvent(actor_id=account.id, action="sign_in", resource_id=account.id))
        session.commit()
        return Actor(account.id, account.username, frozenset(account.roles), True), raw


def resolve_actor(db, settings, raw):
    if not raw or len(raw) > 128:
        return None
    now = time.time()
    with db.session() as session:
        row = session.get(LocalSession, token_digest(raw))
        if not row or row.revoked or row.expires_at <= now or row.last_seen_at <= now - settings.session_idle_minutes * 60:
            return None
        account = session.get(Account, row.account_id)
        if not account or not account.enabled:
            return None
        row.last_seen_at = now
        session.commit()
        return Actor(account.id, account.username, frozenset(account.roles), True)


def revoke_session(db, raw):
    with db.session() as session:
        session.execute(update(LocalSession).where(LocalSession.token_digest == token_digest(raw)).values(revoked=True))
        session.commit()


def require_actor(request: Request) -> Actor:
    actor = getattr(request.state, "actor", None)
    if not actor or not actor.enabled:
        raise HTTPException(401, "Sign in to continue.")
    return actor


def require_clinical(actor):
    if not actor.enabled or not actor.roles & CLINICAL_ROLES:
        raise HTTPException(403, "A reviewer or supervisor role is required.")


def require_case_access(actor, case):
    require_clinical(actor)
    if not case or (actor.id is not None and "supervisor" not in actor.roles and case.assignee_id != actor.id):
        raise HTTPException(404, "Claim not found.")


def visible_claims(actor, claim_type):
    require_clinical(actor)
    return True if "supervisor" in actor.roles else claim_type.assignee_id == actor.id

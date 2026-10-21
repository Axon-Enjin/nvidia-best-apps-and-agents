"""Write-once encrypted source objects, addressed only by opaque server IDs."""
import hashlib
import json
import os
import re
import time
from pathlib import Path

from cryptography.fernet import InvalidToken
from fastapi import HTTPException

from sentinel.accounts import SecretBox
from sentinel.db import new_id


class PrivateStorage:
    def __init__(self, settings):
        self.root = Path(settings.source_storage_root).resolve()
        self.box = SecretBox.from_file(settings.secret_key_file)

    def path(self, key):
        if not re.fullmatch(r"[a-f0-9]{32}", key):
            raise ValueError("Invalid private object key.")
        candidate = self.root / (key + ".source")
        if candidate.resolve().parent != self.root:
            raise ValueError("Private object path escaped storage.")
        return candidate

    def put(self, content, case_id):
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        key = new_id()
        path = self.path(key)
        # Persist a staging receipt before the bytes: a crash leaves a known
        # quarantine object for reconciliation, never an unrecorded guessed path.
        receipt = self.root / (key + ".staging.json")
        with os.fdopen(os.open(receipt, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "w") as handle:
            json.dump({"object_key": key, "case_id": case_id, "sha256": hashlib.sha256(content).hexdigest(),
                       "created_at": time.time()}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags, 0o600), "wb") as handle:
            handle.write(self.box.fernet.encrypt(content))
            handle.flush()
            os.fsync(handle.fileno())
        return key

    def read(self, key, expected_hash):
        try:
            encrypted = self.path(key).read_bytes()
            content = self.box.fernet.decrypt(encrypted)
        except (OSError, ValueError, InvalidToken) as exc:
            raise HTTPException(409, "Original source is missing or damaged; operator recovery is required.") from exc
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise HTTPException(409, "Original source failed integrity verification; operator recovery is required.")
        return content

"""Encrypted coordinated checkpoints and isolated restore. Stop web/worker before operator commands."""
import argparse
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
import time
import zipfile
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from sqlalchemy import inspect, select, update
from sqlalchemy.engine import make_url

from sentinel.accounts import SecretBox
from sentinel.config import Settings
from sentinel.db import Claim, Database, Document, Job, LocalSession, ReviewEvent
from sentinel.storage import PrivateStorage

MAX_BACKUP_BYTES = 512*1024*1024


def verify_workspace(db,settings):
    missing,verified = [],0
    storage = PrivateStorage(settings)
    with db.session() as session:
        docs = session.scalars(select(Document)).all()
        known = {d.object_key for d in docs}
        for d in docs:
            try:
                storage.read(d.object_key,d.source_hash)
                verified += 1
            except Exception:
                missing.append(d.id)
        orphan = [p.name.removesuffix(".staging.json") for p in storage.root.glob("*.staging.json") if p.name.removesuffix(".staging.json") not in known]
        pending = session.scalars(select(Job.id).where(Job.status.in_(["queued","running"]))).all()
        return {"ok":not missing,"verified_sources":verified,"missing_or_damaged":missing,
                "orphan_staging":orphan,"pending_jobs":pending,"history_events":len(session.scalars(select(ReviewEvent.id)).all())}


def postgres_env(url):
    parsed = make_url(url)
    return {**os.environ,"PGHOST":parsed.host or "localhost","PGPORT":str(parsed.port or 5432),
            "PGUSER":parsed.username or "","PGPASSWORD":parsed.password or "","PGDATABASE":parsed.database or ""}


def create_backup(db,settings,target,backup_key_file):
    target = Path(target)
    if target.exists():
        raise ValueError("Backup target already exists; choose a new recovery point.")
    integrity = verify_workspace(db,settings)
    if not integrity["ok"]:
        raise ValueError("Missing/damaged sources prevent a valid coordinated backup.")
    box = SecretBox.from_file(backup_key_file)
    with tempfile.TemporaryDirectory(prefix="sentinel-backup-") as work:
        path = Path(work)/"database"
        engine = "sqlite" if db.engine.dialect.name == "sqlite" else "postgresql"
        if engine == "sqlite":
            with db.engine.connect() as connection, closing(sqlite3.connect(path)) as destination:
                connection.connection.driver_connection.backup(destination)
        else:
            subprocess.run(["pg_dump","--format=custom","--no-owner","--no-acl",f"--file={path}"],
                           env=postgres_env(settings.database_url),check=True,timeout=300,capture_output=True)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as archive:
            archive.write(path,"database")
            archive.write(settings.secret_key_file,"account.key")
            root = Path(settings.source_storage_root).resolve()
            total = path.stat().st_size
            for item in root.rglob("*"):
                if item.is_symlink():
                    raise ValueError("Source backup refuses symlinks.")
                if item.is_file():
                    total += item.stat().st_size
                    if total > MAX_BACKUP_BYTES:
                        raise ValueError("Prototype checkpoint exceeds 512 MB; use a coordinated volume backup.")
                    archive.write(item,"sources/"+item.relative_to(root).as_posix())
            archive.writestr("manifest.json",json.dumps({"format":1,"engine":engine,"created_at":time.time(),"integrity":integrity}))
        encrypted = box.fernet.encrypt(buffer.getvalue())
        target.parent.mkdir(parents=True,exist_ok=True)
        with os.fdopen(os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as output:
            output.write(encrypted)
    return integrity


def retire_case(db,settings,case_id,reason):
    if not re.fullmatch(r"[a-f0-9]{32}",case_id) or not reason.strip():
        raise ValueError("Choose an existing case and retirement reason.")
    with db.session() as session:
        case = session.get(Claim,case_id)
        if not case:
            raise ValueError("Case not found.")
        timestamp = time.time()
        ledger = Path(settings.source_storage_root)/"deletions"
        ledger.mkdir(mode=0o700,parents=True,exist_ok=True)
        payload = json.dumps({"case_id":case_id,"deleted_at":timestamp,"reason":reason}).encode()
        # Tombstone is durable before DB state. A crash is reconciled at restore/verification.
        with (ledger/(case_id+".enc")).open("xb") as output:
            output.write(SecretBox.from_file(settings.secret_key_file).fernet.encrypt(payload))
            output.flush()
            os.fsync(output.fileno())
        case.deleted_at = timestamp
        case.revision += 1
        session.commit()


def apply_deletion_ledger(db,settings,ledger):
    if not Path(ledger).is_dir():
        raise ValueError("Retirement ledger directory is unavailable; do not reopen this restore.")
    box = SecretBox.from_file(settings.secret_key_file)
    with db.session() as session:
        for path in Path(ledger).glob("*.enc"):
            entry = json.loads(box.fernet.decrypt(path.read_bytes()))
            if not re.fullmatch(r"[a-f0-9]{32}",entry["case_id"]) or path.stem != entry["case_id"]:
                raise ValueError("Invalid authenticated retirement ledger.")
            session.execute(update(Claim).where(Claim.id == entry["case_id"]).values(deleted_at=entry["deleted_at"]))
        session.commit()


def restore_backup(backup,target,backup_key_file,*,deletion_ledger=None,database_url=None):
    if deletion_ledger is not None and not Path(deletion_ledger).is_dir():
        raise ValueError("Retirement ledger directory is unavailable; restore was not started.")
    target = Path(target).resolve()
    if target.exists():
        raise ValueError("Restore requires a new isolated directory. Existing data is never overwritten.")
    encrypted = Path(backup).read_bytes()
    if len(encrypted) > MAX_BACKUP_BYTES*2:
        raise ValueError("Backup exceeds prototype restore bound.")
    payload = SecretBox.from_file(backup_key_file).fernet.decrypt(encrypted)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if sum(i.file_size for i in archive.infolist()) > MAX_BACKUP_BYTES:
            raise ValueError("Backup extraction exceeds bound.")
        for item in archive.infolist():
            candidate = (target/item.filename).resolve()
            if target not in candidate.parents or item.is_dir() or (item.external_attr>>16)&0o170000 == 0o120000:
                raise ValueError("Unsafe backup membership.")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest["engine"] == "postgresql" and not database_url:
            raise ValueError("PostgreSQL restore needs an empty isolated database URL.")
        if database_url:
            check = Database(database_url)
            try:
                if inspect(check.engine).get_table_names():
                    raise ValueError("Restore database must be empty; no tables are dropped.")
            finally:
                check.engine.dispose()
        target.mkdir(mode=0o700,parents=True)
        for item in archive.infolist():
            path = target/item.filename
            path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as output:
                output.write(archive.read(item))
    if manifest["engine"] == "postgresql":
        subprocess.run(["pg_restore","--exit-on-error","--no-owner","--no-acl","--dbname",make_url(database_url).database,str(target/"database")],
                       env=postgres_env(database_url),check=True,timeout=300,capture_output=True)
    settings = Settings(database_url=database_url or f"sqlite:///{target/'database'}",auto_migrate=False,embedded_worker=False,
                        source_storage_root=str(target/"sources"),secret_key_file=str(target/"account.key"))
    Path(settings.source_storage_root).mkdir(mode=0o700,exist_ok=True)
    db = Database(settings.database_url)
    try:
        with db.session() as session:
            session.execute(update(LocalSession).values(revoked=True))
            session.execute(update(Job).where(Job.status == "running").values(status="queued",lease_token=None,lease_until=None))
            session.commit()
        saved_ledger = Path(settings.source_storage_root)/"deletions"
        if saved_ledger.exists():
            apply_deletion_ledger(db,settings,saved_ledger)
        if deletion_ledger:
            apply_deletion_ledger(db,settings,deletion_ledger)
            destination = Path(settings.source_storage_root)/"deletions"
            destination.mkdir(mode=0o700,exist_ok=True)
            for path in Path(deletion_ledger).glob("*.enc"):
                shutil.copyfile(path,destination/path.name)
        if not verify_workspace(db,settings)["ok"]:
            raise ValueError("Restored source integrity failed; keep this workspace isolated.")
        (target/"restore-settings.json").write_text(json.dumps(asdict(settings),indent=2))
    finally:
        db.engine.dispose()
    return settings


def main():
    parser = argparse.ArgumentParser(description="Stopped-workspace backup and isolated restore")
    parser.add_argument("action",choices=["backup","restore","verify","retire"])
    parser.add_argument("--target")
    parser.add_argument("--backup")
    parser.add_argument("--backup-key")
    parser.add_argument("--deletion-ledger")
    parser.add_argument("--restore-database-url")
    parser.add_argument("--case-id")
    parser.add_argument("--reason")
    parser.add_argument("--services-stopped",action="store_true",required=True)
    args = parser.parse_args()
    if args.action == "restore":
        settings = restore_backup(args.backup,args.target,args.backup_key,deletion_ledger=args.deletion_ledger,database_url=args.restore_database_url)
        print(f"Restored into {Path(settings.source_storage_root).parent}; sessions revoked; configure this isolated workspace before launch.")
        return
    settings = Settings.from_env()
    db = Database(settings.database_url)
    try:
        if args.action == "backup":
            print(json.dumps(create_backup(db,settings,args.target,args.backup_key)))
        elif args.action == "verify":
            result = verify_workspace(db,settings)
            print(json.dumps(result))
            if not result["ok"]:
                raise SystemExit(1)
        else:
            retire_case(db,settings,args.case_id,args.reason)
    finally:
        db.engine.dispose()


if __name__ == "__main__":
    main()

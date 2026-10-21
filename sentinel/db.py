import time
import uuid
from pathlib import Path

from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def new_id():
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    roles: Mapped[list] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    totp_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    totp_last_step: Mapped[int] = mapped_column(Integer, default=-1)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class LocalSession(Base):
    __tablename__ = "local_sessions"
    token_digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    expires_at: Mapped[float] = mapped_column(Float)
    last_seen_at: Mapped[float] = mapped_column(Float, default=time.time)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class LoginThrottle(Base):
    __tablename__ = "login_throttles"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_start: Mapped[float] = mapped_column(Float)
    attempts: Mapped[int] = mapped_column(Integer, default=0)


class AccessEvent(Base):
    __tablename__ = "access_events"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class Claim(Base):
    __tablename__ = "claims"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    reference: Mapped[str] = mapped_column(String(200))
    patient_id: Mapped[str] = mapped_column(String(200), default="")
    sample_key: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    latest_job_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)
    facility_id: Mapped[str] = mapped_column(String(200), default="")
    encounter_ref: Mapped[str] = mapped_column(String(200), default="")
    revision: Mapped[int] = mapped_column(Integer, default=0)
    current_bundle_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    state: Mapped[str] = mapped_column(String(60), default="Received")
    created_at: Mapped[float] = mapped_column(Float, default=time.time, index=True)


class Job(Base):
    __tablename__ = "audit_jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), index=True)
    bundle_id: Mapped[str | None] = mapped_column(ForeignKey("bundles.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    use_model: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lease_until: Mapped[float | None] = mapped_column(Float, nullable=True)
    xml_name: Mapped[str] = mapped_column(String(200))
    xml_text: Mapped[str] = mapped_column(Text)
    chart_name: Mapped[str] = mapped_column(String(200), default="")
    chart_text: Mapped[str] = mapped_column(Text, default="")
    chart_blob: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    chart_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    xml_hash: Mapped[str] = mapped_column(String(64))
    chart_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    finished_at: Mapped[float | None] = mapped_column(Float, nullable=True)
    __table_args__ = (Index("ix_jobs_queue", "status", "lease_until", "created_at"),)


class Review(Base):
    __tablename__ = "reviews"
    job_id: Mapped[str] = mapped_column(ForeignKey("audit_jobs.id", ondelete="CASCADE"), primary_key=True)
    finding_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    decision: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[float] = mapped_column(Float, default=time.time)


class Bundle(Base):
    __tablename__ = "bundles"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    import_job_id: Mapped[str] = mapped_column(String(32))
    manifest: Mapped[dict] = mapped_column(JSON)
    manifest_hash: Mapped[str] = mapped_column(String(64))
    request_hash: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(100))
    profile_version: Mapped[str] = mapped_column(String(80), default="SAMPLE-ADULT-MEDICAL-1")
    created_by: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    status: Mapped[str] = mapped_column(String(30), default="quarantined")
    imported_revision: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("claim_id", "sequence"), UniqueConstraint("claim_id", "idempotency_key"))


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    bundle_id: Mapped[str] = mapped_column(ForeignKey("bundles.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    declared_type: Mapped[str] = mapped_column(String(40))
    filename: Mapped[str] = mapped_column(String(200))
    source_hash: Mapped[str] = mapped_column(String(64))
    object_key: Mapped[str] = mapped_column(String(32), unique=True)
    byte_count: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(80), default="application/octet-stream")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="quarantined")
    extraction: Mapped[dict] = mapped_column(JSON, default=dict)
    problems: Mapped[list] = mapped_column(JSON, default=list)
    __table_args__ = (UniqueConstraint("bundle_id", "position"),)


class ReviewEvent(Base):
    __tablename__ = "review_events"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), index=True)
    bundle_id: Mapped[str] = mapped_column(ForeignKey("bundles.id"))
    rule_version: Mapped[str] = mapped_column(String(80))
    revision: Mapped[int] = mapped_column(Integer)
    actor_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    actor_name: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    __table_args__ = (UniqueConstraint("claim_id", "revision"),)


class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), index=True)
    bundle_id: Mapped[str] = mapped_column(ForeignKey("bundles.id"))
    rule_version: Mapped[str] = mapped_column(String(80))
    revision: Mapped[int] = mapped_column(Integer)
    actor_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    __table_args__ = (UniqueConstraint("claim_id", "revision"),)


class Database:
    def __init__(self, url: str):
        if url.startswith("sqlite:///"):
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        options = {"connect_args": {"check_same_thread": False, "timeout": 20}} if url.startswith("sqlite") else {
            "pool_size": 5, "max_overflow": 5, "pool_pre_ping": True,
        }
        self.engine = create_engine(url, **options)
        if url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def configure(connection, _):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()
        self.session = sessionmaker(self.engine, expire_on_commit=False)

    def initialize(self):
        """Tests only. Running applications use Alembic migrations."""
        Base.metadata.create_all(self.engine)

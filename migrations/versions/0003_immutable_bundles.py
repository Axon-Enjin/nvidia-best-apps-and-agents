"""Add immutable bundle membership and private source references."""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    for name in ("facility_id", "encounter_ref"):
        op.add_column("claims", sa.Column(name, sa.String(200), nullable=False, server_default=""))
    op.add_column("claims", sa.Column("revision", sa.Integer, nullable=False, server_default="0"))
    op.add_column("claims", sa.Column("state", sa.String(60), nullable=False, server_default="Received"))
    op.add_column("claims", sa.Column("current_bundle_id", sa.String(32), nullable=True))
    op.create_table("bundles",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("claim_id", sa.String(32), sa.ForeignKey("claims.id"), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("import_job_id", sa.String(32), nullable=False),
        sa.Column("manifest", sa.JSON, nullable=False),
        sa.Column("manifest_hash", sa.String(64), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(100), nullable=False),
        sa.Column("profile_version", sa.String(80), nullable=False),
        sa.Column("created_by", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("created_at", sa.Float, nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("imported_revision", sa.Integer, nullable=False),
        sa.UniqueConstraint("claim_id", "sequence"), sa.UniqueConstraint("claim_id", "idempotency_key"))
    op.create_index("ix_bundles_claim_id", "bundles", ["claim_id"])
    op.create_table("documents",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("bundle_id", sa.String(32), sa.ForeignKey("bundles.id"), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("declared_type", sa.String(40), nullable=False),
        sa.Column("filename", sa.String(200), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("object_key", sa.String(32), nullable=False, unique=True),
        sa.Column("byte_count", sa.Integer, nullable=False),
        sa.Column("content_type", sa.String(80), nullable=False),
        sa.Column("page_count", sa.Integer, nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("extraction", sa.JSON, nullable=False),
        sa.Column("problems", sa.JSON, nullable=False), sa.UniqueConstraint("bundle_id", "position"))
    op.create_index("ix_documents_bundle_id", "documents", ["bundle_id"])
    if op.get_bind().dialect.name == "sqlite":
        op.execute("ALTER TABLE audit_jobs ADD COLUMN bundle_id VARCHAR(32) REFERENCES bundles(id)")
    else:
        op.add_column("audit_jobs", sa.Column("bundle_id", sa.String(32), sa.ForeignKey("bundles.id"), nullable=True))
    op.create_index("ix_audit_jobs_bundle_id", "audit_jobs", ["bundle_id"])


def downgrade():
    raise RuntimeError("Bundle rollback requires a coordinated backup; original evidence must be preserved.")

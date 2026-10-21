"""Initial shared-workspace claim, audit job and review schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("claims",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("reference", sa.String(200), nullable=False),
        sa.Column("patient_id", sa.String(200), nullable=False),
        sa.Column("sample_key", sa.String(80), unique=True, nullable=True),
        sa.Column("latest_job_id", sa.String(32), nullable=True),
        sa.Column("created_at", sa.Float, nullable=False))
    op.create_index("ix_claims_created_at", "claims", ["created_at"])
    op.create_table("audit_jobs",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("claim_id", sa.String(32), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("use_model", sa.Boolean, nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False),
        sa.Column("lease_token", sa.String(32), nullable=True),
        sa.Column("lease_until", sa.Float, nullable=True),
        sa.Column("xml_name", sa.String(200), nullable=False),
        sa.Column("xml_text", sa.Text, nullable=False),
        sa.Column("chart_name", sa.String(200), nullable=False),
        sa.Column("chart_text", sa.Text, nullable=False),
        sa.Column("chart_blob", sa.LargeBinary, nullable=True),
        sa.Column("chart_error", sa.Text, nullable=True),
        sa.Column("xml_hash", sa.String(64), nullable=False),
        sa.Column("chart_hash", sa.String(64), nullable=True),
        sa.Column("result", sa.JSON, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.Float, nullable=False),
        sa.Column("finished_at", sa.Float, nullable=True))
    op.create_index("ix_audit_jobs_claim_id", "audit_jobs", ["claim_id"])
    op.create_index("ix_jobs_queue", "audit_jobs", ["status", "lease_until", "created_at"])
    op.create_table("reviews",
        sa.Column("job_id", sa.String(32), sa.ForeignKey("audit_jobs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("finding_id", sa.String(100), primary_key=True),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("updated_at", sa.Float, nullable=False))


def downgrade():
    op.drop_table("reviews")
    op.drop_table("audit_jobs")
    op.drop_table("claims")

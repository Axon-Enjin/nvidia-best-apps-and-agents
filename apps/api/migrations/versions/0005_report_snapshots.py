"""Immutable, versioned internal review snapshots."""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("report_snapshots",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("claim_id", sa.String(32), sa.ForeignKey("claims.id"), nullable=False),
        sa.Column("bundle_id", sa.String(32), sa.ForeignKey("bundles.id"), nullable=False),
        sa.Column("rule_version", sa.String(80), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("actor_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("snapshot", sa.JSON, nullable=False),
        sa.Column("created_at", sa.Float, nullable=False),
        sa.UniqueConstraint("claim_id", "revision"))
    op.create_index("ix_report_snapshots_claim_id", "report_snapshots", ["claim_id"])


def downgrade():
    raise RuntimeError("Restore a coordinated backup to retain published review records.")

"""Append-only decisions and correction lifecycle events."""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("review_events",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("claim_id", sa.String(32), sa.ForeignKey("claims.id"), nullable=False),
        sa.Column("bundle_id", sa.String(32), sa.ForeignKey("bundles.id"), nullable=False),
        sa.Column("rule_version", sa.String(80), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("actor_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("actor_name", sa.String(80), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", sa.Float, nullable=False),
        sa.UniqueConstraint("claim_id", "revision"))
    op.create_index("ix_review_events_claim_id", "review_events", ["claim_id"])


def downgrade():
    raise RuntimeError("Restore a coordinated backup to preserve review history.")

"""Preserve original OCR candidates separately from confirmed source values."""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("extraction_confirmations",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("document_id", sa.String(32), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("actor_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("anchor", sa.JSON, nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("created_at", sa.Float, nullable=False))
    op.create_index("ix_extraction_confirmations_document_id", "extraction_confirmations", ["document_id"])


def downgrade():
    raise RuntimeError("Restore a coordinated backup to preserve source confirmation history.")

"""Reconcile retired case access after restoring older backups."""
import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("claims",sa.Column("deleted_at",sa.Float,nullable=True))


def downgrade():
    raise RuntimeError("Restore a coordinated backup and current retirement ledger.")

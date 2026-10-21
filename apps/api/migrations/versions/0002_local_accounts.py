"""Add named accounts without changing historical sources, jobs or reviews."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("accounts",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("roles", sa.JSON, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("totp_encrypted", sa.Text, nullable=True),
        sa.Column("totp_last_step", sa.Integer, nullable=False),
        sa.Column("created_at", sa.Float, nullable=False))
    op.create_table("local_sessions",
        sa.Column("token_digest", sa.String(64), primary_key=True),
        sa.Column("account_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("created_at", sa.Float, nullable=False),
        sa.Column("expires_at", sa.Float, nullable=False),
        sa.Column("last_seen_at", sa.Float, nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False))
    op.create_index("ix_local_sessions_account_id", "local_sessions", ["account_id"])
    op.create_table("login_throttles",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("window_start", sa.Float, nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False))
    op.create_table("access_events",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("actor_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("detail", sa.JSON, nullable=False),
        sa.Column("created_at", sa.Float, nullable=False))
    # Nullable for existing records: only a supervisor can assign legacy cases.
    # Alembic emits a separate ALTER CONSTRAINT for ForeignKey on add_column.
    # SQLite supports the same nullable reference inline without rebuilding history.
    if op.get_bind().dialect.name == "sqlite":
        op.execute("ALTER TABLE claims ADD COLUMN assignee_id VARCHAR(32) REFERENCES accounts(id)")
        op.execute("ALTER TABLE reviews ADD COLUMN actor_id VARCHAR(32) REFERENCES accounts(id)")
    else:
        op.add_column("claims", sa.Column("assignee_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=True))
        op.add_column("reviews", sa.Column("actor_id", sa.String(32), sa.ForeignKey("accounts.id"), nullable=True))
    op.create_index("ix_claims_assignee_id", "claims", ["assignee_id"])


def downgrade():
    raise RuntimeError("Account rollback requires a coordinated backup; this migration is additive only.")

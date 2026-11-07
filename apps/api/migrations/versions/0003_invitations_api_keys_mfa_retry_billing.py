"""invitations, API keys, MFA, run retries, billing fields

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-06 15:10:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return column in [c["name"] for c in insp.get_columns(table)]


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    if not _has_column("users", "totp_secret"):
        op.add_column("users", sa.Column("totp_secret", sa.String(length=64), nullable=True))
    if not _has_column("users", "totp_enabled"):
        op.add_column(
            "users",
            sa.Column("totp_enabled", sa.Boolean(), server_default=sa.false(), nullable=False),
        )
    if not _has_column("users", "recovery_codes"):
        op.add_column(
            "users",
            sa.Column(
                "recovery_codes",
                sa.JSON(),
                server_default=sa.text("'[]'"),
                nullable=False,
            ),
        )

    if not _has_column("organizations", "stripe_customer_id"):
        op.add_column(
            "organizations",
            sa.Column("stripe_customer_id", sa.String(length=80), nullable=True),
        )
    if not _has_column("organizations", "subscription_status"):
        op.add_column(
            "organizations",
            sa.Column(
                "subscription_status",
                sa.String(length=30),
                server_default="none",
                nullable=False,
            ),
        )
    if not _has_column("organizations", "plan_renewal_at"):
        op.add_column(
            "organizations",
            sa.Column("plan_renewal_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_column("runs", "attempts"):
        op.add_column(
            "runs",
            sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        )
    if not _has_column("runs", "max_attempts"):
        op.add_column(
            "runs",
            sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False),
        )
    if not _has_column("runs", "next_attempt_at"):
        op.add_column(
            "runs",
            sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("invitations"):
        op.create_table(
            "invitations",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("org_id", sa.String(length=36), nullable=False),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("invited_by", sa.String(length=36), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["invited_by"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_invitations_org_id", "invitations", ["org_id"], unique=False)
        op.create_index("ix_invitations_email", "invitations", ["email"], unique=False)
        op.create_index(
            "ix_invitations_token_hash", "invitations", ["token_hash"], unique=True
        )
        op.create_index(
            "ix_invitations_org_created", "invitations", ["org_id", "created_at"], unique=False
        )

    if not _has_table("api_keys"):
        op.create_table(
            "api_keys",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("org_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("prefix", sa.String(length=24), nullable=False),
            sa.Column("key_hash", sa.String(length=64), nullable=False),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_api_keys_org_id", "api_keys", ["org_id"], unique=False)
        op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)
        op.create_index(
            "ix_api_keys_org_created", "api_keys", ["org_id", "created_at"], unique=False
        )


def downgrade() -> None:
    op.drop_index("ix_api_keys_org_created", table_name="api_keys")
    op.drop_index("ix_api_keys_key_hash", table_name="api_keys")
    op.drop_index("ix_api_keys_org_id", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_invitations_org_created", table_name="invitations")
    op.drop_index("ix_invitations_token_hash", table_name="invitations")
    op.drop_index("ix_invitations_email", table_name="invitations")
    op.drop_index("ix_invitations_org_id", table_name="invitations")
    op.drop_table("invitations")

    with op.batch_alter_table("runs", schema=None) as batch_op:
        batch_op.drop_column("next_attempt_at")
        batch_op.drop_column("max_attempts")
        batch_op.drop_column("attempts")

    with op.batch_alter_table("organizations", schema=None) as batch_op:
        batch_op.drop_column("plan_renewal_at")
        batch_op.drop_column("subscription_status")
        batch_op.drop_column("stripe_customer_id")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("recovery_codes")
        batch_op.drop_column("totp_enabled")
        batch_op.drop_column("totp_secret")

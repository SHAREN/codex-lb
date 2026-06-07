"""add quota reserve settings

Revision ID: 20260606_000000_add_quota_reserve_settings
Revises: 20260523_000000_add_accounts_proxy_columns
Create Date: 2026-06-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

revision = "20260606_000000_add_quota_reserve_settings"
down_revision = "20260523_000000_add_accounts_proxy_columns"
branch_labels = None
depends_on = None


def _columns(connection: Connection, table_name: str) -> set[str]:
    inspector = sa.inspect(connection)
    if not inspector.has_table(table_name):
        return set()
    return {str(column["name"]) for column in inspector.get_columns(table_name) if column.get("name") is not None}


def _add_column_if_missing(
    connection: Connection,
    table_name: str,
    column_name: str,
    column: sa.Column,
) -> None:
    columns = _columns(connection, table_name)
    if not columns or column_name in columns:
        return
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(column)


def _drop_column_if_present(connection: Connection, table_name: str, column_name: str) -> None:
    columns = _columns(connection, table_name)
    if not columns or column_name not in columns:
        return
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.drop_column(column_name)


def upgrade() -> None:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("dashboard_settings"):
        return
    _add_column_if_missing(
        bind,
        "dashboard_settings",
        "quota_reserve_enabled",
        sa.Column("quota_reserve_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    _add_column_if_missing(
        bind,
        "dashboard_settings",
        "quota_reserve_primary_percent",
        sa.Column("quota_reserve_primary_percent", sa.Float(), nullable=False, server_default=sa.text("0.0")),
    )
    _add_column_if_missing(
        bind,
        "dashboard_settings",
        "quota_reserve_secondary_percent",
        sa.Column("quota_reserve_secondary_percent", sa.Float(), nullable=False, server_default=sa.text("0.0")),
    )


def downgrade() -> None:
    bind = op.get_bind()
    _drop_column_if_present(bind, "dashboard_settings", "quota_reserve_secondary_percent")
    _drop_column_if_present(bind, "dashboard_settings", "quota_reserve_primary_percent")
    _drop_column_if_present(bind, "dashboard_settings", "quota_reserve_enabled")

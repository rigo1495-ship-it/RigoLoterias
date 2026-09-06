"""add Protouch official contest results

Revision ID: 20260906_06
Revises: 20260906_05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_06"
down_revision: str | None = "20260906_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "protouch_contest_results" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "protouch_contest_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contest_number", sa.String(128), nullable=False),
        sa.Column("contest_date", sa.Date(), nullable=False),
        sa.Column("outcomes_json", sa.JSON(), nullable=False),
        sa.Column("prize_pool_mxn", sa.Integer(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("parser_version", sa.String(64), nullable=False),
        sa.Column("rule_version", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_protouch_contest_results_contest_number",
        "protouch_contest_results",
        ["contest_number"],
        unique=True,
    )
    op.create_index(
        "ix_protouch_contest_results_contest_date", "protouch_contest_results", ["contest_date"]
    )
    op.create_index(
        "ix_protouch_contest_results_source_hash", "protouch_contest_results", ["source_hash"]
    )


def downgrade() -> None:
    op.drop_table("protouch_contest_results")

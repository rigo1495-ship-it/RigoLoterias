"""add pool contest results

Revision ID: 20260906_05
Revises: 20260906_04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_05"
down_revision: str | None = "20260906_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "pool_contest_results" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "pool_contest_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_slug", sa.String(64), nullable=False),
        sa.Column("contest_number", sa.String(128), nullable=False),
        sa.Column("contest_date", sa.Date(), nullable=False),
        sa.Column("outcomes_json", sa.JSON(), nullable=False),
        sa.Column("revancha_outcomes_json", sa.JSON(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("parser_version", sa.String(64), nullable=False),
        sa.Column("rule_version", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "uq_pool_game_contest", "pool_contest_results", ["game_slug", "contest_number"], unique=True
    )
    op.create_index("ix_pool_contest_results_game_slug", "pool_contest_results", ["game_slug"])
    op.create_index(
        "ix_pool_contest_results_contest_date", "pool_contest_results", ["contest_date"]
    )
    op.create_index("ix_pool_contest_results_source_hash", "pool_contest_results", ["source_hash"])


def downgrade() -> None:
    op.drop_table("pool_contest_results")

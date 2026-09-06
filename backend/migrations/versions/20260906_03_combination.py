"""add combination draw results

Revision ID: 20260906_03
Revises: 20260906_02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_03"
down_revision: str | None = "20260906_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "combination_draw_results" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "combination_draw_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_slug", sa.String(64), nullable=False),
        sa.Column("draw_number", sa.String(128), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("natural_numbers_json", sa.JSON(), nullable=False),
        sa.Column("additional_numbers_json", sa.JSON(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("parser_version", sa.String(64), nullable=False),
        sa.Column("rule_version", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "uq_combination_game_draw",
        "combination_draw_results",
        ["game_slug", "draw_number"],
        unique=True,
    )
    op.create_index(
        "ix_combination_draw_results_game_slug",
        "combination_draw_results",
        ["game_slug"],
    )
    op.create_index(
        "ix_combination_draw_results_draw_date",
        "combination_draw_results",
        ["draw_date"],
    )
    op.create_index(
        "ix_combination_draw_results_source_hash",
        "combination_draw_results",
        ["source_hash"],
    )


def downgrade() -> None:
    op.drop_table("combination_draw_results")

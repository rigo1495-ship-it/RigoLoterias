"""add TRIS draw results

Revision ID: 20260906_02
Revises: 20260906_01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_02"
down_revision: str | None = "20260906_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "tris_draw_results" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "tris_draw_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("draw_number", sa.String(128), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("draw_time", sa.String(16)),
        sa.Column("draw_name", sa.String(128), nullable=False),
        sa.Column("winning_number", sa.String(5), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(winning_number) = 5", name="ck_tris_winning_number_length"
        ),
        sa.UniqueConstraint("draw_number"),
    )
    op.create_index(
        "ix_tris_draw_results_draw_number",
        "tris_draw_results",
        ["draw_number"],
        unique=True,
    )
    op.create_index(
        "ix_tris_draw_results_draw_date", "tris_draw_results", ["draw_date"]
    )


def downgrade() -> None:
    if "tris_draw_results" not in sa.inspect(op.get_bind()).get_table_names():
        return
    op.drop_index("ix_tris_draw_results_draw_date", table_name="tris_draw_results")
    op.drop_index("ix_tris_draw_results_draw_number", table_name="tris_draw_results")
    op.drop_table("tris_draw_results")

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


class Game(Base, TimestampMixin):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    capabilities_json: Mapped[list[str]] = mapped_column(JSON, default=list)


class GameRuleVersion(Base, TimestampMixin):
    __tablename__ = "game_rule_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    version: Mapped[str] = mapped_column(String(64))
    rules_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    source: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("uq_game_rule_version", "game_id", "version", unique=True),)


class Draw(Base, TimestampMixin):
    __tablename__ = "draws"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    draw_number: Mapped[str] = mapped_column(String(128))
    draw_date: Mapped[date | None] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), default="imported")
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    source: Mapped[str | None] = mapped_column(Text)
    source_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    __table_args__ = (
        Index("uq_draw_game_number", "game_id", "draw_number", unique=True),
        Index("ix_draw_game_date", "game_id", "draw_date"),
    )


class HistoricalImport(Base, TimestampMixin):
    __tablename__ = "historical_imports"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_hash: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32))
    rows_total: Mapped[int] = mapped_column(Integer, default=0)
    rows_accepted: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)


class ImportRowError(Base, TimestampMixin):
    __tablename__ = "import_row_errors"
    id: Mapped[int] = mapped_column(primary_key=True)
    import_id: Mapped[int] = mapped_column(
        ForeignKey("historical_imports.id"), index=True
    )
    row_number: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class JsonRunMixin(TimestampMixin):
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    strategy: Mapped[str] = mapped_column(String(128))
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class AnalysisRun(Base, JsonRunMixin):
    __tablename__ = "analysis_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    draw_id: Mapped[int | None] = mapped_column(ForeignKey("draws.id"))
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    random_seed: Mapped[int | None] = mapped_column(Integer)


class StrategyDefinition(Base, TimestampMixin):
    __tablename__ = "strategy_definitions"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class BacktestRun(Base, JsonRunMixin):
    __tablename__ = "backtest_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    random_seed: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class BacktestStep(Base, TimestampMixin):
    __tablename__ = "backtest_steps"
    id: Mapped[int] = mapped_column(primary_key=True)
    backtest_run_id: Mapped[int] = mapped_column(
        ForeignKey("backtest_runs.id"), index=True
    )
    target_draw_id: Mapped[int] = mapped_column(ForeignKey("draws.id"))
    history_end_draw_id: Mapped[int | None] = mapped_column(ForeignKey("draws.id"))
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class GeneratedPortfolio(Base, TimestampMixin):
    __tablename__ = "generated_portfolios"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    analysis_run_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_runs.id"))
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    random_seed: Mapped[int | None] = mapped_column(Integer)


class GeneratedTicket(Base, TimestampMixin):
    __tablename__ = "generated_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("generated_portfolios.id"), index=True
    )
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    heuristic_score: Mapped[float | None] = mapped_column(Float)
    model_score: Mapped[float | None] = mapped_column(Float)
    relative_rank: Mapped[int | None] = mapped_column(Integer)


class SimulationRun(Base, JsonRunMixin):
    __tablename__ = "simulation_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    random_seed: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class PrizeRuleVersion(Base, TimestampMixin):
    __tablename__ = "prize_rule_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), index=True)
    version: Mapped[str] = mapped_column(String(64))
    prizes_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(Text)


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    action: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class TrisDrawResultModel(Base, TimestampMixin):
    __tablename__ = "tris_draw_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    draw_number: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    draw_date: Mapped[date] = mapped_column(Date, index=True)
    draw_time: Mapped[str | None] = mapped_column(String(16))
    draw_name: Mapped[str] = mapped_column(String(128), default="Sin horario")
    winning_number: Mapped[str] = mapped_column(String(5))
    source: Mapped[str] = mapped_column(Text, default="manual")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (
        CheckConstraint(
            "length(winning_number) = 5", name="ck_tris_winning_number_length"
        ),
    )


class CombinationDrawResultModel(Base, TimestampMixin):
    __tablename__ = "combination_draw_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_slug: Mapped[str] = mapped_column(String(64), index=True)
    draw_number: Mapped[str] = mapped_column(String(128))
    draw_date: Mapped[date] = mapped_column(Date, index=True)
    natural_numbers_json: Mapped[list[int]] = mapped_column(JSON)
    additional_numbers_json: Mapped[list[int]] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(Text)
    source_hash: Mapped[str] = mapped_column(String(64), index=True)
    parser_version: Mapped[str] = mapped_column(String(64))
    rule_version: Mapped[str] = mapped_column(String(64))
    __table_args__ = (
        Index("uq_combination_game_draw", "game_slug", "draw_number", unique=True),
    )

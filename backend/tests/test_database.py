from sqlalchemy import inspect

from app.db import (
    models,  # noqa: F401
    session,
)
from app.db.base import Base
from app.db.session import build_engine


def test_database_initialization() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {
        "games",
        "draws",
        "analysis_runs",
        "backtest_runs",
        "generated_tickets",
    } <= tables


def test_build_engine_uses_psycopg_for_plain_postgresql_url(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def capture_url(url: str, **_kwargs: object) -> object:
        captured["url"] = url
        return object()

    monkeypatch.setattr(session, "create_engine", capture_url)
    build_engine("postgresql://user:password@example.test:5432/rigoloterias")

    assert captured["url"].startswith("postgresql+psycopg://")

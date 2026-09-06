from sqlalchemy import inspect

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import build_engine


def test_database_initialization() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"games", "draws", "analysis_runs", "backtest_runs", "generated_tickets"} <= tables
